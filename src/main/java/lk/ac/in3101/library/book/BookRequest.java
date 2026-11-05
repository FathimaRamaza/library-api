package lk.ac.in3101.library.book;

import jakarta.validation.constraints.*;
import io.swagger.v3.oas.annotations.media.Schema;

public record BookRequest(
    @Schema(example = "Clean Code") @NotBlank @Size(max = 200) String title,
    @Schema(example = "Robert C. Martin") @NotBlank @Size(max = 150) String author,
    @Schema(example = "9780132350884") @NotBlank @Pattern(regexp = "(?:[0-9]{13}|[0-9]{9}[0-9Xx])", message = "must be a 10 or 13 character ISBN without hyphens") String isbn,
    @Schema(example = "2008") @NotNull @Min(1) @Max(9999) Integer publishedYear
) {}
