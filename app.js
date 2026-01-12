const routes = {
  home: {
    title: "首页",
    render: renderHome,
  },
  cart: {
    title: "购物车",
    render: renderCart,
  },
  orders: {
    title: "订单详情",
    render: renderOrders,
  },
  points: {
    title: "积分中心",
    render: renderPoints,
  },
};

const defaultCart = [
  {
    id: "sku-1001",
    name: "有机苹果礼盒",
    price: 39.9,
    quantity: 2,
  },
  {
    id: "sku-1002",
    name: "进口牛奶 1L",
    price: 12.5,
    quantity: 1,
  },
  {
    id: "sku-1003",
    name: "全麦吐司",
    price: 15.9,
    quantity: 3,
  },
];

const cartStorageKey = "demo-cart";

const currencyFormatter = new Intl.NumberFormat("zh-CN", {
  style: "currency",
  currency: "CNY",
});

function loadCart() {
  const stored = localStorage.getItem(cartStorageKey);
  if (!stored) {
    localStorage.setItem(cartStorageKey, JSON.stringify(defaultCart));
    return [...defaultCart];
  }
  try {
    const parsed = JSON.parse(stored);
    if (Array.isArray(parsed)) {
      return parsed;
    }
  } catch (error) {
    console.warn("购物车缓存解析失败，已重置。", error);
  }
  localStorage.setItem(cartStorageKey, JSON.stringify(defaultCart));
  return [...defaultCart];
}

function saveCart(items) {
  localStorage.setItem(cartStorageKey, JSON.stringify(items));
}

function updateQuantity(items, id, delta) {
  const updated = items.map((item) => {
    if (item.id !== id) {
      return item;
    }
    const nextQuantity = Math.max(0, item.quantity + delta);
    return {
      ...item,
      quantity: nextQuantity,
    };
  });
  return updated.filter((item) => item.quantity > 0);
}

function formatPrice(value) {
  return currencyFormatter.format(value);
}

function renderHome() {
  return `
    <section class="card">
      <h2>今日推荐</h2>
      <div class="grid-2">
        <div class="card">
          <span class="badge">爆款</span>
          <h3>晨间轻食组合</h3>
          <p class="notice">燕麦 + 低脂酸奶 + 水果杯</p>
          <div class="highlight">${formatPrice(49.9)}</div>
        </div>
        <div class="card">
          <span class="badge">新品</span>
          <h3>家庭囤货包</h3>
          <p class="notice">米面粮油一站购齐</p>
          <div class="highlight">${formatPrice(199)}</div>
        </div>
      </div>
    </section>
    <section class="card">
      <h2>服务亮点</h2>
      <ul class="list">
        <li class="list-item">30 分钟极速达<span>🚀</span></li>
        <li class="list-item">冷链全程监控<span>❄️</span></li>
        <li class="list-item">售后无忧保障<span>🛡️</span></li>
      </ul>
    </section>
  `;
}

function renderCart() {
  const cartItems = loadCart();
  const subtotal = cartItems.reduce((sum, item) => sum + item.price * item.quantity, 0);
  const deliveryFee = subtotal >= 99 ? 0 : 6;
  const discount = subtotal >= 150 ? 15 : 0;
  const total = subtotal + deliveryFee - discount;

  const itemsMarkup = cartItems
    .map(
      (item) => `
        <div class="cart-item" data-id="${item.id}">
          <div class="cart-item-info">
            <strong>${item.name}</strong>
            <span class="notice">单价 ${formatPrice(item.price)}</span>
          </div>
          <div class="cart-controls">
            <button class="quantity-btn" data-action="decrease">-</button>
            <span>${item.quantity}</span>
            <button class="quantity-btn" data-action="increase">+</button>
          </div>
        </div>
      `
    )
    .join("");

  return `
    <section class="card">
      <h2>购物车商品</h2>
      ${itemsMarkup || '<p class="notice">购物车为空，去首页选购吧。</p>'}
    </section>
    <section class="card">
      <h2>价格明细</h2>
      <div class="list">
        <div class="list-item"><span>商品小计</span><span>${formatPrice(subtotal)}</span></div>
        <div class="list-item"><span>配送费</span><span>${deliveryFee === 0 ? "免运费" : formatPrice(deliveryFee)}</span></div>
        <div class="list-item"><span>满减优惠</span><span>-${formatPrice(discount)}</span></div>
      </div>
      <div class="total-row" style="margin-top: 12px;">
        <span>应付总额</span>
        <span>${formatPrice(total)}</span>
      </div>
      <p class="notice" style="margin-top: 8px;">提示：商品数量变动后将实时更新价格。</p>
    </section>
  `;
}

function renderOrders() {
  return `
    <section class="card">
      <h2>订单信息</h2>
      <div class="list">
        <div class="list-item"><span>订单编号</span><span>#20240412-8891</span></div>
        <div class="list-item"><span>配送方式</span><span>冷链直送</span></div>
        <div class="list-item"><span>收货地址</span><span>上海市徐汇区xx路128号</span></div>
      </div>
    </section>
    <section class="card">
      <h2>配送轨迹</h2>
      <div class="timeline">
        <div class="timeline-item">
          <div class="timeline-dot"></div>
          <div class="timeline-content">
            <strong>骑手已送达</strong>
            <p class="notice">10:15 已签收，欢迎评价</p>
          </div>
        </div>
        <div class="timeline-item">
          <div class="timeline-dot"></div>
          <div class="timeline-content">
            <strong>配送中</strong>
            <p class="notice">09:40 骑手距你 1.2km</p>
          </div>
        </div>
        <div class="timeline-item">
          <div class="timeline-dot"></div>
          <div class="timeline-content">
            <strong>仓库出库</strong>
            <p class="notice">09:10 商品完成拣货打包</p>
          </div>
        </div>
      </div>
    </section>
    <section class="card">
      <h2>售后服务</h2>
      <p class="notice">如需退款或补寄，请点击下方入口。</p>
      <button class="action-button" type="button">申请售后</button>
    </section>
  `;
}

function renderPoints() {
  return `
    <section class="card">
      <h2>积分余额</h2>
      <div class="highlight">3,280 积分</div>
      <p class="notice">积分可抵扣运费或兑换礼品。</p>
      <div class="grid-2" style="margin-top: 12px;">
        <button class="action-button" type="button">立即充值</button>
        <button class="action-button" type="button" style="background:#111827;">兑换礼品</button>
      </div>
    </section>
    <section class="card">
      <h2>积分流水</h2>
      <div class="list">
        <div class="list-item"><span>4/10 购物返积分</span><span>+120</span></div>
        <div class="list-item"><span>4/08 运费抵扣</span><span>-80</span></div>
        <div class="list-item"><span>4/05 充值赠送</span><span>+300</span></div>
        <div class="list-item"><span>4/01 完成订单</span><span>+90</span></div>
      </div>
    </section>
  `;
}

function renderRoute(routeKey) {
  const route = routes[routeKey] || routes.home;
  const mainContent = document.getElementById("main-content");
  const title = document.getElementById("page-title");
  title.textContent = route.title;
  mainContent.innerHTML = route.render();
  attachCartHandlers(routeKey);
}

function attachCartHandlers(routeKey) {
  if (routeKey !== "cart") {
    return;
  }
  const mainContent = document.getElementById("main-content");
  const buttons = mainContent.querySelectorAll(".quantity-btn");
  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      const itemElement = button.closest(".cart-item");
      if (!itemElement) {
        return;
      }
      const id = itemElement.dataset.id;
      const action = button.dataset.action;
      const delta = action === "increase" ? 1 : -1;
      const updated = updateQuantity(loadCart(), id, delta);
      saveCart(updated);
      renderRoute("cart");
    });
  });
}

function setActiveTab(routeKey) {
  const tabs = document.querySelectorAll(".tabbar-item");
  tabs.forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.route === routeKey);
  });
}

function navigate(routeKey) {
  const target = routes[routeKey] ? routeKey : "home";
  window.location.hash = target;
}

function handleHashChange() {
  const routeKey = window.location.hash.replace("#", "") || "home";
  renderRoute(routeKey);
  setActiveTab(routeKey);
}

document.querySelectorAll(".tabbar-item").forEach((tab) => {
  tab.addEventListener("click", () => navigate(tab.dataset.route));
});

window.addEventListener("hashchange", handleHashChange);

handleHashChange();
