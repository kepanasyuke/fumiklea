package com.library.service;

import com.library.dto.BookDto;
import com.library.entity.Book;
import com.library.exception.ResourceNotFoundException;
import com.library.repository.BookRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class BookService {
    private final BookRepository bookRepository;

    public List<BookDto> search(String title, String author, String isbn) {
        return bookRepository.searchBooks(title, author, isbn)
                .stream().map(this::toDto).collect(Collectors.toList());
    }

    public BookDto create(BookDto dto) {
        Book book = toEntity(dto);
        book.setAvailableCopies(dto.getTotalCopies());
        return toDto(bookRepository.save(book));
    }

    public BookDto update(Long id, BookDto dto) {
        Book book = bookRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Book not found"));
        book.setTitle(dto.getTitle());
        book.setAuthor(dto.getAuthor());
        book.setIsbn(dto.getIsbn());
        book.setPublishedYear(dto.getPublishedYear());
        book.setTotalCopies(dto.getTotalCopies());
        // availableCopies logic: if totalCopies increased, add difference
        int diff = dto.getTotalCopies() - book.getTotalCopies();
        book.setAvailableCopies(book.getAvailableCopies() + diff);
        return toDto(bookRepository.save(book));
    }

    public void delete(Long id) {
        bookRepository.deleteById(id);
    }

    private BookDto toDto(Book book) {
        BookDto dto = new BookDto();
        dto.setId(book.getId());
        dto.setTitle(book.getTitle());
        dto.setAuthor(book.getAuthor());
        dto.setIsbn(book.getIsbn());
        dto.setPublishedYear(book.getPublishedYear());
        dto.setTotalCopies(book.getTotalCopies());
        dto.setAvailableCopies(book.getAvailableCopies());
        return dto;
    }

    private Book toEntity(BookDto dto) {
        return Book.builder()
                .title(dto.getTitle())
                .author(dto.getAuthor())
                .isbn(dto.getIsbn())
                .publishedYear(dto.getPublishedYear())
                .totalCopies(dto.getTotalCopies())
                .build();
    }
}
