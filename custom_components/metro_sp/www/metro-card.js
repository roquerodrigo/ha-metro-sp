/**
 * Metrô SP card — a Lovelace custom card that lists the Metrô SP / CPTM lines
 * exposed by the `metro_sp` integration and shows each line's operation status.
 *
 * Zero-build vanilla web component (no Lit/bundler). Styles are driven entirely
 * by Home Assistant design tokens so the card follows the active theme and
 * light/dark mode automatically. The status dot uses the upstream `status_color`
 * attribute; the line badge uses the line's official `color_hex`.
 *
 * Config:
 *   type: custom:metro-card
 *   entities: [...]             # optional: pick which lines to show (entity ids).
 *                               #   when omitted, every metro_sp line is shown,
 *                               #   sorted by line number.
 *   secondary_info: last-changed  # last-changed | description | none (default last-changed)
 */

const DEFAULT_SECONDARY = "last-changed";

// i18n — pure frontend plugin (no custom_component translations), so strings are
// embedded here and picked by the active HA UI language, falling back to English.
const TRANSLATIONS = {
  en: {
    "card.empty": "No Metrô SP lines found",
    "card.line": "Line",
    "editor.entities": "Lines to show (leave empty for all)",
    "editor.secondary": "Secondary info",
    "editor.secondary_last_changed": "Last changed",
    "editor.secondary_description": "Status description",
    "editor.secondary_none": "None",
  },
  "pt-BR": {
    "card.empty": "Nenhuma linha do Metrô SP encontrada",
    "card.line": "Linha",
    "editor.entities": "Linhas a exibir (vazio = todas)",
    "editor.secondary": "Informação secundária",
    "editor.secondary_last_changed": "Última alteração",
    "editor.secondary_description": "Descrição do status",
    "editor.secondary_none": "Nenhuma",
  },
};

// Maps ha-form field names to their translation keys (for computeLabel).
const EDITOR_LABEL_KEYS = {
  entities: "editor.entities",
  secondary_info: "editor.secondary",
};

/** The active HA UI language, or a supported fallback (base lang, then "en"). */
function resolveLang(hass) {
  const lang = (hass && (hass.locale?.language || hass.language || hass.selectedLanguage)) || "en";
  if (TRANSLATIONS[lang]) return lang;
  if (lang.split("-")[0] === "pt") return "pt-BR";
  return "en";
}

/** Translate a dotted key for the active language; English is the fallback. */
function localize(hass, key) {
  const lang = resolveLang(hass);
  return TRANSLATIONS[lang]?.[key] ?? TRANSLATIONS.en[key] ?? key;
}

/** True for a metro_sp line sensor — identified by its integration attributes. */
function isMetroLine(state) {
  const a = state?.attributes;
  return !!a && a.line_code !== undefined && a.color_hex !== undefined;
}

/** Escape a string for safe interpolation into innerHTML. */
function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]
  );
}

class MetroCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
    this._hass = null;
    this._signature = null;
  }

  static getConfigElement() {
    return document.createElement("metro-card-editor");
  }

  static getStubConfig() {
    return { type: "custom:metro-card", secondary_info: DEFAULT_SECONDARY };
  }

  setConfig(config) {
    const secondary = config.secondary_info ?? DEFAULT_SECONDARY;
    if (!["last-changed", "description", "none"].includes(secondary)) {
      throw new Error('metro-card: "secondary_info" must be "last-changed", "description" or "none"');
    }
    // An empty list (the editor's initial state) means "show all lines", same
    // as omitting the option — otherwise opening the editor would blank the card.
    const entities =
      Array.isArray(config.entities) && config.entities.length
        ? config.entities.map((e) => (typeof e === "string" ? e : e.entity))
        : null;
    this._config = {
      secondaryInfo: secondary,
      entities,
    };
    this._signature = null; // force re-render
    if (this._hass) this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  getCardSize() {
    return 3;
  }

  getGridOptions() {
    return { min_columns: 6, min_rows: 3 };
  }

  /** Discover the metro line sensors to display, sorted by line number. */
  _collect() {
    const hass = this._hass;
    const registry = hass.entities || {};
    let ids;
    if (this._config.entities) {
      ids = this._config.entities;
    } else {
      ids = Object.keys(hass.states).filter((id) => {
        if (!id.startsWith("sensor.")) return false;
        if (!isMetroLine(hass.states[id])) return false;
        if (registry[id] && registry[id].hidden_by) return false;
        return true;
      });
    }

    const items = ids
      .map((id) => {
        const st = hass.states[id];
        if (!st || !isMetroLine(st)) return null;
        const a = st.attributes;
        return {
          id,
          lineCode: a.line_code,
          colorName: a.color_name,
          colorHex: a.color_hex,
          statusColor: a.status_color,
          picture: a.entity_picture,
          description: a.description,
          status: st.state,
          lastChanged: st.last_changed,
        };
      })
      .filter(Boolean);

    items.sort((x, y) => Number(x.lineCode) - Number(y.lineCode));
    return items;
  }

  _render() {
    if (!this._hass) return;
    const hass = this._hass;
    const t = (key) => localize(hass, key);
    const lang = resolveLang(hass);
    const items = this._collect();
    const secondary = this._config.secondaryInfo;

    // Skip a rebuild when nothing visible has changed (avoids flicker).
    const signature = JSON.stringify([
      lang,
      secondary,
      items.map((i) => [i.id, i.status, i.statusColor, i.picture, i.description, i.lastChanged]),
    ]);
    if (signature === this._signature) return;
    this._signature = signature;

    const rows = items
      .map((item) => {
        const badge = item.picture
          ? `<img class="badge" src="${esc(item.picture)}" alt="${esc(item.colorName)}" />`
          : `<span class="badge dot" style="background:${esc(item.colorHex)}">${esc(item.lineCode)}</span>`;
        const secondaryHtml =
          secondary === "description"
            ? `<div class="secondary">${esc(item.description || item.status)}</div>`
            : secondary === "last-changed"
              ? `<div class="secondary"><ha-relative-time class="rt" data-ts="${esc(item.lastChanged)}"></ha-relative-time></div>`
              : "";
        return `
          <div class="row" data-id="${esc(item.id)}">
            ${badge}
            <div class="body">
              <div class="name">${esc(t("card.line"))} ${esc(item.lineCode)} · ${esc(item.colorName)}</div>
              ${secondaryHtml}
            </div>
            <div class="status">
              <span class="status-dot" style="background:${esc(item.statusColor)}"></span>
              <span class="status-label">${esc(item.status)}</span>
            </div>
          </div>`;
      })
      .join("");

    const empty = `<div class="empty"><ha-icon icon="mdi:subway-alert-variant"></ha-icon><span>${t("card.empty")}</span></div>`;

    this.shadowRoot.innerHTML = `
      <style>${MetroCard.styles}</style>
      <ha-card>
        <div class="list">${items.length ? rows : empty}</div>
      </ha-card>`;

    // ha-relative-time is a property-driven element — wire hass + datetime after
    // the string render (it self-refreshes its "x minutes ago" text).
    this.shadowRoot.querySelectorAll(".rt").forEach((el) => {
      el.hass = hass;
      const ts = el.dataset.ts;
      if (ts) el.datetime = new Date(ts);
    });

    this.shadowRoot.querySelectorAll(".row").forEach((row) => {
      row.addEventListener("click", () => this._showMore(row.dataset.id));
    });
  }

  /** Open the more-info dialog for an entity (standard HA behaviour). */
  _showMore(entityId) {
    this.dispatchEvent(
      new CustomEvent("hass-more-info", { detail: { entityId }, bubbles: true, composed: true })
    );
  }

  static get styles() {
    return `
      :host { display: block; }
      ha-card { padding: 8px; }
      .list { display: flex; flex-direction: column; }
      .row {
        display: flex;
        align-items: center;
        gap: 14px;
        cursor: pointer;
        padding: 10px 12px;
        min-height: 40px;
        border-radius: 12px;
        transition: background .2s ease;
      }
      .row:hover { background: var(--secondary-background-color); }
      .badge {
        flex: 0 0 auto;
        width: 34px;
        height: 34px;
        border-radius: 8px;
        object-fit: contain;
      }
      .badge.dot {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        color: #fff;
        font-weight: 700;
        font-size: 0.95rem;
        text-shadow: 0 1px 2px rgba(0,0,0,.35);
      }
      .body { flex: 1 1 auto; min-width: 0; }
      .name {
        color: var(--primary-text-color);
        font-size: 1.05rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
      .secondary {
        color: var(--secondary-text-color);
        font-size: 0.8125rem;
        margin-top: 2px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
      .status {
        flex: 0 0 auto;
        display: flex;
        align-items: center;
        gap: 8px;
        max-width: 45%;
      }
      .status-dot {
        flex: 0 0 auto;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        box-shadow: 0 0 0 2px var(--ha-card-background, var(--card-background-color, #fff));
      }
      .status-label {
        color: var(--primary-text-color);
        font-size: 0.95rem;
        text-align: right;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
      .empty {
        display: flex;
        align-items: center;
        gap: 8px;
        color: var(--secondary-text-color);
        padding: 16px 12px;
      }
    `;
  }
}

class MetroCardEditor extends HTMLElement {
  constructor() {
    super();
    this._config = {};
    this._hass = null;
  }

  setConfig(config) {
    this._config = config;
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  /** Build the ha-form schema with option labels in the active language. */
  _schema() {
    const t = (key) => localize(this._hass, key);
    return [
      {
        name: "entities",
        selector: {
          entity: {
            multiple: true,
            filter: { integration: "metro_sp", domain: "sensor" },
          },
        },
      },
      {
        name: "secondary_info",
        selector: {
          select: {
            mode: "dropdown",
            options: [
              { value: "last-changed", label: t("editor.secondary_last_changed") },
              { value: "description", label: t("editor.secondary_description") },
              { value: "none", label: t("editor.secondary_none") },
            ],
          },
        },
      },
    ];
  }

  _labels(schema) {
    return localize(this._hass, EDITOR_LABEL_KEYS[schema.name] ?? schema.name);
  }

  _render() {
    if (!this._hass) return;
    if (!this._form) {
      this._form = document.createElement("ha-form");
      this._form.computeLabel = (schema) => this._labels(schema);
      this._form.addEventListener("value-changed", (ev) => {
        const config = { type: "custom:metro-card", ...ev.detail.value };
        this.dispatchEvent(
          new CustomEvent("config-changed", { detail: { config }, bubbles: true, composed: true })
        );
      });
      this.appendChild(this._form);
    }
    this._form.hass = this._hass;
    this._form.schema = this._schema();
    this._form.data = {
      entities: this._config.entities ?? [],
      secondary_info: this._config.secondary_info ?? DEFAULT_SECONDARY,
    };
  }
}

customElements.define("metro-card", MetroCard);
customElements.define("metro-card-editor", MetroCardEditor);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "metro-card",
  name: "Metrô SP Card",
  description: "Lists the Metrô SP / CPTM lines and their operation status.",
  preview: true,
  documentationURL: "https://github.com/roquerodrigo/ha-metro-sp",
});

// eslint-disable-next-line no-console
console.info("%c metro-card ", "background:#0455A1;color:#fff;border-radius:3px", "loaded");
