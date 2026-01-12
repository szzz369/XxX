const app = getApp();

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
    selectedGoodsName: '',
    cartCount: 0,
  },
  onLoad(options) {
    const selectedGoodsName =
      options.selected || (app.globalData.selectedGoods?.name ?? '');
    this.setData({ selectedGoodsName });
    this.fetchMemberSummary();
    this.updateProgress();
  },
  onShow() {
    this.setData({ cartCount: app.globalData.cartCount });
  },
  updateProgress() {
    const { growthValue, nextLevelThreshold, discountRate } = this.data;
    const progress = Math.min(100, Math.floor((growthValue / nextLevelThreshold) * 100));
    const remainingGrowth = Math.max(0, nextLevelThreshold - growthValue);
    const discountRatePercent = Math.round(discountRate * 100);
    this.setData({ progress, remainingGrowth, discountRatePercent });
  },
  fetchMemberSummary() {
    wx.request({
      url: `${app.globalData.apiBaseUrl}/members/summary`,
      method: 'GET',
      success: (res) => {
        const data = res?.data?.data;
        if (!data) {
          return;
        }
        this.setData({
          levelName: data.levelName ?? this.data.levelName,
          growthValue: data.growthValue ?? this.data.growthValue,
          nextLevelName: data.nextLevelName ?? this.data.nextLevelName,
          nextLevelThreshold: data.nextLevelThreshold ?? this.data.nextLevelThreshold,
          discountRate: data.discountRate ?? this.data.discountRate,
          pointsMultiplier: data.pointsMultiplier ?? this.data.pointsMultiplier,
          freeShippingThreshold:
            data.freeShippingThreshold ?? this.data.freeShippingThreshold,
        });
        this.updateProgress();
      },
    });
  },
  goToGoods() {
    wx.switchTab({ url: '/pages/goods/index' });
  },
});
