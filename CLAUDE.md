# CLAUDE.md

Guidance for Claude Code (claude.ai/code) agents working in this repository.

## Always read `CODE_STYLE.md` first

Before creating, renaming or restructuring any file/class/function, **read [`CODE_STYLE.md`](./CODE_STYLE.md)** — the single source of truth for conventions (language, file organisation, naming, typing, coordinator pattern, translations, lint workflow, conventional commits). For user-facing topics (supported lines, install, sensor attributes) see [`README.md`](./README.md).

This file only adds what neither of those covers: the verification workflow, local-dev quirks, and the architectural *why*.

## Verification workflow

**After every code change, run lint then tests, in that order, before declaring the task done:**

```bash
uv run ruff format . && uv run ruff check . --fix && uv run mypy custom_components/metro_sp && uv run pytest
```

`pytest` enforces a **90 % coverage gate** (configured in `pyproject.toml`). Both gates mirror CI. Skip this only when the change literally cannot affect lint or tests (e.g., README-only edits).

## Local development

- `scripts/develop` starts Home Assistant in debug mode with the integration loaded (config in `config/`, `PYTHONPATH` at `custom_components/`; no symlinks).
- When restarting HA during development, clear the registry so entity/device IDs are recreated with current values:

  ```bash
  rm config/.storage/core.entity_registry config/.storage/core.device_registry
  ```

- macOS Bluetooth causes intermittent crashes (PyObjC/CoreBluetooth race, exit 134), unrelated to this integration. Mitigate with `bluetooth: passive_scanning: false` in `config/configuration.yaml`.

## Architectural rationale

Standard HA `DataUpdateCoordinator` layout; the non-obvious decisions:

- **Coordinator grace period.** On upstream failure the coordinator returns the last known data for `FAILURE_GRACE_PERIOD` (5 min) instead of marking entities unavailable, only raising `UpdateFailed` once it elapses.
- **Public, unauthenticated API** (`.../api/v1/lines`). There is deliberately no `AuthenticationError`, reauth, or options flow — do not add one unless the upstream API gains auth.
- **`description` is a state attribute, not a separate sensor:** HA truncates state values longer than 255 characters to `unknown`, and the upstream incident text routinely exceeds that.
- **Per-line device.** Each line is its own device, so `device_info` is a `@property` on `MetroSPLineSensor`, not on the `MetroSPEntity` base. The pt-BR `entity_id` slug (`sensor.metro_sp_linha_{N}_{cor}_operacao`) is set via `self.entity_id` in the constructor and is registry state on users' installs — never rename it.
- **Bundled Lovelace card** (`www/metro-card.js`, a zero-build vanilla `custom:metro-card`): `MetroSPCardRegistration` registers it as a Lovelace dashboard resource, not just via `add_extra_js_url`. Dashboard resources persist in storage and are fetched on every dashboard load, closing the startup window where a mid-boot extra module was missing from already-served pages; `add_extra_js_url` remains only as the YAML-mode-Lovelace fallback. The `?v={integration.version}` query busts the browser cache on release. i18n strings are embedded in the file — a pure frontend plugin has no access to `custom_components` translations.
- **No `repairs.py`:** there is no recoverable condition to surface. Add the platform together with the first real issue it raises, never as an unused scaffold.
