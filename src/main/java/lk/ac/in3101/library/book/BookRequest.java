package lk.ac.in3101.library.book;

import jakarta.validation.constraints.*;

public record BookRequest(
    @NotBlank @Size(max = 200) String title,
    @NotBlank @Size(max = 150) String author,
    @NotBlank @Pattern(regexp = "(?:[0-9]{13}|[0-9]{9}[0-9Xx])", message = "must be a 10 or 13 character ISBN without hyphens") String isbn,
    @NotNull @Min(1) @Max(9999) Integer publishedYear
) {}
