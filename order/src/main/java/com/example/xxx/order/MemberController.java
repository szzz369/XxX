package com.example.xxx.order;

import com.example.xxx.common.api.ApiResponse;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/members")
public class MemberController {

    @GetMapping("/summary")
    public ApiResponse<MemberSummary> summary() {
        MemberSummary summary =
                new MemberSummary("普通会员", 1200, "白银会员", 2000, 0.95, 1.2, 88);
        return ApiResponse.success(summary);
    }
}
