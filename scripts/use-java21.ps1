$candidates = @(
    "$env:ProgramFiles\Eclipse Adoptium",
    "$env:ProgramFiles\Java",
    "$env:ProgramFiles\Microsoft",
    "$env:USERPROFILE\.jdks"
)
$jdk = $candidates | Where-Object { Test-Path $_ } | ForEach-Object {
    Get-ChildItem -LiteralPath $_ -Directory | Where-Object { $_.Name -match '(jdk-?21|jdk.*-21|openjdk-21)' }
} | Where-Object { Test-Path (Join-Path $_.FullName 'bin\javac.exe') } | Select-Object -First 1
if (-not $jdk) { throw 'JDK 21 not found. Install it using winget install --id EclipseAdoptium.Temurin.21.JDK --exact --source winget' }
$env:JAVA_HOME = $jdk.FullName
$env:Path = "$env:JAVA_HOME\bin;$env:Path"
Write-Host "Project JAVA_HOME: $env:JAVA_HOME"
