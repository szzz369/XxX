package com.example.xxx.order;

import com.example.xxx.common.tenant.TenantContext;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

@Service
public class OrderStatusService {
    private static final String KEY_PREFIX = "order:status:";

    private final StringRedisTemplate redisTemplate;

    public OrderStatusService(StringRedisTemplate redisTemplate) {
        this.redisTemplate = redisTemplate;
    }

    public void updateStatus(String orderId, String status) {
        String key = buildKey(orderId);
        redisTemplate.opsForValue().set(key, status);
    }

    public String getStatus(String orderId) {
        String key = buildKey(orderId);
        return redisTemplate.opsForValue().get(key);
    }

    private String buildKey(String orderId) {
        String tenantId = TenantContext.getTenantId();
        return KEY_PREFIX + tenantId + ":" + orderId;
    }
}
