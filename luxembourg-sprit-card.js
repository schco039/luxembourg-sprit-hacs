/**
 * Luxembourg Spritpreise – Custom Lovelace Card
 * Zeigt SP95 Preis, Trend, Differenz, Tankkosten und Preisverlauf
 */

class LuxembourgSpritCard extends HTMLElement {
  set hass(hass) {
    if (!this.content) {
      this.innerHTML = `<ha-card></ha-card>`;
      this.card = this.querySelector("ha-card");
      this.content = document.createElement("div");
      this.card.appendChild(this.content);
    }

    const config = this._config;
    if (!config) return;

    const entityId = config.entity;
    const stateObj = hass.states[entityId];

    if (!stateObj) {
      this.content.innerHTML = `<div style="padding:16px;color:var(--error-color)">
        Entity <b>${entityId}</b> nicht gefunden.
      </div>`;
      return;
    }

    const attr = stateObj.attributes;
    const price = attr.price;
    const prev = attr.previous_price;
    const diff = attr.diff;
    const diffPct = attr.diff_pct;
    const tankCost = attr.tank_cost;
    const tankDiff = attr.tank_diff;
    const trend = attr.trend || "unknown";
    const vehicleName = attr.vehicle_name || config.title || "Fahrzeug";
    const tankSize = attr.tank_size || "?";
    const articleTitle = attr.article_title || "";
    const articleLink = attr.article_link || "#";
    const articleDate = attr.article_date || "";
    const lastCheck = attr.last_check || "";

    // Trend styling
    const trendConfig = {
      rising:  { icon: "mdi:trending-up",   color: "#e74c3c", label: "wird teurer",   emoji: "🔴", advice: "👉 Heute noch tanken!" },
      falling: { icon: "mdi:trending-down",  color: "#27ae60", label: "wird günstiger", emoji: "🟢", advice: "💡 Morgen tanken!" },
      stable:  { icon: "mdi:trending-neutral", color: "#f39c12", label: "stabil",       emoji: "🟡", advice: "" },
      unknown: { icon: "mdi:help-circle",    color: "#95a5a6", label: "unbekannt",     emoji: "⚪", advice: "" },
    };
    const t = trendConfig[trend] || trendConfig.unknown;

    const fmt = (v, dec = 3) => v !== null && v !== undefined ? Number(v).toFixed(dec) : "–";
    const fmtDiff = (v, dec = 3) => {
      if (v === null || v === undefined) return "–";
      const sign = v > 0 ? "+" : "";
      return `${sign}${Number(v).toFixed(dec)}`;
    };

    // Format last check
    let checkStr = "";
    if (lastCheck) {
      try {
        checkStr = new Date(lastCheck).toLocaleString("de-DE", { hour: "2-digit", minute: "2-digit", day: "2-digit", month: "2-digit" });
      } catch { checkStr = lastCheck; }
    }

    this.content.innerHTML = `
      <style>
        .sprit-card { font-family: var(--paper-font-body1_-_font-family); padding: 16px; }
        .sprit-header { display: flex; align-items: center; gap: 10px; margin-bottom: 16px; }
        .sprit-header-icon { font-size: 28px; }
        .sprit-header-text h2 { margin: 0; font-size: 1.1em; font-weight: 600; color: var(--primary-text-color); }
        .sprit-header-text p  { margin: 2px 0 0; font-size: 0.8em; color: var(--secondary-text-color); }
        .sprit-trend-badge {
          display: inline-flex; align-items: center; gap: 6px;
          padding: 4px 12px; border-radius: 20px; font-size: 0.85em; font-weight: 600;
          background: ${t.color}22; color: ${t.color}; margin-bottom: 14px;
        }
        .sprit-main { display: flex; align-items: baseline; gap: 8px; margin-bottom: 4px; }
        .sprit-price { font-size: 2.8em; font-weight: 700; color: var(--primary-text-color); }
        .sprit-unit  { font-size: 1em; color: var(--secondary-text-color); }
        .sprit-diff  { font-size: 1em; font-weight: 600; color: ${t.color}; }
        .sprit-grid  {
          display: grid; grid-template-columns: 1fr 1fr;
          gap: 10px; margin: 14px 0;
        }
        .sprit-tile  {
          background: var(--secondary-background-color);
          border-radius: 10px; padding: 10px 12px;
        }
        .sprit-tile-label { font-size: 0.73em; color: var(--secondary-text-color); text-transform: uppercase; letter-spacing: 0.05em; }
        .sprit-tile-value { font-size: 1.3em; font-weight: 600; color: var(--primary-text-color); margin-top: 2px; }
        .sprit-tile-sub   { font-size: 0.8em; color: ${t.color}; font-weight: 500; }
        .sprit-advice { text-align: center; font-size: 0.9em; font-weight: 600; color: ${t.color}; margin: 6px 0 12px; }
        .sprit-article {
          background: var(--secondary-background-color);
          border-radius: 8px; padding: 10px 12px; margin-top: 4px;
        }
        .sprit-article a { color: var(--primary-color); text-decoration: none; font-size: 0.82em; }
        .sprit-article-date { font-size: 0.75em; color: var(--secondary-text-color); margin-top: 3px; }
        .sprit-footer { font-size: 0.72em; color: var(--disabled-text-color); margin-top: 10px; text-align: right; }
        .sprit-divider { border: none; border-top: 1px solid var(--divider-color); margin: 12px 0; }
      </style>
      <div class="sprit-card">

        <div class="sprit-header">
          <div class="sprit-header-icon">⛽</div>
          <div class="sprit-header-text">
            <h2>Super 95 – ${vehicleName}</h2>
            <p>Luxemburg · Staatlicher Festpreis</p>
          </div>
        </div>

        <div class="sprit-trend-badge">
          ${t.emoji} SP95 ${t.label}
        </div>

        <div class="sprit-main">
          <span class="sprit-price">${fmt(price)}</span>
          <span class="sprit-unit">€/L</span>
          ${diff !== null ? `<span class="sprit-diff">(${fmtDiff(diff)} €)</span>` : ""}
        </div>
        ${diffPct !== null ? `<div style="font-size:0.85em;color:var(--secondary-text-color);margin-bottom:4px">
          Vortag: ${fmt(prev)} €/L &nbsp;|&nbsp; ${fmtDiff(diffPct, 1)} %
        </div>` : ""}

        ${t.advice ? `<div class="sprit-advice">${t.advice}</div>` : ""}

        <div class="sprit-grid">
          <div class="sprit-tile">
            <div class="sprit-tile-label">Volltank (${tankSize} L)</div>
            <div class="sprit-tile-value">${fmt(tankCost, 2)} €</div>
            ${tankDiff !== null ? `<div class="sprit-tile-sub">${fmtDiff(tankDiff, 2)} € zum Vortag</div>` : ""}
          </div>
          <div class="sprit-tile">
            <div class="sprit-tile-label">Änderung</div>
            <div class="sprit-tile-value" style="color:${t.color}">${fmtDiff(diff)} €/L</div>
            <div class="sprit-tile-sub">${fmtDiff(diffPct, 1)} %</div>
          </div>
        </div>

        <hr class="sprit-divider">

        ${articleTitle ? `
        <div class="sprit-article">
          <a href="${articleLink}" target="_blank">📰 ${articleTitle}</a>
          <div class="sprit-article-date">📅 ${articleDate}</div>
        </div>` : ""}

        <div class="sprit-footer">Zuletzt geprüft: ${checkStr} · lesfrontaliers.lu</div>
      </div>
    `;
  }

  setConfig(config) {
    if (!config.entity) throw new Error("'entity' ist erforderlich");
    this._config = config;
  }

  getCardSize() { return 4; }

  static getConfigElement() {
    return document.createElement("luxembourg-sprit-card-editor");
  }

  static getStubConfig() {
    return { entity: "sensor.sp95_preis" };
  }
}

customElements.define("luxembourg-sprit-card", LuxembourgSpritCard);

// Register with HACS card picker
window.customCards = window.customCards || [];
window.customCards.push({
  type: "luxembourg-sprit-card",
  name: "Luxembourg Spritpreise",
  description: "Zeigt den aktuellen SP95 Preis in Luxemburg mit Trend, Differenz und Tankkosten.",
  preview: true,
});
