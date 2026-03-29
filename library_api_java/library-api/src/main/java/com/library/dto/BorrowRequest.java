package com.library.dto;

import lombok.Data;
import jakarta.validation.constraints.NotNull;

@Data
public class BorrowRequest {
    @NotNull
    private Long bookId;
}
