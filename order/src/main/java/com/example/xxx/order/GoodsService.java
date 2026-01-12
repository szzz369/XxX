package com.example.xxx.order;

import java.util.List;
import org.springframework.stereotype.Service;

@Service
public class GoodsService {
    public List<GoodsItem> listGoods() {
        return List.of(
                new GoodsItem("sku-1", "会员精选咖啡豆", 68, 20),
                new GoodsItem("sku-2", "轻食沙拉", 42, 15),
                new GoodsItem("sku-3", "能量果昔", 32, 25));
    }
}
