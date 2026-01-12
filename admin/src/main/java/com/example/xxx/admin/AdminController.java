package com.example.xxx.admin;

import com.example.xxx.common.api.ApiResponse;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/admin")
public class AdminController {

    @GetMapping("/ping")
    public ApiResponse<String> ping() {
        return ApiResponse.success("admin-ok");
    }
}
