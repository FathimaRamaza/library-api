Library REST API
A simple RESTful API for managing books, built with Spring Boot and MySQL.
Features
- Add new books
- View all books or search by ID
- Update book details
- Delete books
- Validate book information
- API documentation using Swagger UI
Technologies
Java 21 · Spring Boot · Spring Data JPA · MySQL · Maven · Swagger UI · Postman
API Endpoints
Method	Endpoint	Description
GET	/api/books	Retrieve all books
GET	/api/books/{id}	Retrieve a book
POST	/api/books	Add a new book
PUT	/api/books/{id}	Update a book
DELETE	/api/books/{id}	Delete a book

Running the Project
Configure the MySQL database and application settings, then start the Spring Boot application using the provided setup scripts.
.\scripts\setup-mysql.ps1


The API runs at http://localhost:8080.
API Documentation
Swagger UI: http://localhost:8080/swagger-ui.html
