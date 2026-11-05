# Library REST API

A Spring Boot REST API for managing books. It stores book details in MySQL and
provides endpoints to create, read, update and delete records. Each book has a
title, author, ISBN and publication year.

## Features

- Book CRUD operations
- Request validation and unique ISBNs
- HTTP responses for invalid requests and missing books
- Interactive API documentation with Swagger UI

## Technologies

Java 21, Maven, Spring Boot 4.1.2, Spring Web MVC, Spring Data JPA, MySQL,
Jakarta Validation and springdoc-openapi. Integration tests use JUnit and H2.

## API Endpoints

Base URL: `http://localhost:8080`

| Method | Endpoint | Description | Success |
|---|---|---|---|
| POST | `/api/books` | Create a book | 201 |
| GET | `/api/books` | List all books | 200 |
| GET | `/api/books/{id}` | Get one book | 200 |
| PUT | `/api/books/{id}` | Update a book | 200 |
| DELETE | `/api/books/{id}` | Delete a book | 204 |

Invalid input returns 400, missing books return 404, and duplicate ISBNs return 409.

## Setup and Run

Install JDK 21 and Maven, and start MySQL locally on port 3306.

From the project folder in PowerShell, run the first-time setup:

```powershell
.\scripts\setup-mysql.ps1
```

Enter the MySQL root password at the local prompt. The script creates
`library_db` and a dedicated app account, saves an encrypted app credential
in Git-ignored `.local/`, and starts the API.

For an existing database and app account, use:

```powershell
.\scripts\run.ps1
```

Both scripts select Java 21. The run script uses saved credentials or prompts
for the app password.

To build and run tests:

```powershell
. .\scripts\use-java21.ps1
mvn clean verify
```

## Swagger Documentation

Open [Swagger UI](http://localhost:8080/swagger-ui/index.html) while the API is
running to view endpoints and try requests. The OpenAPI specification is available
at [`/v3/api-docs`](http://localhost:8080/v3/api-docs).
