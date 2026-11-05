-- Optional database-only SQL, run as an authenticated MySQL administrator.
-- Prefer scripts/setup-mysql.ps1 for secure app-user provisioning and startup.
SELECT SCHEMA_NAME AS existing_database
FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = 'library_db';
CREATE DATABASE IF NOT EXISTS library_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
SHOW DATABASES LIKE 'library_db';
