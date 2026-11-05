# Observed setup and verification — 5 November 2026

| Item | Verified result |
|---|---|
| Project | Existing project at `C:\labs\library-api`; no nested project |
| Java 21 | Temurin 21.0.13+9 at `C:\Program Files\Eclipse Adoptium\jdk-21.0.13.9-hotspot` |
| Winget | Package `EclipseAdoptium.Temurin.21.JDK` found. Initial automated installer returned cancellation code 1602; subsequent inspection confirmed the installed JDK and successful execution. |
| Project JAVA_HOME | `scripts/use-java21.ps1` selects JDK 21 and prepends its bin directory to the current process PATH; run/setup scripts invoke it automatically. Global Java settings are unchanged. |
| Maven | 3.9.11; verified running on Java 21 |
| Build | `mvn -B clean verify` completed with exit 0 and BUILD SUCCESS on Java 21 |
| Automated integration test | 1 test, zero failures/errors/skips; H2 is isolated to tests |
| MySQL | Direct authenticated query confirmed MySQL 9.5.0, database `library_db`, account `library_app@localhost` |
| Database provisioning | Database already existed when inspected; no database recreation or deletion was needed |
| App credentials | Windows-user-encrypted credential exists in Git-ignored `.local/mysql.credential.xml`; no root password was requested in chat or committed |
| Running application | Final JAR started on Java 21 with an explicit MySQL JDBC URL, database `library_db`; background process ID at verification: 5420 |
| GET /api/books | HTTP 200 from http://localhost:8080/api/books |
| Swagger | UI resource responds; OpenAPI POST declares 201, 400 and 409; error responses use ProblemDetail schemas |

## Real MySQL API verification

`scripts/verify-lab.ps1` completed successfully against the running application:

| Official case | Observed result |
|---|---|
| S1 POST create | 201, title `[235089A] - Clean Code`, author Robert C. Martin |
| S2 GET all | 200, exactly three books, including the newly created index-number book |
| S3 GET by ID | 200 |
| S4 PUT update | 200; updated title verified |
| S5 DELETE | 204 with empty body |
| S6 GET deleted ID | 404 |
| S7 POST empty title | 400 with a title validation error; other fields valid |
| S8 Swagger POST documentation | OpenAPI fetched with 200; POST response codes 201 and 400 verified |

These were real HTTP checks against MySQL, not a Postman execution or fabricated
screenshots. Evidence includes response bodies in `target/mysql-verification.json`,
build output in `java21-verify.log`, test reports in `target/surefire-reports/`,
and running application logs in `target/application.log`.

The smoke test created and then deleted its own book according to S1–S6.
The two original supporting books remain: The Pragmatic Programmer and Introduction
to Java. **Skip the collection's Preparation folder and run S1–S8 directly.**
S1 creates the third book. For S8, manually open Swagger UI, expand POST /api/books,
and capture the Responses section showing 201 and 400.

## Password entry and later restarts

For a future fresh database, run `scripts/setup-mysql.ps1` locally and enter the
root password only at MySQL's masked prompt. SQL is passed via stdin. The script
generates a dedicated app password and saves only that app credential with Windows
DPAPI encryption under Git-ignored `.local/`. Never put a root password in chat,
command arguments, source files or Git. Existing app credentials are not reset.

For subsequent starts use `scripts/run.ps1`; it loads the encrypted app credential,
selects JDK 21, and uses MySQL. Stop the current API before starting another copy.
No setup blocker remains; Postman and Swagger screenshots still need to be captured
manually.
