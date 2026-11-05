param([string]$BaseUrl = 'http://localhost:8080')
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Net.Http
$client = [System.Net.Http.HttpClient]::new()
$results = [System.Collections.Generic.List[object]]::new()
function Send-Request($method, $path, $body = $null) {
    $request = [System.Net.Http.HttpRequestMessage]::new([System.Net.Http.HttpMethod]::new($method), "$BaseUrl$path")
    if ($null -ne $body) {
        $request.Content = [System.Net.Http.StringContent]::new(($body | ConvertTo-Json -Compress), [System.Text.Encoding]::UTF8, 'application/json')
    }
    try {
        $response = $client.SendAsync($request).GetAwaiter().GetResult()
        try {
            return [pscustomobject]@{ Status = [int]$response.StatusCode; Body = $response.Content.ReadAsStringAsync().GetAwaiter().GetResult() }
        } finally { $response.Dispose() }
    } finally { $request.Dispose() }
}
function Check($name, $response, $expected) {
    $results.Add([pscustomobject]@{ Case=$name; Expected=$expected; Actual=$response.Status; Body=$response.Body })
    if ($response.Status -ne $expected) { throw "$name expected $expected but received $($response.Status)" }
    Write-Host "$name HTTP $expected"
}
$createdId = $null
try {
    $before = Send-Request GET '/api/books'
    $beforeBooks = $before.Body | ConvertFrom-Json
    if ($before.Status -ne 200 -or @($beforeBooks).Count -ne 2) {
        throw 'This verification needs exactly two supporting books. It never deletes existing data to prepare the database.'
    }
    $isbn = '978' + [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds().ToString().Substring(3)
    $book = @{title='[235089A] - Clean Code'; author='Robert C. Martin'; isbn=$isbn; publishedYear=2008}
    $created = Send-Request POST '/api/books' $book
    Check S1 $created 201
    $createdId = ($created.Body | ConvertFrom-Json).id
    $listed = Send-Request GET '/api/books'
    Check S2 $listed 200
    $books = $listed.Body | ConvertFrom-Json
    if (@($books).Count -ne 3 -or -not ($books | Where-Object { $_.title -eq '[235089A] - Clean Code' -and $_.id -eq $createdId })) {
        throw 'S2 requires exactly three books including the newly created index-number book.'
    }
    Check S3 (Send-Request GET "/api/books/$createdId") 200
    $book.title = '[235089A] - Clean Code (Updated)'
    $updated = Send-Request PUT "/api/books/$createdId" $book
    Check S4 $updated 200
    if (($updated.Body | ConvertFrom-Json).title -ne $book.title) { throw 'S4 did not update the title' }
    $deletedId = $createdId
    $deleted = Send-Request DELETE "/api/books/$deletedId"
    Check S5 $deleted 204
    if ($deleted.Body) { throw 'S5 response must be empty' }
    $createdId = $null
    Check S6 (Send-Request GET "/api/books/$deletedId") 404
    $book.title = ''
    $invalid = Send-Request POST '/api/books' $book
    Check S7 $invalid 400
    if (-not (($invalid.Body | ConvertFrom-Json).errors | Where-Object { $_ -like 'title:*' })) { throw 'S7 requires a title validation error' }
    $docs = Send-Request GET '/v3/api-docs'
    Check S8 $docs 200
    $responses = ($docs.Body | ConvertFrom-Json).paths.'/api/books'.post.responses
    if (-not $responses.'201' -or -not $responses.'400') { throw 'S8 must document POST 201 and 400' }
    Write-Host 'S8: POST 201 and 400 documented. Capture Swagger UI manually for the screenshot.'
} finally {
    # Only clean up the book created by this run if a later assertion failed.
    if ($null -ne $createdId) { Send-Request DELETE "/api/books/$createdId" | Out-Null }
    $client.Dispose()
    $evidenceDirectory = Join-Path (Split-Path $PSScriptRoot -Parent) 'target'
    New-Item -ItemType Directory -Path $evidenceDirectory -Force | Out-Null
    $results | ConvertTo-Json -Depth 8 | Set-Content (Join-Path $evidenceDirectory 'mysql-verification.json') -Encoding UTF8
}
