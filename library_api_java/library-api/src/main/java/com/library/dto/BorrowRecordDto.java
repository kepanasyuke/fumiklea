package com.library.dto;

import lombok.Data;
import java.time.LocalDate;

@Data
public class BorrowRecordDto {
    private Long id;
    private String bookTitle;
    private String username;
    private LocalDate borrowDate;
    private LocalDate dueDate;
    private LocalDate returnDate;
    private String status;
}