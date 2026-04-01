const PAGE_SIZE = 4;

const userInfo = (() => {
  try {
    return JSON.parse(localStorage.getItem("user")) || null;
  } catch (e) {
    return null;
  }
})();

const token = localStorage.getItem("token") || "";

const costumes = [];
let ownedOutfitIds = new Set();
let currentSelectedId = null;
let pendingCostume = null;
let pendingAction = null;
let currentPage = 0;

const getImageUrl = (id) => `/static/outfits/${id}.png`;

const request = async (url, options = {}) => {
  const headers = options.headers || {};
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  const res = await fetch(url, {
    ...options,
    headers,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "请求失败");
  }
  return res.json();
};

const pointStage = document.getElementById("pointStage");
const costumeGrid = document.getElementById("costumeGrid");
const mainCharacter = document.getElementById("mainCharacter");
const pageIndicator = document.getElementById("pageIndicator");
const pageToggleButton = document.getElementById("pageToggleButton");
const confirmModal = document.getElementById("confirmModal");
const cancelExchange = document.getElementById("cancelExchange");
const confirmExchange = document.getElementById("confirmExchange");
const confirmText = document.querySelector(".confirm-text");
const userNameEl = document.querySelector(".user-name");
const currentScoreEl = document.getElementById("currentScore");

function syncEquippedAvatar(outfitId) {
  const avatarUrl = outfitId ? getImageUrl(outfitId) : "";
  if (outfitId) {
    localStorage.setItem("equippedAvatarId", String(outfitId));
  } else {
    localStorage.removeItem("equippedAvatarId");
  }
  if (avatarUrl) {
    localStorage.setItem("equippedAvatarUrl", avatarUrl);
  } else {
    localStorage.removeItem("equippedAvatarUrl");
  }
}

function updateStageScale() {
  if (!pointStage) return;
  const designWidth = 1024;
  const designHeight = 580;
  const scale = Math.min(
    window.innerWidth / designWidth,
    window.innerHeight / designHeight
  ) * 0.9;
  pointStage.style.setProperty("--scale", String(scale));
}

function renderPage() {
  costumeGrid.innerHTML = "";

  const start = currentPage * PAGE_SIZE;
  const pageItems = costumes.slice(start, start + PAGE_SIZE);

  pageItems.forEach((item) => {
    const card = document.createElement("div");
    card.className = "costume-card";
    if (item.id === currentSelectedId) {
      card.classList.add("selected");
    }

    const frame = document.createElement("div");
    frame.className = "costume-frame";

    const img = document.createElement("img");
    img.className = "costume-image";
    img.src = item.image;
    img.alt = item.name || "形象";

    const name = document.createElement("div");
    name.className = "costume-name";
    name.textContent = item.name || `形象${item.id}`;

    if (ownedOutfitIds.has(item.id)) {
      card.classList.add("owned");
      const badge = document.createElement("div");
      badge.className = "badge";
      badge.textContent = "已拥有";
      frame.appendChild(badge);
    } else if (item.price !== undefined) {
      const priceTag = document.createElement("div");
      priceTag.className = "price-tag";
      priceTag.textContent = `${item.price}积分`;
      frame.appendChild(priceTag);
    }

    frame.appendChild(img);
    card.appendChild(frame);
    card.appendChild(name);

    card.addEventListener("click", () => {
      pendingCostume = item;
      openConfirmDialog();
    });

    costumeGrid.appendChild(card);
  });

  const totalPages = Math.ceil(costumes.length / PAGE_SIZE) || 1;
  pageIndicator.textContent = `${currentPage + 1}/${totalPages}`;
  pageToggleButton.textContent = currentPage === 0 ? "下一页" : "上一页";
}

function openConfirmDialog() {
  if (!pendingCostume || !confirmText) return;
  if (ownedOutfitIds.has(pendingCostume.id)) {
    pendingAction = "equip";
    confirmText.textContent = "确定切换到该形象吗？";
  } else {
    pendingAction = "redeem";
    confirmText.textContent = `确定花费${pendingCostume.price || 0}积分兑换该套装吗？`;
  }
  confirmModal.classList.remove("hidden");
}

function closeConfirmDialog() {
  confirmModal.classList.add("hidden");
}

pageToggleButton.addEventListener("click", () => {
  const totalPages = Math.ceil(costumes.length / PAGE_SIZE) || 1;
  currentPage = (currentPage + 1) % totalPages;
  renderPage();
});

cancelExchange.addEventListener("click", () => {
  pendingCostume = null;
  pendingAction = null;
  closeConfirmDialog();
});

confirmExchange.addEventListener("click", async () => {
  if (!pendingCostume || !userInfo?.id) {
    closeConfirmDialog();
    return;
  }

  try {
    if (pendingAction === "redeem") {
      await request("/shop/redeem", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: userInfo.id,
          outfit_id: pendingCostume.id,
        }),
      });
      ownedOutfitIds.add(pendingCostume.id);
    }

    await request("/shop/equip", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: userInfo.id,
        outfit_id: pendingCostume.id,
      }),
    });

    currentSelectedId = pendingCostume.id;
    mainCharacter.src = pendingCostume.image;
    syncEquippedAvatar(currentSelectedId);
    await refreshUserPoints();
    await refreshOwnedItems();
    renderPage();
  } catch (e) {
    alert(e.message || "操作失败");
  } finally {
    pendingCostume = null;
    pendingAction = null;
    closeConfirmDialog();
  }
});

async function refreshUserPoints() {
  if (!userInfo?.id) return;
  try {
    const res = await request(`/user/api/points/${userInfo.id}`);
    if (currentScoreEl && res?.data?.total_points !== undefined) {
      currentScoreEl.textContent = String(res.data.total_points).padStart(2, "0");
    }
  } catch (e) {
    console.error(e);
  }
}

async function refreshOwnedItems() {
  if (!userInfo?.id) return;
  const ownedRes = await request(`/shop/user-items?user_id=${userInfo?.id || ""}`);
  const owned = ownedRes?.data || [];
  ownedOutfitIds = new Set(owned.map((it) => it.id));
}

async function initPage() {
  if (userNameEl) {
    userNameEl.textContent = userInfo?.username || "游客";
  }
  await refreshUserPoints();

  try {
    const itemsRes = await request("/shop/items");
    const items = itemsRes?.data || [];
    costumes.splice(0, costumes.length, ...items.map((item) => ({
      ...item,
      image: getImageUrl(item.id),
    })));

    await refreshOwnedItems();

    const currentRes = await request(`/shop/current-avatar?user_id=${userInfo?.id || ""}`);
    const current = currentRes?.data || null;
    if (current?.id) {
      currentSelectedId = current.id;
      mainCharacter.src = getImageUrl(current.id);
      syncEquippedAvatar(currentSelectedId);
    } else if (costumes.length > 0) {
      currentSelectedId = costumes[0].id;
      mainCharacter.src = costumes[0].image;
      syncEquippedAvatar(currentSelectedId);
    }

    renderPage();
  } catch (e) {
    alert(e.message || "加载失败");
  }
}

// 初始渲染
updateStageScale();
initPage();

window.addEventListener("resize", updateStageScale);

