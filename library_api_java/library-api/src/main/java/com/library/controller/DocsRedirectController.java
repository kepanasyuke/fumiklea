package com.library.controller;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.net.URI;

@RestController
public class DocsRedirectController {

    @GetMapping("/api-docs")
    public ResponseEntity<Void> redirectToV3ApiDocs() {
        return ResponseEntity.status(HttpStatus.FOUND)
                .location(URI.create("/v3/api-docs"))
                .build();
    }
}
