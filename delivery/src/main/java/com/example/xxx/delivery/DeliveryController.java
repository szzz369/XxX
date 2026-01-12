package com.example.xxx.delivery;

import com.example.xxx.common.api.ApiResponse;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/delivery")
public class DeliveryController {

    @GetMapping("/ping")
    public ApiResponse<String> ping() {
        return ApiResponse.success("delivery-ok");
    }
}
