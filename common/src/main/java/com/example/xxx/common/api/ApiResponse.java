package com.example.xxx.common.api;

import java.time.OffsetDateTime;

public class ApiResponse<T> {
    private final String code;
    private final String message;
    private final T data;
    private final OffsetDateTime timestamp;

    private ApiResponse(String code, String message, T data, OffsetDateTime timestamp) {
        this.code = code;
        this.message = message;
        this.data = data;
        this.timestamp = timestamp;
    }

    public static <T> ApiResponse<T> success(T data) {
        return new ApiResponse<>("0", "OK", data, OffsetDateTime.now());
    }

    public static <T> ApiResponse<T> failure(String code, String message) {
        return new ApiResponse<>(code, message, null, OffsetDateTime.now());
    }

    public String getCode() {
        return code;
    }

    public String getMessage() {
        return message;
    }

    public T getData() {
        return data;
    }

    public OffsetDateTime getTimestamp() {
        return timestamp;
    }
}
