(function () {
  const searchInput = document.getElementById("search-input");
  const searchShell = document.getElementById("search-shell");
  const grid = document.getElementById("product-grid");
  const resultCount = document.getElementById("result-count");
  const fMarketplace = document.getElementById("f-marketplace");
  const fSort = document.getElementById("f-sort");

  const MKT_ICON = {
    "Amazon": "📦", "eBay": "🏷️", "TikTok Shop": "🎵",
    "AliExpress": "🚀", "Alibaba": "🏭",
  };

  let debounceTimer = null;
  let activeController = null;

  function debouncedSearch() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(runSearch, 220);
  }

  async function runSearch() {
    if (activeController) activeController.abort();
    activeController = new AbortController();
    searchShell.classList.add("loading");

    const params = new URLSearchParams({
      q: searchInput.value.trim(),
      marketplace: fMarketplace.value,
      sort: fSort.value,
    });

    try {
      const res = await fetch("/api/search?" + params.toString(), { signal: activeController.signal });
      const data = await res.json();
      renderResults(data);
    } catch (e) {
      if (e.name !== "AbortError") console.error(e);
    } finally {
      searchShell.classList.remove("loading");
    }
  }

  function renderResults(data) {
    resultCount.textContent = `${data.count} result${data.count === 1 ? "" : "s"}`;
    if (!data.results.length) {
      grid.innerHTML = `<div class="empty-state" style="grid-column:1/-1;">
          <div class="big">¯\\_(ツ)_/¯</div>
          No products match that search yet. Try a broader term.
        </div>`;
      return;
    }
    grid.innerHTML = data.results.map(cardHtml).join("");
  }

  function cardHtml(p) {
    const icon = MKT_ICON[p.marketplace] || "🛒";
    const trendColor = p.trend_score >= 75 ? "var(--teal)" : p.trend_score >= 45 ? "var(--amber)" : "var(--text-faint)";
    return `
      <div class="product-card">
        <div class="card-top">
          <div class="card-icon" style="background:${p.accent}22;color:${p.accent};">${icon}</div>
          <span class="mkt-badge">${p.marketplace}</span>
        </div>
        <h4>${escapeHtml(p.title)}</h4>
        <div class="card-meta">
          <span>${p.category}</span>
          <span class="price">$${p.price.toFixed(2)}</span>
        </div>
        <div class="trend-bar-wrap"><div class="trend-bar-fill" style="width:${p.trend_score}%;background:${trendColor};"></div></div>
        <div class="card-stats">
          <span>★ <b>${p.rating}</b></span>
          <span><b>${p.units_sold_30d.toLocaleString()}</b> sold/30d</span>
          <span><b>${p.country_name}</b></span>
        </div>
      </div>`;
  }

  function escapeHtml(s) {
    const d = document.createElement("div");
    d.textContent = s;
    return d.innerHTML;
  }

  searchInput.addEventListener("input", debouncedSearch);
  fMarketplace.addEventListener("change", runSearch);
  fSort.addEventListener("change", runSearch);

  // ---- stats tiles ----
  async function loadStats() {
    try {
      const res = await fetch("/api/stats");
      const s = await res.json();
      document.getElementById("stat-products").textContent = s.total_products;
      document.getElementById("stat-trend").textContent = s.avg_trend;
      document.getElementById("stat-sales").textContent = s.total_sales.toLocaleString();
      document.getElementById("stat-countries").textContent = s.active_countries;
    } catch (e) { console.error(e); }
  }

  // ---- trending sidebar ----
  async function loadTrending() {
    try {
      const res = await fetch("/api/trending");
      const data = await res.json();
      const list = document.getElementById("trend-list");
      list.innerHTML = data.results.map((p, i) => `
        <div class="trend-row">
          <span class="rank">${i + 1}</span>
          <span class="swatch-dot" style="background:${p.accent};"></span>
          <div class="info">
            <div class="ttitle">${escapeHtml(p.title)}</div>
            <div class="tmeta">${p.marketplace} · ${p.country_name}</div>
          </div>
          <div class="tscore">${p.trend_score}</div>
        </div>`).join("");
    } catch (e) { console.error(e); }
  }

  loadStats();
  loadTrending();
  runSearch();
  setInterval(loadStats, 8000);
  setInterval(loadTrending, 8000);
})();
