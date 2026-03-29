package com.library.service;

import com.library.dto.BorrowRecordDto;
import com.library.entity.Book;
import com.library.entity.Borrowing;
import com.library.entity.User;
import com.library.exception.BusinessException;
import com.library.exception.ResourceNotFoundException;
import com.library.repository.BookRepository;
import com.library.repository.BorrowingRepository;
import com.library.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.time.LocalDate;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class BorrowingService {
    private final BorrowingRepository borrowingRepository;
    private final BookRepository bookRepository;
    private final UserRepository userRepository;

    @Transactional
    public BorrowRecordDto issueBook(Long bookId, String username) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new ResourceNotFoundException("User not found"));
        Book book = bookRepository.findById(bookId)
                .orElseThrow(() -> new ResourceNotFoundException("Book not found"));

        if (book.getAvailableCopies() <= 0) {
            throw new BusinessException("No available copies");
        }
        if (borrowingRepository.existsByUserAndBookAndReturnDateIsNull(user, book)) {
            throw new BusinessException("User already borrowed this book and hasn't returned it");
        }

        book.setAvailableCopies(book.getAvailableCopies() - 1);
        bookRepository.save(book);

        Borrowing borrowing = Borrowing.builder()
                .user(user)
                .book(book)
                .borrowDate(LocalDate.now())
                .dueDate(LocalDate.now().plusDays(14))
                .status("BORROWED")
                .build();
        return toDto(borrowingRepository.save(borrowing));
    }

    @Transactional
    public BorrowRecordDto returnBook(Long borrowingId, String username) {
        Borrowing borrowing = borrowingRepository.findById(borrowingId)
                .orElseThrow(() -> new ResourceNotFoundException("Borrowing record not found"));
        if (!borrowing.getUser().getUsername().equals(username)) {
            throw new BusinessException("You can only return your own borrowings");
        }
        if (borrowing.getReturnDate() != null) {
            throw new BusinessException("Book already returned");
        }

        borrowing.setReturnDate(LocalDate.now());
        borrowing.setStatus("RETURNED");
        Book book = borrowing.getBook();
        book.setAvailableCopies(book.getAvailableCopies() + 1);
        bookRepository.save(book);

        return toDto(borrowingRepository.save(borrowing));
    }

    public List<BorrowRecordDto> getUserBorrowings(String username) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new ResourceNotFoundException("User not found"));
        return borrowingRepository.findByUser(user).stream()
                .map(this::toDto).collect(Collectors.toList());
    }

    private BorrowRecordDto toDto(Borrowing b) {
        BorrowRecordDto dto = new BorrowRecordDto();
        dto.setId(b.getId());
        dto.setBookTitle(b.getBook().getTitle());
        dto.setUsername(b.getUser().getUsername());
        dto.setBorrowDate(b.getBorrowDate());
        dto.setDueDate(b.getDueDate());
        dto.setReturnDate(b.getReturnDate());
        dto.setStatus(b.getStatus());
        return dto;
    }
}