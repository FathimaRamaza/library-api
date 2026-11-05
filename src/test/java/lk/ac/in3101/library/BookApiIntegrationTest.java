package lk.ac.in3101.library;

import java.net.URI;
import java.net.http.*;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;
import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT, properties = {
    "spring.datasource.url=jdbc:h2:mem:library;MODE=MySQL;DB_CLOSE_DELAY=-1",
    "spring.datasource.username=sa", "spring.datasource.password=",
    "spring.datasource.driver-class-name=org.h2.Driver"
})
class BookApiIntegrationTest {
    @LocalServerPort int port;
    final HttpClient client = HttpClient.newHttpClient();
    HttpResponse<String> request(String method, String path, String body) throws Exception {
        return client.send(HttpRequest.newBuilder(URI.create("http://localhost:" + port + path))
            .header("Content-Type", "application/json")
            .method(method, body == null ? HttpRequest.BodyPublishers.noBody() : HttpRequest.BodyPublishers.ofString(body))
            .build(), HttpResponse.BodyHandlers.ofString());
    }
    @Test void crudValidationAndDocumentation() throws Exception {
        String book = """
            {"title":"Clean Code","author":"Robert C. Martin","isbn":"9780132350884","publishedYear":2008}
            """;
        assertThat(request("POST", "/api/books", "{}").statusCode()).isEqualTo(400);
        assertThat(request("POST", "/api/books", "{").statusCode()).isEqualTo(400);
        var created = request("POST", "/api/books", book);
        assertThat(created.statusCode()).isEqualTo(201);
        String path = URI.create(created.headers().firstValue("Location").orElseThrow()).getPath();
        assertThat(request("GET", path, null).body()).contains("Clean Code");
        assertThat(request("GET", "/api/books", null).body()).contains("9780132350884");
        assertThat(request("POST", "/api/books", book).statusCode()).isEqualTo(409);
        var updated = request("PUT", path, book.replace("Clean Code", "Clean Code Updated"));
        assertThat(updated.statusCode()).isEqualTo(200);
        assertThat(updated.body()).contains("Clean Code Updated");
        assertThat(request("DELETE", path, null).statusCode()).isEqualTo(204);
        assertThat(request("GET", path, null).statusCode()).isEqualTo(404);
        assertThat(request("PUT", path, book).statusCode()).isEqualTo(404);
        assertThat(request("DELETE", path, null).statusCode()).isEqualTo(404);
        assertThat(request("GET", "/api/books/0", null).statusCode()).isEqualTo(400);
        assertThat(request("GET", "/v3/api-docs", null).statusCode()).isEqualTo(200);
        String docs = request("GET", "/v3/api-docs", null).body();
        var openApi = new tools.jackson.databind.ObjectMapper().readTree(docs);
        var postResponses = openApi.path("paths").path("/api/books").path("post").path("responses");
        assertThat(postResponses.has("201")).isTrue();
        assertThat(postResponses.has("400")).isTrue();
        var examples = java.util.Map.of("title", "Clean Code", "author", "Robert C. Martin",
                "isbn", "9780132350884", "publishedYear", "2008");
        for (String schema : java.util.List.of("BookRequest", "Book")) {
            var properties = openApi.path("components").path("schemas").path(schema).path("properties");
            examples.forEach((field, expected) -> assertThat(properties.path(field).path("example").asText())
                    .as("%s.%s example", schema, field).isEqualTo(expected));
        }
        assertThat(request("GET", "/swagger-ui/index.html", null).statusCode()).isEqualTo(200);
    }
}
