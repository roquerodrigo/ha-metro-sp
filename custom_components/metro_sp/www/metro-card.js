/**
 * Card Metrô SP — um card custom do Lovelace que lista as linhas do Metrô SP /
 * CPTM expostas pela integração `metro_sp` e mostra o status de operação de
 * cada linha.
 *
 * Web component em vanilla JS, sem build (sem Lit nem bundler). Os estilos vêm
 * inteiramente dos design tokens do Home Assistant, então o card acompanha o
 * tema ativo e o modo claro/escuro automaticamente. O ponto de status usa o
 * atributo `status_color` da origem; o selo da linha usa o `color_hex` oficial
 * da linha.
 *
 * Config:
 *   type: custom:metro-card
 *   entities: [...]             # opcional: escolhe as linhas exibidas (entity ids).
 *                               #   quando omitido, todas as linhas do metro_sp
 *                               #   são exibidas, ordenadas pelo número da linha.
 *   secondary_info: last-changed  # last-changed | description | none (padrão last-changed)
 */

const DEFAULT_SECONDARY = "last-changed";

// i18n — plugin puramente de frontend (sem as traduções do custom_component),
// então as strings ficam embutidas aqui e são escolhidas pelo idioma ativo da UI
// do HA, com fallback para o inglês.
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

// Mapeia os nomes de campo do ha-form para as translation keys (para o computeLabel).
const EDITOR_LABEL_KEYS = {
  entities: "editor.entities",
  secondary_info: "editor.secondary",
};

/** O idioma ativo da UI do HA, ou um fallback suportado (idioma base, depois "en"). */
function resolveLang(hass) {
  const lang = (hass && (hass.locale?.language || hass.language || hass.selectedLanguage)) || "en";
  if (TRANSLATIONS[lang]) return lang;
  if (lang.split("-")[0] === "pt") return "pt-BR";
  return "en";
}

/** Traduz uma chave pontuada para o idioma ativo; o inglês é o fallback. */
function localize(hass, key) {
  const lang = resolveLang(hass);
  return TRANSLATIONS[lang]?.[key] ?? TRANSLATIONS.en[key] ?? key;
}

/** Verdadeiro para um sensor de linha do metro_sp — identificado pelos atributos da integração. */
function isMetroLine(state) {
  const a = state?.attributes;
  return !!a && a.line_code !== undefined && a.color_hex !== undefined;
}

/** Escapa uma string para interpolação segura em innerHTML. */
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
    // Uma lista vazia (o estado inicial do editor) significa "mostrar todas as
    // linhas", como omitir a opção — do contrário, abrir o editor esvaziaria o card.
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

  /** Descobre os sensores de linha a exibir, ordenados pelo número da linha. */
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

    // Pula a reconstrução quando nada visível mudou (evita flicker).
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

    // O ha-relative-time é um elemento orientado a propriedades — hass e datetime
    // são ligados depois do render da string (ele atualiza sozinho o texto "há x minutos").
    this.shadowRoot.querySelectorAll(".rt").forEach((el) => {
      el.hass = hass;
      const ts = el.dataset.ts;
      if (ts) el.datetime = new Date(ts);
    });

    this.shadowRoot.querySelectorAll(".row").forEach((row) => {
      row.addEventListener("click", () => this._showMore(row.dataset.id));
    });
  }

  /** Abre o diálogo more-info de uma entidade (comportamento padrão do HA). */
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

  /** Monta o schema do ha-form com os rótulos das opções no idioma ativo. */
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

// O módulo roda uma vez por URL de onde é servido, e a URL do card carrega a
// versão da integração. Atualizar a integração sem reiniciar o Home Assistant
// deixa a URL da versão anterior registrada ao lado da nova, então o módulo é
// avaliado duas vezes. Sem esta guarda, a segunda execução falha no nome de tag
// já ocupado e registra uma entrada duplicada no seletor de cards.
if (!customElements.get("metro-card")) {
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
}
