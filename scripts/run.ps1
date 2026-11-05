$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\use-java21.ps1"
if (-not $env:JAVA_HOME -or -not (Test-Path "$env:JAVA_HOME\bin\java.exe")) {
    throw 'Set JAVA_HOME to your JDK 21 installation.'
}
$previousPreference = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
$javaVersion = & "$env:JAVA_HOME\bin\java.exe" -version 2>&1 | Out-String
$ErrorActionPreference = $previousPreference
if ($javaVersion -notmatch 'version "21[.\"]') { throw 'This lab requires JDK 21. Set JAVA_HOME to JDK 21.' }
if (-not $env:DB_USERNAME) { $env:DB_USERNAME = 'library_app' }
if (-not $env:DB_PASSWORD -and (Test-Path "$PSScriptRoot\..\.local\mysql.credential.xml")) {
    $credential = Import-Clixml "$PSScriptRoot\..\.local\mysql.credential.xml"
    $env:DB_USERNAME = $credential.UserName
    $env:DB_PASSWORD = $credential.GetNetworkCredential().Password
}
if (-not $env:DB_PASSWORD) {
    $secret = Read-Host 'MySQL library_app password' -AsSecureString
    $env:DB_PASSWORD = [System.Net.NetworkCredential]::new('', $secret).Password
}
try {
    Push-Location (Split-Path $PSScriptRoot -Parent)
    & mvn spring-boot:run
    if ($LASTEXITCODE -ne 0) { throw "Application exited with code $LASTEXITCODE" }
} finally {
    Pop-Location
    Remove-Item Env:DB_PASSWORD -ErrorAction SilentlyContinue
}
