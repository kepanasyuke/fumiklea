package com.library.controller;

import com.library.dto.BorrowRecordDto;
import com.library.dto.BorrowRequest;
import com.library.service.BorrowingService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/borrow")
@RequiredArgsConstructor
public class BorrowingController {
    private final BorrowingService borrowingService;

    @PostMapping("/issue")
    @ResponseStatus(HttpStatus.CREATED)
    public BorrowRecordDto issueBook(@Valid @RequestBody BorrowRequest request,
                                     @AuthenticationPrincipal UserDetails userDetails) {
        return borrowingService.issueBook(request.getBookId(), userDetails.getUsername());
    }

    @PutMapping("/return/{borrowingId}")
    public BorrowRecordDto returnBook(@PathVariable Long borrowingId,
                                      @AuthenticationPrincipal UserDetails userDetails) {
        return borrowingService.returnBook(borrowingId, userDetails.getUsername());
    }

    @GetMapping("/history")
    public List<BorrowRecordDto> getHistory(@AuthenticationPrincipal UserDetails userDetails) {
        return borrowingService.getUserBorrowings(userDetails.getUsername());
    }
}
