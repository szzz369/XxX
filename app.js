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
  admin: {
    title: "管理后台",
    render: renderAdmin,
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
const pointsStorageKey = "demo-points";
const pointsHistoryKey = "demo-points-history";

const defaultPoints = {
  balance: 3280,
};

const defaultPointsHistory = [
  { label: "4/10 购物返积分", value: 120 },
  { label: "4/08 运费抵扣", value: -80 },
  { label: "4/05 充值赠送", value: 300 },
  { label: "4/01 完成订单", value: 90 },
];

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

function loadPoints() {
  const stored = localStorage.getItem(pointsStorageKey);
  if (!stored) {
    localStorage.setItem(pointsStorageKey, JSON.stringify(defaultPoints));
    return { ...defaultPoints };
  }
  try {
    const parsed = JSON.parse(stored);
    if (parsed && typeof parsed.balance === "number") {
      return parsed;
    }
  } catch (error) {
    console.warn("积分缓存解析失败，已重置。", error);
  }
  localStorage.setItem(pointsStorageKey, JSON.stringify(defaultPoints));
  return { ...defaultPoints };
}

function savePoints(points) {
  localStorage.setItem(pointsStorageKey, JSON.stringify(points));
}

function loadPointsHistory() {
  const stored = localStorage.getItem(pointsHistoryKey);
  if (!stored) {
    localStorage.setItem(pointsHistoryKey, JSON.stringify(defaultPointsHistory));
    return [...defaultPointsHistory];
  }
  try {
    const parsed = JSON.parse(stored);
    if (Array.isArray(parsed)) {
      return parsed;
    }
  } catch (error) {
    console.warn("积分流水缓存解析失败，已重置。", error);
  }
  localStorage.setItem(pointsHistoryKey, JSON.stringify(defaultPointsHistory));
  return [...defaultPointsHistory];
}

function savePointsHistory(history) {
  localStorage.setItem(pointsHistoryKey, JSON.stringify(history));
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
    <section class="card">
      <h2>运营管理入口</h2>
      <p class="notice">进入管理后台查看订单、配送与积分运营数据。</p>
      <button class="action-button" type="button" data-route-link="admin">进入管理后台</button>
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
      <div class="section-header">
        <h2>购物车商品</h2>
        <button class="ghost-button" type="button" data-action="clear-cart">清空</button>
      </div>
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
      <div class="button-row">
        <button class="action-button" type="button" data-action="checkout" ${cartItems.length ? "" : "disabled"}>
          去结算
        </button>
        <button class="secondary-button" type="button" data-action="save-cart" ${cartItems.length ? "" : "disabled"}>
          保存购物车
        </button>
      </div>
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
      <button class="action-button" type="button" data-action="after-sale">申请售后</button>
    </section>
  `;
}

function renderPoints() {
  const points = loadPoints();
  const history = loadPointsHistory();
  const historyMarkup = history
    .map((item) => {
      const sign = item.value > 0 ? "+" : "";
      return `<div class="list-item"><span>${item.label}</span><span>${sign}${item.value}</span></div>`;
    })
    .join("");
  return `
    <section class="card">
      <h2>积分余额</h2>
      <div class="highlight">${points.balance.toLocaleString("zh-CN")} 积分</div>
      <p class="notice">积分可抵扣运费或兑换礼品。</p>
      <div class="grid-2" style="margin-top: 12px;">
        <button class="action-button" type="button" data-action="recharge-points">立即充值</button>
        <button class="action-button dark" type="button" data-action="redeem-points">兑换礼品</button>
      </div>
    </section>
    <section class="card">
      <h2>积分流水</h2>
      <div class="list">
        ${historyMarkup}
      </div>
    </section>
  `;
}

function renderAdmin() {
  return `
    <section class="card">
      <h2>管理后台概览</h2>
      <p class="notice">对应后端模块：认证、菜单、订单、支付、配送、积分与统一管理。</p>
      <div class="module-grid">
        <div class="module-card">
          <div class="module-title"><span>auth</span><span class="badge">用户</span></div>
          <div class="module-meta">账号登录、权限认证、会话管理。</div>
        </div>
        <div class="module-card">
          <div class="module-title"><span>menu</span><span class="badge">商品</span></div>
          <div class="module-meta">商品菜单、分类配置、上下架管理。</div>
        </div>
        <div class="module-card">
          <div class="module-title"><span>order</span><span class="badge">订单</span></div>
          <div class="module-meta">订单接单、状态流转、售后处理。</div>
        </div>
        <div class="module-card">
          <div class="module-title"><span>payment</span><span class="badge">支付</span></div>
          <div class="module-meta">支付渠道配置、交易回调对账。</div>
        </div>
        <div class="module-card">
          <div class="module-title"><span>delivery</span><span class="badge">配送</span></div>
          <div class="module-meta">履约方式、骑手轨迹、签收状态。</div>
        </div>
        <div class="module-card">
          <div class="module-title"><span>points</span><span class="badge">积分</span></div>
          <div class="module-meta">积分规则、营销配置与对账。</div>
        </div>
      </div>
    </section>
    <section class="card">
      <h2>快捷操作</h2>
      <div class="list">
        <div class="list-item"><span>今日待处理订单</span><span>18</span></div>
        <div class="list-item"><span>待处理退款申请</span><span>3</span></div>
        <div class="list-item"><span>配送异常预警</span><span>2</span></div>
      </div>
      <button class="action-button" type="button" data-route-link="orders" style="margin-top: 12px;">
        查看订单详情
      </button>
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
  attachRouteLinks();
  attachActionHandlers();
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

function attachRouteLinks() {
  const mainContent = document.getElementById("main-content");
  const links = mainContent.querySelectorAll("[data-route-link]");
  links.forEach((link) => {
    link.addEventListener("click", () => navigate(link.dataset.routeLink));
  });
}

function attachActionHandlers() {
  const mainContent = document.getElementById("main-content");
  const actions = mainContent.querySelectorAll("[data-action]");
  actions.forEach((button) => {
    button.addEventListener("click", () => handleAction(button.dataset.action));
  });
}

function handleAction(action) {
  switch (action) {
    case "after-sale":
      openModal({
        title: "售后申请",
        description: "我们将为你创建售后工单，预计 10 分钟内响应。",
        confirmText: "提交申请",
        onConfirm: () => showToast("售后申请已提交，请留意客服消息。"),
      });
      break;
    case "recharge-points":
      openModal({
        title: "积分充值",
        description: "选择充值档位即可获得额外赠送积分。",
        confirmText: "确认充值",
        onConfirm: () => {
          const bonus = 300;
          updatePointsBalance(bonus, "积分充值赠送");
          showToast(`充值成功，已到账 ${bonus} 积分`);
        },
      });
      break;
    case "redeem-points":
      openModal({
        title: "兑换礼品",
        description: "本次兑换将扣除 200 积分，确认继续？",
        confirmText: "确认兑换",
        onConfirm: () => {
          const cost = 200;
          const points = loadPoints();
          if (points.balance < cost) {
            showToast("积分不足，快去充值吧！");
            return;
          }
          updatePointsBalance(-cost, "礼品兑换");
          showToast("兑换成功，礼品已加入配送清单。");
        },
      });
      break;
    case "clear-cart":
      openModal({
        title: "清空购物车",
        description: "确认清空所有商品吗？",
        confirmText: "确认清空",
        onConfirm: () => {
          saveCart([]);
          renderRoute("cart");
          showToast("购物车已清空。");
        },
      });
      break;
    case "checkout":
      openModal({
        title: "提交订单",
        description: "预计 30 分钟内送达，确认提交订单吗？",
        confirmText: "确认提交",
        onConfirm: () => {
          saveCart([]);
          renderRoute("orders");
          showToast("订单已提交，配送中。");
        },
      });
      break;
    case "save-cart":
      showToast("购物车已保存，下次打开将自动恢复。");
      break;
    default:
      showToast("功能正在建设中。");
  }
}

function updatePointsBalance(delta, label) {
  const points = loadPoints();
  const nextBalance = Math.max(0, points.balance + delta);
  savePoints({ balance: nextBalance });
  const history = loadPointsHistory();
  const today = new Date();
  const dateLabel = `${today.getMonth() + 1}/${today.getDate()}`;
  const nextHistory = [
    { label: `${dateLabel} ${label}`, value: delta },
    ...history,
  ].slice(0, 6);
  savePointsHistory(nextHistory);
  renderRoute("points");
}

function ensureToastContainer() {
  let container = document.querySelector(".toast-container");
  if (!container) {
    container = document.createElement("div");
    container.className = "toast-container";
    document.body.appendChild(container);
  }
  return container;
}

function showToast(message) {
  const container = ensureToastContainer();
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.textContent = message;
  container.appendChild(toast);
  requestAnimationFrame(() => {
    toast.classList.add("show");
  });
  setTimeout(() => {
    toast.classList.remove("show");
    setTimeout(() => toast.remove(), 300);
  }, 2400);
}

function ensureModal() {
  let modal = document.querySelector(".modal-overlay");
  if (!modal) {
    modal = document.createElement("div");
    modal.className = "modal-overlay";
    modal.innerHTML = `
      <div class="modal-card">
        <h3 class="modal-title"></h3>
        <p class="modal-description"></p>
        <div class="modal-actions">
          <button class="ghost-button" type="button" data-modal-action="cancel">取消</button>
          <button class="action-button" type="button" data-modal-action="confirm">确认</button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);
  }
  return modal;
}

function openModal({ title, description, confirmText, onConfirm }) {
  const modal = ensureModal();
  modal.querySelector(".modal-title").textContent = title;
  modal.querySelector(".modal-description").textContent = description;
  const confirmButton = modal.querySelector('[data-modal-action="confirm"]');
  confirmButton.textContent = confirmText || "确认";
  const cancelButton = modal.querySelector('[data-modal-action="cancel"]');

  const closeModal = () => {
    modal.classList.remove("open");
    confirmButton.removeEventListener("click", onConfirmClick);
    cancelButton.removeEventListener("click", onCancelClick);
  };

  const onConfirmClick = () => {
    if (typeof onConfirm === "function") {
      onConfirm();
    }
    closeModal();
  };

  const onCancelClick = () => closeModal();

  confirmButton.addEventListener("click", onConfirmClick);
  cancelButton.addEventListener("click", onCancelClick);
  modal.addEventListener("click", (event) => {
    if (event.target === modal) {
      closeModal();
    }
  }, { once: true });
  modal.classList.add("open");
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
