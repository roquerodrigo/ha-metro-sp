# CLAUDE.md

Guidance for Claude Code (claude.ai/code) agents working in this repository.

## Always read `CODE_STYLE.md` first

Before creating, renaming or restructuring any file/class/function, **read [`CODE_STYLE.md`](./CODE_STYLE.md)**. It is the single source of truth for conventions: language, file organisation, naming, typing, properties vs `__init__`, imports, docstrings, comments, coordinator pattern, diagnostics layout, translations, lint workflow.

For user-facing topics (what's included, how to install, useful commands, CI list), see [`README.md`](./README.md).

This file deliberately avoids restating those rules — it only adds:

1. The verification workflow agents must run after every change.
2. The architectural reasoning that is not obvious from `CODE_STYLE.md` alone.
3. Local development quirks specific to this repo.

## Verification workflow

**After every code change, always run lint then tests, in that order, before declaring the task done:**

```bash
uv run ruff format . && uv run ruff check . --fix && uv run mypy custom_components/metro_sp && uv run pytest
```

- The lint commands run `ruff format`, `ruff check --fix` and `mypy` (configured in `pyproject.toml`). Fix any failure and re-run before moving on.
- `pytest` enforces a **90 % coverage gate** (configured in `pyproject.toml`).

Both gates mirror CI. Skip this only when the change literally cannot affect lint or tests (e.g., README-only edits).

## Local development

- `uv sync` installs the dependencies declared in `pyproject.toml` (`uv.lock`).
- `scripts/develop` starts Home Assistant in debug mode with the integration loaded. Config lives in `config/`; `PYTHONPATH` points at `custom_components/`. No symlinks needed.
- When restarting HA during development, clear the registry so entity/device IDs are recreated with current values:

  ```bash
  rm config/.storage/core.entity_registry config/.storage/core.device_registry
  ```

- macOS Bluetooth causes intermittent crashes (PyObjC/CoreBluetooth race, exit 134). Unrelated to this integration. If it hits you, add `bluetooth: passive_scanning: false` to `config/configuration.yaml` as a mitigation.

## Architecture

The integration follows the HA `DataUpdateCoordinator` pattern:

```
config_flow.py        → tests connectivity and creates the ConfigEntry (no credentials)
__init__.py           → instantiates ApiClient + DataUpdateCoordinator, performs the first refresh,
                        and delegates card/static-file registration to MetroSPCardRegistration
card_registration.py  → registers the whole www/ dir as static files under STATIC_URL_PREFIX
                        (per-line images + the bundled metro-card.js) and keeps the card
                        registered as a Lovelace dashboard resource
coordinator.py        → polls every UPDATE_INTERVAL (5 min); returns dict[int, MetroSPLine] keyed by line Code;
                        tolerates API failures for FAILURE_GRACE_PERIOD (5 min), returning stale data instead
                        of marking entities unavailable — only raises UpdateFailed once the grace period elapses
sensor.py             → reads coordinator.data and creates one sensor per line (translation key
                        ``operation``); the incident text is exposed via the ``description`` state attribute
```

### Entry typing

`data.py` defines `MetroSPConfigEntry = ConfigEntry[MetroSPData]` and the `MetroSPData(client, coordinator, integration)` dataclass. State lives on `entry.runtime_data` (auto-discarded on unload), never on `hass.data`.

The only `hass.data` entries are the two sentinels in `card_registration.py` (`_STATIC_PATH_REGISTERED_KEY`, `_EXTRA_MODULE_REGISTERED_KEY`) — per-`hass` flags so the `/metro_sp` static path and the extra-module fallback are registered exactly once across reloads. They are *not* per-entry state.

### API and exceptions

`api.py` exposes `MetroSPApiClient` plus the `_verify_response_or_raise` helper. The Metrô SP API (`https://apim-proximotrem-prd-brazilsouth-001.azure-api.net/api/v1/lines`) is **public, no auth**, so there is no `AuthenticationError` and no reauth flow.

Exceptions live under `exceptions/`:

- `MetroSPApiClientError` (base)
- `MetroSPApiClientCommunicationError` (timeout, connection, socket)

`_api_wrapper` maps `TimeoutError`, `aiohttp.ClientError` and `socket.gaierror` to `CommunicationError`; any other exception becomes the base error.

### Per-line entities

Each line becomes an independent **device** with `manufacturer` mapped per operator (`_LINE_OPERATORS` in `sensor.py`). Each device has one sensor:

- **Operation** (`sensor.metro_sp_linha_{N}_{cor}_operacao`, translation key `operation`): `native_value = StatusLabel`; attributes carry status / colour fields plus `description` (the upstream `Description`, falling back to `StatusLabel` when empty). `entity_picture` points at the local `/metro_sp/linha_{N}.png` static asset registered by `card_registration.py`.

`description` is intentionally an attribute, not a separate sensor: HA truncates state values longer than 255 characters to `unknown`, and the upstream incident text routinely exceeds that.

Because each line is its own device, `device_info` lives as a `@property` on `MetroSPLineSensor`, **not** on the `MetroSPEntity` base. The base only carries integration-wide attributes (`_attr_attribution`, `_attr_has_entity_name`).

The `entity_id` is suggested explicitly in the constructor via `self.entity_id = "sensor.{base_id}_operacao"`, which HA records as `suggested_object_id` in the registry on first creation.

### Bundled Lovelace card

`custom_components/metro_sp/www/metro-card.js` ships a zero-build vanilla web
component (`custom:metro-card`, no Lit/bundler) that lists the integration's
line sensors with their status. `MetroSPCardRegistration` serves it from the
same static dir as the line images and registers it as a **Lovelace dashboard
resource** (versioned with `?v={integration.version}` to bust the browser
cache on release) — users never add a dashboard resource by hand. Dashboard
resources persist in storage and are fetched on every dashboard load, which
closes the startup window where an extra module registered mid-boot was
missing from already-served pages; `add_extra_js_url` remains only as the
fallback for YAML-mode Lovelace, which has no programmatic resource storage.
Styling uses HA design tokens (theme/light/dark follow automatically); i18n
strings (`en`, `pt-BR`) are embedded in the file itself since this is a pure
frontend plugin with no access to `custom_components` translations.

### Diagnostics

`diagnostics.py` returns `MetroSPDiagnosticsPayload` (entry metadata + the indexed coordinator dump). `TO_REDACT` is empty today — keep the `async_redact_data` plumbing so adding a redacted key later is a one-line change. `.github/ISSUE_TEMPLATE/bug.yml` asks users to attach the dump.

There is deliberately no `repairs.py`: the integration has no recoverable condition to surface, and a scaffold with an unused helper only misleads. Add the platform (plus `issues.<issue_id>` translation strings and tests) together with the first real issue it raises.

## Language

Everything committed to code is English — identifiers, `ATTRIBUTION`, device names, translation keys (`operation`), commit messages. User-facing pt-BR strings live only in `translations/pt-BR.json`.

**Documented exception: `README.md` is written in pt-BR.** The integration serves the São Paulo metro network and its audience is Brazilian; keep the README in pt-BR and do not "fix" it to English.
