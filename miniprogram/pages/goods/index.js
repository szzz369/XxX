const app = getApp();

Page({
  data: {
    goods: [],
    selectedGoodsName: '',
    cartCount: 0,
    isLoading: true,
  },
  onLoad() {
    this.fetchGoods();
    this.refreshGlobalState();
  },
  onShow() {
    this.refreshGlobalState();
  },
  refreshGlobalState() {
    const { selectedGoods, cartCount } = app.globalData;
    this.setData({
      selectedGoodsName: selectedGoods ? selectedGoods.name : '',
      cartCount,
    });
  },
  fetchGoods() {
    this.setData({ isLoading: true });
    wx.request({
      url: `${app.globalData.apiBaseUrl}/goods`,
      method: 'GET',
      success: (res) => {
        const list = res?.data?.data ?? [];
        if (Array.isArray(list) && list.length > 0) {
          this.setData({ goods: list, isLoading: false });
          return;
        }
        this.useFallbackGoods();
      },
      fail: () => {
        this.useFallbackGoods();
      },
    });
  },
  useFallbackGoods() {
    this.setData({
      goods: [
        { id: 'sku-1', name: '会员精选咖啡豆', price: 68, stock: 20 },
        { id: 'sku-2', name: '轻食沙拉', price: 42, stock: 15 },
        { id: 'sku-3', name: '能量果昔', price: 32, stock: 25 },
      ],
      isLoading: false,
    });
  },
  selectGoods(event) {
    const { goods } = event.currentTarget.dataset;
    app.globalData.selectedGoods = goods;
    this.refreshGlobalState();
    wx.navigateTo({
      url: `/pages/member-center/member-center?selected=${goods.name}`,
    });
  },
  addToCart(event) {
    const { goods } = event.currentTarget.dataset;
    app.globalData.cartCount += 1;
    app.globalData.selectedGoods = goods;
    this.refreshGlobalState();
  },
});
