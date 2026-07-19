const catalogGrid = document.querySelector("#catalog-grid");

const themeGradients = {
  sendai:
    "linear-gradient(135deg, rgba(30, 90, 122, 0.88), rgba(106, 171, 143, 0.75)), url('https://images.unsplash.com/photo-1493976040374-85c8e9127844?auto=format&fit=crop&w=800&q=80') center / cover",
  peach:
    "linear-gradient(135deg, rgba(155, 45, 48, 0.85), rgba(232, 135, 106, 0.75)), url('https://images.unsplash.com/photo-1578662996442-48f60103fc96?auto=format&fit=crop&w=800&q=80') center / cover",
  aizu: "linear-gradient(135deg, rgba(155, 45, 48, 0.9), rgba(61, 122, 140, 0.8))",
  onsen: "linear-gradient(135deg, rgba(61, 122, 140, 0.85), rgba(47, 93, 74, 0.8))",
};

function createPlanCard(plan) {
  const item = document.createElement("li");
  const link = document.createElement("a");

  item.className = "catalog-item";
  link.className = "plan-card";
  link.href = plan.href;

  const coverStyle = themeGradients[plan.theme] || themeGradients.aizu;
  const tags = (plan.tags || [])
    .map((tag) => `<span class="plan-card__tag">${tag}</span>`)
    .join("");

  link.innerHTML = `
    <div class="plan-card__cover" style="background: ${coverStyle}">
      <p class="plan-card__eyebrow"></p>
      <h2 class="plan-card__title"></h2>
      <p class="plan-card__duration"></p>
    </div>
    <div class="plan-card__body">
      <p class="plan-card__description"></p>
      <div class="plan-card__tags">${tags}</div>
      <span class="plan-card__cta">プランを見る →</span>
    </div>
  `;

  link.querySelector(".plan-card__eyebrow").textContent = plan.eyebrow;
  link.querySelector(".plan-card__title").textContent = plan.title;
  link.querySelector(".plan-card__duration").textContent = plan.duration;
  link.querySelector(".plan-card__description").textContent = plan.description;

  item.append(link);
  return item;
}

async function loadCatalog() {
  if (!catalogGrid) return;

  try {
    const response = await fetch("plans/manifest.json");
    if (!response.ok) throw new Error("manifest not found");

    const { plans } = await response.json();

    if (!plans.length) {
      catalogGrid.innerHTML =
        '<li class="catalog-empty">まだ旅行プランが登録されていません。</li>';
      return;
    }

    catalogGrid.replaceChildren(...plans.map(createPlanCard));
  } catch {
    catalogGrid.innerHTML =
      '<li class="catalog-error">旅行プラン一覧を読み込めませんでした。</li>';
  }
}

loadCatalog();
