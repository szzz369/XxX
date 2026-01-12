package com.example.xxx.order;

public class MemberSummary {
    private final String levelName;
    private final int growthValue;
    private final String nextLevelName;
    private final int nextLevelThreshold;
    private final double discountRate;
    private final double pointsMultiplier;
    private final int freeShippingThreshold;

    public MemberSummary(
            String levelName,
            int growthValue,
            String nextLevelName,
            int nextLevelThreshold,
            double discountRate,
            double pointsMultiplier,
            int freeShippingThreshold) {
        this.levelName = levelName;
        this.growthValue = growthValue;
        this.nextLevelName = nextLevelName;
        this.nextLevelThreshold = nextLevelThreshold;
        this.discountRate = discountRate;
        this.pointsMultiplier = pointsMultiplier;
        this.freeShippingThreshold = freeShippingThreshold;
    }

    public String getLevelName() {
        return levelName;
    }

    public int getGrowthValue() {
        return growthValue;
    }

    public String getNextLevelName() {
        return nextLevelName;
    }

    public int getNextLevelThreshold() {
        return nextLevelThreshold;
    }

    public double getDiscountRate() {
        return discountRate;
    }

    public double getPointsMultiplier() {
        return pointsMultiplier;
    }

    public int getFreeShippingThreshold() {
        return freeShippingThreshold;
    }
}
