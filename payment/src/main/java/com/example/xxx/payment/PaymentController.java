package com.example.xxx.payment;

import com.example.xxx.common.api.ApiResponse;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/payment")
public class PaymentController {

    @GetMapping("/ping")
    public ApiResponse<String> ping() {
        return ApiResponse.success("payment-ok");
    }
}
