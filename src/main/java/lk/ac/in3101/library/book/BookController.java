package lk.ac.in3101.library.book;

import java.util.List;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Positive;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.support.ServletUriComponentsBuilder;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import org.springframework.http.ProblemDetail;
import io.swagger.v3.oas.annotations.tags.Tag;

@RestController
@RequestMapping("/api/books")
@Tag(name = "Books", description = "Library book CRUD operations")
public class BookController {
    private final BookService service;
    public BookController(BookService service) { this.service = service; }
    @GetMapping
    @Operation(summary = "List all books")
    public List<Book> list() { return service.findAll(); }
    @GetMapping("/{id}")
    public Book get(@PathVariable @Positive long id) { return service.findById(id); }
    @PostMapping
    @Operation(summary = "Create a book")
    @ApiResponses({
        @ApiResponse(responseCode = "201", description = "Book created; Location header identifies the new book", useReturnTypeSchema = true),
        @ApiResponse(responseCode = "400", description = "Invalid request, including an empty title",
            content = @Content(mediaType = "application/problem+json", schema = @Schema(implementation = ProblemDetail.class))),
        @ApiResponse(responseCode = "409", description = "ISBN already exists",
            content = @Content(mediaType = "application/problem+json", schema = @Schema(implementation = ProblemDetail.class)))
    })
    public ResponseEntity<Book> create(@Valid @RequestBody BookRequest request) {
        Book book = service.create(request);
        return ResponseEntity.created(ServletUriComponentsBuilder.fromCurrentRequest().path("/{id}").buildAndExpand(book.getId()).toUri()).body(book);
    }
    @PutMapping("/{id}")
    public Book update(@PathVariable @Positive long id, @Valid @RequestBody BookRequest request) { return service.update(id, request); }
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable @Positive long id) {
        service.delete(id);
        return ResponseEntity.noContent().build();
    }
}
