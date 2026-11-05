package lk.ac.in3101.library.book;

import java.util.List;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.http.HttpStatus;

@Service
@Transactional(readOnly = true)
public class BookService {
    private final BookRepository repository;
    public BookService(BookRepository repository) { this.repository = repository; }
    public List<Book> findAll() { return repository.findAll(Sort.by("id")); }
    public Book findById(long id) {
        return repository.findById(id).orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Book not found"));
    }
    @Transactional
    public Book create(BookRequest request) { return repository.saveAndFlush(new Book(request)); }
    @Transactional
    public Book update(long id, BookRequest request) {
        Book book = findById(id);
        book.update(request);
        return repository.saveAndFlush(book);
    }
    @Transactional
    public void delete(long id) { repository.delete(findById(id)); }
}
