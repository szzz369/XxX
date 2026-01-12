const templates = {
  home: document.querySelector("#home-template"),
  cart: document.querySelector("#cart-template"),
  order: document.querySelector("#order-template"),
  points: document.querySelector("#points-template"),
  "after-sale": document.querySelector("#after-sale-template"),
};

const titles = {
  home: "首页",
  cart: "购物车",
  order: "订单详情",
  points: "积分中心",
  "after-sale": "售后服务",
};

const cartStorageKey = "demo-cart";

const defaultCart = [
  { id: 1, name: "轻薄羽绒服", price: 399, quantity: 1 },
  { id: 2, name: "智能运动手环", price: 299, quantity: 2 },
];

const pointsFlow = [
  { id: 1, label: "购物奖励", points: "+120", time: "2024-09-18 18:30" },
  { id: 2, label: "兑换优惠券", points: "-80", time: "2024-09-17 09:42" },
  { id: 3, label: "签到积分", points: "+20", time: "2024-09-16 07:10" },
];

const view = document.querySelector("#view");
const pageTitle = document.querySelector("#page-title");
const tabs = document.querySelectorAll(".tab");

const loadCart = () => {
  const stored = window.localStorage.getItem(cartStorageKey);
  if (!stored) {
    window.localStorage.setItem(cartStorageKey, JSON.stringify(defaultCart));
    return [...defaultCart];
  }
  try {
    return JSON.parse(stored);
  } catch (error) {
    window.localStorage.setItem(cartStorageKey, JSON.stringify(defaultCart));
    return [...defaultCart];
  }
};

const saveCart = (cart) => {
  window.localStorage.setItem(cartStorageKey, JSON.stringify(cart));
};

const formatPrice = (value) => `¥${value.toFixed(2)}`;

const renderCart = (root) => {
  const cartItems = root.querySelector("#cart-items");
  const totalNode = root.querySelector("#cart-total");
  const checkoutBtn = root.querySelector("#checkout");

  let cart = loadCart();

  const updateView = () => {
    cartItems.innerHTML = "";
    let total = 0;

    cart.forEach((item) => {
      total += item.price * item.quantity;
      const row = document.createElement("div");
      row.className = "cart-item";
      row.innerHTML = `
        <div>
          <h4>${item.name}</h4>
          <span>${formatPrice(item.price)} / 件</span>
        </div>
        <div class="quantity">
          <button data-action="decrease" aria-label="减少数量">-</button>
          <strong>${item.quantity}</strong>
          <button data-action="increase" aria-label="增加数量">+</button>
        </div>
      `;

      row.querySelectorAll("button").forEach((button) => {
        button.addEventListener("click", () => {
          const action = button.dataset.action;
          if (action === "increase") {
            item.quantity += 1;
          }
          if (action === "decrease") {
            item.quantity = Math.max(0, item.quantity - 1);
          }
          cart = cart.filter((entry) => entry.quantity > 0);
          if (cart.length === 0) {
            cart = [...defaultCart];
          }
          saveCart(cart);
          updateView();
        });
      });

      cartItems.appendChild(row);
    });

    totalNode.textContent = formatPrice(total);
  };

  checkoutBtn.addEventListener("click", () => {
    alert("已为你跳转到结算页（示例）");
  });

  updateView();
};

const renderPoints = (root) => {
  const list = root.querySelector("#points-history");
  list.innerHTML = "";
  pointsFlow.forEach((item) => {
    const li = document.createElement("li");
    li.innerHTML = `
      <div>
        <strong>${item.label}</strong>
        <span>${item.time}</span>
      </div>
      <strong>${item.points}</strong>
    `;
    list.appendChild(li);
  });

  const recharge = root.querySelector("#points-recharge");
  recharge.addEventListener("click", () => {
    alert("积分充值入口已打开（示例）");
  });
};

const renderRoute = () => {
  const route = window.location.hash.replace("#/", "") || "home";
  const template = templates[route] || templates.home;
  view.innerHTML = "";
  view.appendChild(template.content.cloneNode(true));

  const title = titles[route] || titles.home;
  pageTitle.textContent = title;

  tabs.forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.route === route);
  });

  if (route === "cart") {
    renderCart(view);
  }

  if (route === "points") {
    renderPoints(view);
  }
};

window.addEventListener("hashchange", renderRoute);
window.addEventListener("DOMContentLoaded", () => {
  if (!window.location.hash) {
    window.location.hash = "#/home";
  }
  renderRoute();
});
