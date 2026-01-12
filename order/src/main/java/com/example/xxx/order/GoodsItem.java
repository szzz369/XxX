package com.example.xxx.order;

public class GoodsItem {
    private final String id;
    private final String name;
    private final int price;
    private final int stock;

    public GoodsItem(String id, String name, int price, int stock) {
        this.id = id;
        this.name = name;
        this.price = price;
        this.stock = stock;
    }

    public String getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public int getPrice() {
        return price;
    }

    public int getStock() {
        return stock;
    }
}
