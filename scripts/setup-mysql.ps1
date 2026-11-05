# Run this yourself in a local PowerShell terminal. mysql prompts for root's
# password directly; the script never reads or stores that password.
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\use-java21.ps1"
$mysql = Get-ChildItem "$env:ProgramFiles\MySQL\MySQL Server*\bin\mysql.exe" |
    Sort-Object FullName | Select-Object -First 1 -ExpandProperty FullName
if (-not $mysql) { throw 'MySQL command line client not found.' }
$bytes = New-Object byte[] 32
$rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
$rng.GetBytes($bytes)
$rng.Dispose()
$appPassword = [Convert]::ToBase64String($bytes)
# SQL is passed through stdin, not in process arguments or a file.
# CREATE USER deliberately fails if the account exists; existing credentials are
# never reset automatically. The database create itself is idempotent.
$sql = @"
SELECT SCHEMA_NAME AS existing_database FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = 'library_db';
CREATE DATABASE IF NOT EXISTS library_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'library_app'@'localhost' IDENTIFIED BY '$appPassword';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE ON library_db.* TO 'library_app'@'localhost';
SHOW DATABASES LIKE 'library_db';
"@
Write-Host 'Enter your MySQL root password at the mysql password prompt (not in chat).'
$sql | & $mysql --host=localhost --port=3306 --user=root --password --batch
if ($LASTEXITCODE -ne 0) {
    $appPassword = $null
    throw 'Setup failed. If library_app already exists, run scripts/run.ps1 and enter its existing password; do not reset it automatically. Otherwise inspect the MySQL error above.'
}
$env:DB_USERNAME = 'library_app'
$env:DB_PASSWORD = $appPassword
$localDirectory = Join-Path (Split-Path $PSScriptRoot -Parent) '.local'
New-Item -ItemType Directory -Path $localDirectory -Force | Out-Null
$credential = [System.Management.Automation.PSCredential]::new('library_app', (ConvertTo-SecureString $appPassword -AsPlainText -Force))
# Windows Export-Clixml protects the password using DPAPI for this Windows user.
# The entire directory is Git-ignored; root's password is never saved.
$credential | Export-Clixml (Join-Path $localDirectory 'mysql.credential.xml')
$appPassword = $null
Write-Host 'Database and app user created. App credentials saved with Windows user encryption in Git-ignored .local. Root password was not saved.'
Write-Host 'After startup, verify in another terminal: Invoke-RestMethod http://localhost:8080/api/books'
& "$PSScriptRoot\run.ps1"
