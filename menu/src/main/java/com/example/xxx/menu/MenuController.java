package com.example.xxx.menu;

import com.example.xxx.common.api.ApiResponse;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/menu")
public class MenuController {

    @GetMapping("/ping")
    public ApiResponse<String> ping() {
        return ApiResponse.success("menu-ok");
    }
}
