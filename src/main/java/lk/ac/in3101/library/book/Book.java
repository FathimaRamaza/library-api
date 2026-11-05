package lk.ac.in3101.library.book;

import jakarta.persistence.*;

@Entity
@Table(name = "books")
public class Book {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(nullable = false, length = 200)
    private String title;
    @Column(nullable = false, length = 150)
    private String author;
    @Column(nullable = false, unique = true, length = 13)
    private String isbn;
    @Column(name = "published_year", nullable = false)
    private Integer publishedYear;

    protected Book() {}
    public Book(BookRequest request) { update(request); }
    public void update(BookRequest request) {
        title = request.title().strip();
        author = request.author().strip();
        isbn = request.isbn();
        publishedYear = request.publishedYear();
    }
    public Long getId() { return id; }
    public String getTitle() { return title; }
    public String getAuthor() { return author; }
    public String getIsbn() { return isbn; }
    public Integer getPublishedYear() { return publishedYear; }
}
