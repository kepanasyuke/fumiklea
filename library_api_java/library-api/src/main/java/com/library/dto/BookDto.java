package com.library.dto;

import lombok.Data;
import jakarta.validation.constraints.*;

@Data
public class BookDto {
    private Long id;
    @NotBlank
    private String title;
    @NotBlank
    private String author;
    @NotBlank
    private String isbn;
    @Min(1000) @Max(2100)
    private Integer publishedYear;
    @Positive
    private Integer totalCopies;
    private Integer availableCopies; // auto-calculated
}