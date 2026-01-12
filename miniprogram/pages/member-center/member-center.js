Page({
  data: {
    levelName: '普通会员',
    growthValue: 1200,
    nextLevelName: '白银会员',
    nextLevelThreshold: 2000,
    discountRate: 0.95,
    pointsMultiplier: 1.2,
    freeShippingThreshold: 88,
    progress: 0,
    remainingGrowth: 0,
    discountRatePercent: 0,
  },
  onLoad() {
    this.updateProgress();
  },
  updateProgress() {
    const { growthValue, nextLevelThreshold, discountRate } = this.data;
    const progress = Math.min(100, Math.floor((growthValue / nextLevelThreshold) * 100));
    const remainingGrowth = Math.max(0, nextLevelThreshold - growthValue);
    const discountRatePercent = Math.round(discountRate * 100);
    this.setData({ progress, remainingGrowth, discountRatePercent });
  },
});
