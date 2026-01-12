package com.example.xxx.points;

import com.example.xxx.common.api.ApiResponse;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/points")
public class PointsController {

    @GetMapping("/ping")
    public ApiResponse<String> ping() {
        return ApiResponse.success("points-ok");
    }
}
