"""Build an editable DOCX and print-ready HTML from actual submission evidence.

Standard library only. PDF export additionally requires installed Edge or Chrome.
Run from any directory: python scripts/build_submission.py [--pdf]
"""
from pathlib import Path
from html import escape
from xml.sax.saxutils import escape as xml_escape
from zipfile import ZipFile, ZIP_DEFLATED
import argparse
import base64
import json
import os
import shutil
import subprocess
import tempfile
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'submission'
HEADINGS = [
    'S1 - Postman - Create a Book',
    'S2 - Postman - List All Books',
    'S3 - Postman - Get One Book',
    'S4 - Postman - Update a Book',
    'S5 - Postman - Delete a Book',
    'S6 - Postman - Deleted Book (404)',
    'S7 - Postman - Validation (400)',
    'S8 - Swagger UI - Documented Endpoint',
]
CAPTIONS = [
    'POST /api/books: HTTP 201; [235089A] - Clean Code by Robert C. Martin.',
    'GET /api/books: HTTP 200; exactly three books including the index-number book.',
    'GET /api/books/{id}: HTTP 200 for the book created in S1.',
    'PUT /api/books/{id}: HTTP 200 with the updated book.',
    'DELETE /api/books/{id}: HTTP 204 and an empty response body.',
    'GET the deleted ID: HTTP 404.',
    'POST with an empty title and otherwise valid fields: HTTP 400 and a title error.',
    'Swagger UI: expanded POST /api/books documents HTTP 201 and 400.',
]


def paragraph(text, style=None):
    props = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ''
    return f'<w:p>{props}<w:r><w:t xml:space="preserve">{xml_escape(text)}</w:t></w:r></w:p>'


def image_size(data, suffix):
    if suffix == '.png':
        return int.from_bytes(data[16:20], 'big'), int.from_bytes(data[20:24], 'big')
    # JPEG start-of-frame markers carry the original dimensions.
    offset = 2
    while offset < len(data):
        if data[offset] != 255:
            offset += 1
            continue
        while data[offset] == 255:
            offset += 1
        marker = data[offset]
        offset += 1
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            continue
        length = int.from_bytes(data[offset:offset + 2], 'big')
        if marker in (0xC0, 0xC1, 0xC2):
            return int.from_bytes(data[offset + 5:offset + 7], 'big'), int.from_bytes(data[offset + 3:offset + 5], 'big')
        offset += length
    raise ValueError('Unsupported JPEG; save it as PNG instead.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdf', action='store_true')
    args = parser.parse_args()
    details = json.loads((OUT / 'details.json').read_text(encoding='utf-8-sig'))
    name, index, repo = (details[k] for k in ('studentName', 'indexNumber', 'repositoryUrl'))
    if not index.isalnum():
        raise SystemExit('Index number must be alphanumeric.')
    screenshots = []
    for number in range(1, 9):
        folder = OUT / 'screenshots' / f'S{number}'
        folder.mkdir(parents=True, exist_ok=True)
        (folder / '.gitkeep').touch()
        files = sorted(p for p in folder.iterdir() if p.suffix.lower() in ('.png', '.jpg', '.jpeg'))
        if len(files) > 1:
            raise SystemExit(f'Keep exactly one screenshot in {folder}.')
        screenshots.append(files[0] if files else None)
    missing = [f'S{i}' for i, file in enumerate(screenshots, 1) if file is None]
    parsed = urlparse(repo)
    complete = not missing and 'PENDING' not in name and parsed.scheme == 'https' and parsed.hostname == 'github.com' and len(parsed.path.strip('/').split('/')) == 2
    label = 'Submission evidence' if complete else 'DRAFT - missing information or screenshot evidence'
    html = ['<!doctype html><html lang="en"><meta charset="utf-8"><title>IN3101 Lab 02</title><style>',
            '@page{size:A4;margin:18mm}body{font:11pt Arial,sans-serif;color:#18283c;margin:0}section{break-after:page;min-height:245mm;box-sizing:border-box}section:last-child{break-after:auto}.cover{padding-top:35mm}h1{font-size:30pt;color:#143a5a}h2{font-size:19pt;border-bottom:3px solid #268b98;padding-bottom:10px}p{line-height:1.5}.label{color:#617183;font-size:10pt;text-transform:uppercase;letter-spacing:1px}.placeholder{border:2px dashed #9aa8b6;padding:35mm 8mm;margin-top:12mm;text-align:center;color:#596979}img{display:block;max-width:100%;max-height:190mm;margin:10mm auto;object-fit:contain}a{color:#164e80;overflow-wrap:anywhere}@media screen{body{max-width:180mm;margin:20px auto;background:#edf1f5}section{background:white;padding:15mm;margin-bottom:20px}}',
            '</style><body><section class="cover"><p class="label">IN3101 · Lab 02</p><h1>Library REST API</h1><p>Spring Boot · Java 21 · MySQL</p>',
            f'<p><strong>Student name</strong><br>{escape(name)}</p><p><strong>Index number</strong><br>{escape(index)}</p>',
            f'<p><strong>GitHub repository</strong><br><a href="{escape(repo, quote=True)}">{escape(repo)}</a></p><p>{escape(label)}</p></section>']
    word = [paragraph('IN3101 | LAB 02', 'Subtitle'), paragraph('Library REST API', 'Title'),
            paragraph('Spring Boot | Java 21 | MySQL', 'Subtitle'), paragraph('Student name: ' + name),
            paragraph('Index number: ' + index), paragraph('GitHub repository: ' + repo), paragraph(label)]
    rels = ['<Relationship Id="styles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>']
    images = []
    for number, (heading, caption, file) in enumerate(zip(HEADINGS, CAPTIONS, screenshots), 1):
        word += ['<w:p><w:r><w:br w:type="page"/></w:r></w:p>', paragraph(heading, 'Heading1'), paragraph(caption)]
        html += [f'<section><h2>{escape(heading)}</h2><p>{escape(caption)}</p>']
        if file:
            data = file.read_bytes()
            suffix = file.suffix.lower()
            width, height = image_size(data, suffix)
            scale = min(6.5 * 914400 / width, 7.2 * 914400 / height)
            cx, cy = int(width * scale), int(height * scale)
            media = f'image{number}{suffix}'
            images.append((media, data))
            rels.append(f'<Relationship Id="img{number}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/{media}"/>')
            word.append(f'<w:p><w:r><w:drawing><wp:inline><wp:extent cx="{cx}" cy="{cy}"/><wp:docPr id="{number}" name="S{number}"/><a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic><pic:nvPicPr><pic:cNvPr id="{number}" name="S{number}"/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip r:embed="img{number}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>')
            mime = 'image/png' if suffix == '.png' else 'image/jpeg'
            html.append(f'<img alt="Actual screenshot S{number}" src="data:{mime};base64,{base64.b64encode(data).decode()}">')
        else:
            placeholder = f'PLACEHOLDER - Insert your actual S{number} screenshot. No screenshot has been supplied or captured.'
            word.append(paragraph(placeholder))
            html.append(f'<div class="placeholder">{escape(placeholder)}</div>')
        html.append('</section>')
    html.append('</body></html>')
    html_path = OUT / f'{index}_IN3101_Lab02.html'
    html_path.write_text('\n'.join(html), encoding='utf-8')
    namespaces = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"'
    with ZipFile(OUT / f'{index}_IN3101_Lab02.docx', 'w', ZIP_DEFLATED) as archive:
        archive.writestr('[Content_Types].xml', '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Default Extension="png" ContentType="image/png"/><Default Extension="jpg" ContentType="image/jpeg"/><Default Extension="jpeg" ContentType="image/jpeg"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>')
        archive.writestr('_rels/.rels', '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="document" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
        archive.writestr('word/_rels/document.xml.rels', '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + ''.join(rels) + '</Relationships>')
        archive.writestr('word/document.xml', f'<?xml version="1.0" encoding="UTF-8"?><w:document {namespaces}><w:body>' + ''.join(word) + '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1020" w:right="1020" w:bottom="1020" w:left="1020"/></w:sectPr></w:body></w:document>')
        archive.writestr('word/styles.xml', '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="22"/></w:rPr></w:rPrDefault></w:docDefaults>' + ''.join(f'<w:style w:type="paragraph" w:styleId="{style}"><w:name w:val="{style}"/><w:pPr><w:spacing w:before="240" w:after="200"/></w:pPr><w:rPr><w:color w:val="143A5A"/><w:sz w:val="{size}"/><w:b/></w:rPr></w:style>' for style, size in [('Title', 60), ('Subtitle', 28), ('Heading1', 36)]) + '</w:styles>')
        for media, data in images:
            archive.writestr('word/media/' + media, data)
    print(f'Created DOCX and HTML in {OUT}. Missing screenshots: {", ".join(missing) or "none"}.')
    if args.pdf:
        if not complete:
            raise SystemExit('Final PDF blocked: supply student name, actual GitHub URL and all eight screenshots in submission/details.json and submission/screenshots/.')
        browser = next((p for p in [shutil.which('msedge'), shutil.which('chrome'), str(Path(os.environ.get('PROGRAMFILES(X86)', '')) / 'Microsoft/Edge/Application/msedge.exe'), str(Path(os.environ.get('PROGRAMFILES', '')) / 'Google/Chrome/Application/chrome.exe')] if p and Path(p).is_file()), None)
        if not browser:
            raise SystemExit('No supported browser found. Open the HTML and print to PDF manually.')
        local = ROOT / '.local'
        local.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='submission-browser-', dir=local) as profile:
            pdf = OUT / f'{index}_IN3101_Lab02.pdf'
            subprocess.run([browser, '--headless', '--disable-gpu', '--no-pdf-header-footer', '--allow-file-access-from-files', f'--user-data-dir={profile}', f'--print-to-pdf={pdf}', html_path.as_uri()], check=True, timeout=90, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if not pdf.is_file():
                raise SystemExit('Browser did not create the PDF; print the HTML manually.')
            print(f'Created {pdf}')


if __name__ == '__main__':
    main()
