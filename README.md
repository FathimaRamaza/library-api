# Library REST API

A Spring Boot REST API for managing books with MySQL storage, input validation, and Swagger documentation.

## Features

- Create, list, retrieve, update, and delete books.
- Validate required fields and reject duplicate ISBNs.
- Return appropriate HTTP responses for invalid requests and missing books.

## Technologies

Java 21, Spring Boot, Spring Data JPA, MySQL, Maven, Swagger UI and Postman.

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/books` | List all books |
| GET | `/api/books/{id}` | Get a book by ID |
| POST | `/api/books` | Create a book |
| PUT | `/api/books/{id}` | Update a book |
| DELETE | `/api/books/{id}` | Delete a book |

## Running the Project

Install Java 21 and Maven, start MySQL on port 3306, then run this first-time setup from the project folder:

```powershell
.\scripts\setup-mysql.ps1
```

Enter the MySQL root password at the local prompt. The script creates the database and app account, then starts the API.

For an existing setup, use `.\scripts\run.ps1` instead.

## API Documentation

With the application running, open Swagger UI to explore and try endpoints:

http://localhost:8080/swagger-ui/index.html
