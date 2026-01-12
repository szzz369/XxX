package com.example.xxx.order;

import com.example.xxx.common.api.ApiResponse;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/orders")
public class OrderController {

    private final OrderStatusService orderStatusService;

    public OrderController(OrderStatusService orderStatusService) {
        this.orderStatusService = orderStatusService;
    }

    @GetMapping("/ping")
    public ApiResponse<String> ping() {
        return ApiResponse.success("order-ok");
    }

    @PostMapping("/{orderId}/status")
    public ApiResponse<Void> updateStatus(@PathVariable String orderId, @RequestParam String status) {
        orderStatusService.updateStatus(orderId, status);
        return ApiResponse.success(null);
    }

    @GetMapping("/{orderId}/status")
    public ApiResponse<String> getStatus(@PathVariable String orderId) {
        return ApiResponse.success(orderStatusService.getStatus(orderId));
    }
}
