package com.library.repository;

import com.library.entity.Borrowing;
import com.library.entity.Book;
import com.library.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface BorrowingRepository extends JpaRepository<Borrowing, Long> {
    List<Borrowing> findByUser(User user);
    boolean existsByUserAndBookAndReturnDateIsNull(User user, Book book);
}