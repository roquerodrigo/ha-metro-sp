# CLAUDE.md

Guidance for Claude Code (claude.ai/code) agents working in this repository.

## Always read `CODE_STYLE.md` first

Before creating, renaming or restructuring any file/class/function, **read [`CODE_STYLE.md`](./CODE_STYLE.md)**. It is the single source of truth for conventions: language, file organisation, naming, typing, properties vs `__init__`, imports, docstrings, comments, coordinator pattern, repairs/diagnostics layout, translations, lint workflow.

For user-facing topics (what's included, how to install, useful commands, CI list), see [`README.md`](./README.md).

This file deliberately avoids restating those rules — it only adds:

1. The verification workflow agents must run after every change.
2. The architectural reasoning that is not obvious from `CODE_STYLE.md` alone.
3. Local development quirks specific to this repo.

## Verification workflow

**After every code change, always run lint then tests, in that order, before declaring the task done:**

```bash
scripts/lint && pytest
```

- `scripts/lint` runs `ruff format`, `ruff check --fix` and `mypy` (`mypy.ini`). Fix any failure and re-run before moving on.
- `pytest` enforces a **95 % coverage gate** (`pytest.ini`).

Both gates mirror CI (`.github/workflows/lint.yml`). Skip this only when the change literally cannot affect lint or tests (e.g., README-only edits).

## Local development

- `scripts/setup` installs `requirements.txt` + `requirements_test.txt`.
- `scripts/develop` starts Home Assistant in debug mode with the integration loaded. Config lives in `config/`; `PYTHONPATH` points at `custom_components/`. No symlinks needed.
- When restarting HA during development, clear the registry so entity/device IDs are recreated with current values:

  ```bash
  rm config/.storage/core.entity_registry config/.storage/core.device_registry
  ```

- macOS Bluetooth causes intermittent crashes (PyObjC/CoreBluetooth race, exit 134). Unrelated to this integration. `config/configuration.yaml` already sets `bluetooth: passive_scanning: false` as mitigation.

## Architecture

The integration follows the HA `DataUpdateCoordinator` pattern:

```
config_flow.py   → tests connectivity and creates the ConfigEntry (no credentials)
__init__.py      → instantiates ApiClient + DataUpdateCoordinator, performs the first refresh,
                   registers the per-line static images under STATIC_URL_PREFIX
coordinator.py   → polls every UPDATE_INTERVAL (5 min); returns dict[int, MetroSPLine] keyed by line Code
sensor.py        → reads coordinator.data and creates two sensors per line (operacao + detalhes)
```

### Entry typing

`data.py` defines `MetroSPConfigEntry = ConfigEntry[MetroSPData]` and the `MetroSPData(client, coordinator, integration)` dataclass. State lives on `entry.runtime_data` (auto-discarded on unload), never on `hass.data`.

The single `hass.data` entry is `_STATIC_REGISTERED_KEY` in `__init__.py` — a per-`hass` sentinel so we register the `/metro_sp` static path exactly once across reloads. It is *not* per-entry state.

### API and exceptions

`api.py` exposes `MetroSPApiClient` plus the `_verify_response_or_raise` helper. The Metrô SP API (`https://apim-proximotrem-prd-brazilsouth-001.azure-api.net/api/v1/lines`) is **public, no auth**, so there is no `AuthenticationError` and no reauth flow.

Exceptions live under `exceptions/`:

- `MetroSPApiClientError` (base)
- `MetroSPApiClientCommunicationError` (timeout, connection, socket)

`_api_wrapper` maps `TimeoutError`, `aiohttp.ClientError` and `socket.gaierror` to `CommunicationError`; any other exception becomes the base error.

### Per-line entities

Each line becomes an independent **device** with `manufacturer` mapped per operator (`_LINE_OPERATORS` in `sensor.py`). Each device has two sensors:

- **Operação** (`sensor.metro_sp_linha_{N}_{cor}_operacao`): `native_value = StatusLabel`; attributes carry status / colour fields. `entity_picture` points at the local `/metro_sp/linha_{N}.png` static asset registered in `__init__.py`.
- **Detalhes da Operação** (`sensor.metro_sp_linha_{N}_{cor}_detalhes`): `native_value = Description`.

Because each line is its own device, `device_info` lives as a `@property` on `MetroSPLineSensor`, **not** on the `MetroSPEntity` base. The base only carries integration-wide attributes (`_attr_attribution`, `_attr_has_entity_name`).

The `entity_id` is suggested explicitly in the constructor via `self.entity_id = "sensor.{base_id}_{key}"`, which HA records as `suggested_object_id` in the registry on first creation.

### Diagnostics

`diagnostics.py` returns `MetroSPDiagnosticsPayload` (entry metadata + the indexed coordinator dump). `TO_REDACT` is empty today — keep the `async_redact_data` plumbing so adding a redacted key later is a one-line change. `.github/ISSUE_TEMPLATE/bug.yml` asks users to attach the dump.

### Repairs

`repairs.py` is the entry point HA calls when the user clicks **Fix** on an issue:

- `async_create_fix_flow(hass, issue_id, data)` returns a `RepairsFlow`. Branch on `issue_id` for multiple kinds; the default returns `ConfirmRepairFlow`.
- `async_raise_deprecated_api_issue(hass)` is the sample helper that registers an issue. Call helpers like this from the coordinator/setup when you detect a recoverable problem.

Issue strings live under `issues.<issue_id>` in the translation files.
