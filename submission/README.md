# IN3101 Lab 02 submission

The report uses your actual evidence only. No screenshots were found during preparation.
Place one real PNG or JPG in each folder `screenshots/S1/` through `screenshots/S8/`.
For example: `screenshots/S1/S1.png`. Do not include passwords, tokens or unrelated
personal information in screenshots.

| Case | Capture |
|---|---|
| S1 | POST create: body, 201 response, generated ID |
| S2 | GET all: 200 and exactly three books including `[235089A] - Clean Code` |
| S3 | GET created ID: 200 and book |
| S4 | PUT: updated request and 200 response |
| S5 | DELETE same ID: 204 and empty body |
| S6 | GET deleted ID: 404 |
| S7 | POST with only an empty title: 400 and title error |
| S8 | Swagger UI expanded POST /api/books: documented 201 and 400 responses |

The current API contains two supporting books. Skip the Postman Preparation folder
and run S1-S8 in order. S1 creates your third, index-number book. Capture S2 before
continuing to S5, which deletes it. Check the database count first if you have
already repeated requests; do not delete existing work automatically.

Update `details.json` with your confirmed student name and actual public repository
URL. Generate the editable Word report and printable HTML from the project root:

```powershell
python scripts/build_submission.py
```

Missing evidence appears as a clearly marked placeholder. When all eight images,
the name and repository URL are supplied, generate `235089A_IN3101_Lab02.pdf`:

```powershell
python scripts/build_submission.py --pdf
```

PDF generation uses installed Edge or Chrome. Alternatively open the generated HTML
in a browser, press Ctrl+P, choose Save as PDF, A4 and background graphics, and save
as `235089A_IN3101_Lab02.pdf`. Do not submit a report with placeholders.

Before LMS upload, check the PDF cover, repository link, eight screenshots and
legibility. Ensure the public repository is accessible while signed out. Upload
the final PDF to the IN3101 Lab 02 assignment and enter the GitHub URL if LMS asks
for a link. Complete the final Submit/Confirm action and retain its receipt.
Follow any additional naming or upload instructions shown by your lecturer/LMS.
