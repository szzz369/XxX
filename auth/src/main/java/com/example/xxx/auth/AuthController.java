package com.example.xxx.auth;

import com.example.xxx.common.api.ApiResponse;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/auth")
public class AuthController {

    @GetMapping("/ping")
    public ApiResponse<String> ping() {
        return ApiResponse.success("auth-ok");
    }
}
