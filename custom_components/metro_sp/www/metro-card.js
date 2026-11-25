const CARD_TYPE = "metro-card";
const EDITOR_TYPE = "metro-card-editor";
const INTEGRATION_DOMAIN = "metro_sp";
const DEFAULT_SECONDARY = "last-changed";
const SECONDARY_OPTIONS = ["last-changed", "description", "none"];

const TRANSLATIONS = {
  en: {
    "card.empty": "No Metrô SP lines found",
    "card.line": "Line",
    "editor.entities": "Lines to show (leave empty for all)",
    "editor.secondary_info": "Secondary info",
    "editor.secondary_info_last-changed": "Last changed",
    "editor.secondary_info_description": "Status description",
    "editor.secondary_info_none": "None",
  },
  "pt-BR": {
    "card.empty": "Nenhuma linha do Metrô SP encontrada",
    "card.line": "Linha",
    "editor.entities": "Linhas a exibir (vazio = todas)",
    "editor.secondary_info": "Informação secundária",
    "editor.secondary_info_last-changed": "Última alteração",
    "editor.secondary_info_description": "Descrição do status",
    "editor.secondary_info_none": "Nenhuma",
  },
};

const STATUS_COLOR_FALLBACK = "var(--disabled-color)";

// A origem envia o nome da cor em pt-BR, que o CSS não reconhece.
const STATUS_COLORS = {
  verde: "var(--green-color)",
  amarelo: "var(--amber-color)",
  amarela: "var(--amber-color)",
  laranja: "var(--orange-color)",
  vermelho: "var(--red-color)",
  vermelha: "var(--red-color)",
  lavanda: "var(--purple-color)",
  roxo: "var(--purple-color)",
  azul: "var(--blue-color)",
  cinza: "var(--grey-color)",
};

const resolveLanguage = (hass) => {
  const language =
    (hass && (hass.locale?.language || hass.language || hass.selectedLanguage)) || "en";
  if (TRANSLATIONS[language]) return language;
  if (language.split("-")[0] === "pt") return "pt-BR";
  return "en";
};

const localize = (hass, key) =>
  TRANSLATIONS[resolveLanguage(hass)]?.[key] ?? TRANSLATIONS.en[key] ?? key;

const escapeHtml = (value) =>
  String(value ?? "").replace(
    /[&<>"']/g,
    (character) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[character],
  );

const statusColor = (sourceColor) => {
  const value = String(sourceColor ?? "").trim();
  const known = STATUS_COLORS[value.toLowerCase()];
  if (known) return known;
  if (value && globalThis.CSS?.supports?.("color", value)) return value;
  return STATUS_COLOR_FALLBACK;
};

const isMetroLine = (state) =>
  state?.attributes?.line_code !== undefined && state.attributes.color_hex !== undefined;

class MetroCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
    this._hass = null;
    this._signature = null;
  }

  static getConfigElement() {
    return document.createElement(EDITOR_TYPE);
  }

  static getStubConfig() {
    return { secondary_info: DEFAULT_SECONDARY };
  }

  setConfig(config) {
    const secondary = config.secondary_info ?? DEFAULT_SECONDARY;
    if (!SECONDARY_OPTIONS.includes(secondary)) {
      throw new Error(`${CARD_TYPE}: "secondary_info" must be one of ${SECONDARY_OPTIONS.join(", ")}`);
    }
    // Uma lista vazia (o estado inicial do editor) significa "mostrar todas as
    // linhas", como omitir a opção — do contrário, abrir o editor esvaziaria o card.
    const entities =
      Array.isArray(config.entities) && config.entities.length
        ? config.entities.map((entity) => (typeof entity === "string" ? entity : entity.entity))
        : null;
    this._config = { secondaryInfo: secondary, entities };
    this._signature = null;
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

  _lines() {
    const hass = this._hass;
    const registry = hass.entities || {};
    const entityIds =
      this._config.entities ??
      Object.keys(hass.states).filter(
        (entityId) =>
          entityId.startsWith("sensor.") &&
          isMetroLine(hass.states[entityId]) &&
          !registry[entityId]?.hidden,
      );

    return entityIds
      .map((entityId) => hass.states[entityId])
      .filter(isMetroLine)
      .map((state) => ({
        entityId: state.entity_id,
        lineCode: state.attributes.line_code,
        colorName: state.attributes.color_name,
        colorHex: state.attributes.color_hex,
        statusColor: state.attributes.status_color,
        picture: state.attributes.entity_picture,
        description: state.attributes.description,
        status: hass.formatEntityState(state),
        lastChanged: state.last_changed,
      }))
      .sort((left, right) => Number(left.lineCode) - Number(right.lineCode));
  }

  _render() {
    if (!this._hass) return;
    const hass = this._hass;
    const lines = this._lines();

    const signature = JSON.stringify([
      resolveLanguage(hass),
      this._config.secondaryInfo,
      lines.map((line) => [
        line.entityId,
        line.status,
        line.statusColor,
        line.picture,
        line.description,
        line.lastChanged,
      ]),
    ]);
    if (signature === this._signature) return;
    this._signature = signature;

    const empty = `
      <div class="empty">
        <ha-icon icon="mdi:subway-alert-variant"></ha-icon>
        <span>${escapeHtml(localize(hass, "card.empty"))}</span>
      </div>`;

    this.shadowRoot.innerHTML = `
      <style>${MetroCard.styles}</style>
      <ha-card>
        <div class="lines">${lines.length ? lines.map((line) => this._renderLine(line)).join("") : empty}</div>
      </ha-card>`;

    this.shadowRoot.querySelectorAll("ha-relative-time").forEach((element) => {
      element.hass = hass;
      element.datetime = new Date(element.dataset.datetime);
    });

    this.shadowRoot.querySelectorAll(".line").forEach((element) => {
      element.addEventListener("click", () => this._showMoreInfo(element.dataset.entity));
      element.addEventListener("keydown", (event) => {
        if (event.key !== "Enter" && event.key !== " ") return;
        event.preventDefault();
        this._showMoreInfo(element.dataset.entity);
      });
    });
  }

  _renderLine(line) {
    const name = `${localize(this._hass, "card.line")} ${line.lineCode} · ${line.colorName}`;
    const icon = line.picture
      ? `<ha-tile-icon image-url="${escapeHtml(line.picture)}"></ha-tile-icon>`
      : `<ha-tile-icon style="--tile-icon-color: ${escapeHtml(line.colorHex)}">
          <span slot="icon" class="line-code">${escapeHtml(line.lineCode)}</span>
        </ha-tile-icon>`;

    let secondary = "";
    if (this._config.secondaryInfo === "description") {
      const description = line.description || line.status;
      secondary = `<span slot="secondary" title="${escapeHtml(description)}">${escapeHtml(description)}</span>`;
    } else if (this._config.secondaryInfo === "last-changed" && line.lastChanged) {
      secondary = `<ha-relative-time slot="secondary" data-datetime="${escapeHtml(line.lastChanged)}"></ha-relative-time>`;
    }

    return `
      <div
        class="line"
        data-entity="${escapeHtml(line.entityId)}"
        role="button"
        tabindex="0"
        aria-label="${escapeHtml(`${name}: ${line.status}`)}"
      >
        <ha-ripple></ha-ripple>
        ${icon}
        <ha-tile-info primary="${escapeHtml(name)}">${secondary}</ha-tile-info>
        <ha-badge class="status" style="--badge-color: ${escapeHtml(statusColor(line.statusColor))}">
          <ha-icon slot="icon" icon="mdi:circle"></ha-icon>
          ${escapeHtml(line.status)}
        </ha-badge>
      </div>`;
  }

  _showMoreInfo(entityId) {
    this.dispatchEvent(
      new CustomEvent("hass-more-info", { detail: { entityId }, bubbles: true, composed: true }),
    );
  }

  static get styles() {
    return `
      :host { display: block; }
      ha-card { padding: var(--ha-space-2, 8px); }
      .lines { display: flex; flex-direction: column; }
      .line {
        --ha-ripple-color: var(--primary-color);
        --ha-ripple-hover-opacity: 0.04;
        --ha-ripple-pressed-opacity: 0.12;
        position: relative;
        display: flex;
        align-items: center;
        gap: var(--ha-space-3, 12px);
        min-height: 56px;
        padding: 0 var(--ha-space-2, 8px);
        border-radius: var(--ha-border-radius-lg, 12px);
        cursor: pointer;
        outline: none;
      }
      .line:focus-visible { box-shadow: 0 0 0 2px var(--primary-color); }
      ha-tile-icon { flex: none; }
      .line-code {
        font-weight: var(--ha-font-weight-bold, 700);
        font-size: var(--ha-font-size-m, 14px);
      }
      ha-tile-info { flex: 1 1 auto; min-width: 0; }
      .status {
        flex: none;
        --ha-badge-size: 28px;
        --ha-badge-icon-size: 10px;
      }
      .empty {
        display: flex;
        align-items: center;
        gap: var(--ha-space-2, 8px);
        padding: var(--ha-space-4, 16px) var(--ha-space-3, 12px);
        color: var(--secondary-text-color);
      }
    `;
  }
}

class MetroCardEditor extends HTMLElement {
  setConfig(config) {
    this._config = config;
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  _schema() {
    return [
      {
        name: "entities",
        selector: {
          entity: { multiple: true, filter: { integration: INTEGRATION_DOMAIN, domain: "sensor" } },
        },
      },
      {
        name: "secondary_info",
        selector: {
          select: {
            mode: "dropdown",
            options: SECONDARY_OPTIONS.map((value) => ({
              value,
              label: localize(this._hass, `editor.secondary_info_${value}`),
            })),
          },
        },
      },
    ];
  }

  _render() {
    if (!this._hass || !this._config) return;
    if (!this._form) {
      this._form = document.createElement("ha-form");
      this._form.computeLabel = (field) => localize(this._hass, `editor.${field.name}`);
      this._form.addEventListener("value-changed", (event) => {
        const config = { ...this._config, ...event.detail.value };
        for (const [key, value] of Object.entries(config)) {
          if (value === "" || value == null || (Array.isArray(value) && value.length === 0)) {
            delete config[key];
          }
        }
        config.type = this._config.type ?? `custom:${CARD_TYPE}`;
        this.dispatchEvent(
          new CustomEvent("config-changed", { detail: { config }, bubbles: true, composed: true }),
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

// O módulo é avaliado uma vez por URL, e a URL carrega a versão da integração:
// atualizar sem reiniciar o Home Assistant o carrega uma segunda vez.
if (!customElements.get(CARD_TYPE)) {
  customElements.define(CARD_TYPE, MetroCard);
  customElements.define(EDITOR_TYPE, MetroCardEditor);

  window.customCards = window.customCards || [];
  window.customCards.push({
    type: CARD_TYPE,
    name: "Metrô SP Card",
    description: "Lists the Metrô SP / CPTM lines and their operation status.",
    preview: true,
    documentationURL: "https://github.com/roquerodrigo/ha-metro-sp",
  });

  console.info("%c metro-card ", "background:#0455A1;color:#fff;border-radius:3px", "loaded");
}
