/* Global demand radar: dark Leaflet basemap + custom pulsing markers
   sized by listing volume, colored by trend score (cold -> hot). */
(function () {
  const map = L.map("world-map", {
    center: [20, 10],
    zoom: 2,
    minZoom: 1.5,
    maxZoom: 6,
    worldCopyJump: true,
    zoomControl: true,
    attributionControl: false,
  });

  L.tileLayer(
    "https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png",
    { subdomains: "abcd", maxZoom: 10 }
  ).addTo(map);

  let markers = [];

  function colorForTrend(t) {
    if (t >= 75) return "#22D3B8"; // hot
    if (t >= 45) return "#FBBF24"; // rising
    return "#475569"; // low
  }

  function radiusForVolume(count) {
    return Math.max(7, Math.min(26, 6 + count * 1.4));
  }

  function buildIcon(country) {
    const color = colorForTrend(country.trend_score);
    const r = radiusForVolume(country.listing_count);
    const ring = country.trend_score >= 70
      ? `<div class="pulse-ring" style="width:${r * 1.6}px;height:${r * 1.6}px;background:${color}33;border:1px solid ${color};"></div>`
      : "";
    const html = `
      <div class="pulse-marker" style="width:${r * 2.6}px;height:${r * 2.6}px;">
        ${ring}
        <div class="pulse-core" style="width:${r}px;height:${r}px;background:${color};box-shadow:0 0 ${r}px ${color}99;"></div>
      </div>`;
    return L.divIcon({ html, className: "", iconSize: [r * 2.6, r * 2.6] });
  }

  function render(countries) {
    markers.forEach((m) => map.removeLayer(m));
    markers = [];
    countries.forEach((c) => {
      const marker = L.marker([c.lat, c.lng], { icon: buildIcon(c) });
      marker.bindPopup(`
        <div class="map-popup">
          <div class="name">${c.name}</div>
          <div class="row"><span>Trend score</span><b>${c.trend_score}</b></div>
          <div class="row"><span>Listings tracked</span><b>${c.listing_count}</b></div>
          <div class="row"><span>Avg rating</span><b>${c.avg_rating}★</b></div>
          <div class="row"><span>Units sold (30d)</span><b>${c.total_sales.toLocaleString()}</b></div>
        </div>`);
      marker.addTo(map);
      markers.push(marker);
    });
  }

  async function poll() {
    try {
      const res = await fetch("/api/countries");
      const data = await res.json();
      render(data.countries);
      const el = document.getElementById("map-updated");
      if (el) el.textContent = "updated " + new Date(data.updated_at + "Z").toLocaleTimeString();
    } catch (e) {
      console.error("map poll failed", e);
    }
  }

  poll();
  setInterval(poll, 6000);
})();
