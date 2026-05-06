# Code Style Guide

Style conventions for the `ha-metro-sp` project. Run `scripts/lint`
before committing — it executes `ruff format`, `ruff check --fix` and `mypy`,
and must exit cleanly. `pytest` (with the 95 % coverage gate) follows.

**Always read this file before adding or restructuring code.**

## Language

- Code is written in **English**: file names, class names, function names,
  variable names, dictionary keys, identifier strings.
- The Metrô SP API itself uses Portuguese keys (`Code`, `ColorName`,
  `StatusLabel`, …). Wrap them in a `MetroSPLine` `TypedDict` in `data.py` so
  the rest of the code refers to a typed shape, not raw strings.
- The conversation language with the user can be Portuguese or anything else;
  what is committed to disk stays English (with the API-payload exception
  above and the user-facing pt-BR translations).
- User-facing strings live in `custom_components/metro_sp/translations/{en,pt-BR}.json`
  only — do not hardcode them in Python.

## File organization

- **One top-level class per file.** Multiple semantically related classes (e.g.
  exception families) get grouped into a package directory with one class per
  submodule and an `__init__.py` re-exporting the public symbols.
  - Example: `exceptions/` contains `api_client_error.py`,
    `api_client_communication_error.py`, plus `__init__.py`.
- **TypedDicts and `type` aliases do not count as "classes"** for this rule —
  they live alongside related code (typically in `data.py`) and do not need
  their own file.
- **Helper functions** may live in the same file as the single class that uses
  them (e.g. `_verify_response_or_raise` in `api.py`).
- **`__init__.py` of the integration package** wires `async_setup_entry`,
  `async_unload_entry`, `async_reload_entry` (plus the static-www registration
  the integration needs) and nothing else.

## Naming

- Public classes are prefixed with `MetroSP`.
- Concrete platform entities end with the entity type:
  `MetroSPLineSensor`.
- Exception classes end with `Error`: `MetroSPApiClientError`,
  `MetroSPApiClientCommunicationError`.
- Private attributes / functions are prefixed with `_`.

## Typing

**Strict typing. No generics, no `Any`.** Mypy on `scripts/lint` enforces this.

Banned: `typing.Any`, `object` as a value type, bare `dict` / `list` / `tuple` /
`set`, `dict[str, Any]`, `Mapping[str, Any]`.

Required:

- `TypedDict` for known dict / JSON shapes (see `data.py`: `MetroSPLine`,
  `MetroSPDiagnosticsEntry`, `MetroSPDiagnosticsPayload`,
  `MetroSPSensorAttributes`).
- `@dataclass` for structured records (`MetroSPData`).
- Named `type` aliases for recursive / shared shapes — `JsonPrimitive`,
  `JsonValue`, `JsonObject` in `data.py`.
- `frozenset[str]` / `tuple[str, ...]` for fixed string collections.
- `cast("TypedDictName", value)` at HA framework boundaries that hand us a
  permissive type (e.g. `entry.data` is `MappingProxyType[str, Any]`).

When narrowing an HA-provided callback signature, mypy reports `[override]`
(Liskov violation). Add `# type: ignore[override]` with a one-line comment
explaining the deliberate narrowing.

## Properties and `__init__`

- **Always prefer `@property`** over assigning `_attr_*` values in `__init__`.
  Properties are computed lazily from backing fields stored on the parent class
  (e.g. `self.coordinator`, `self.entity_description`).
- When the body of `__init__` would only call `super().__init__(...)`, omit
  `__init__` entirely and let Python inherit the parent.
- Class-level constants like `_attr_attribution = ATTRIBUTION` and
  `_attr_has_entity_name = True` are fine — they don't depend on instance
  state.

## Imports

- Always start every module with `from __future__ import annotations` so type
  hints become lazy strings and the runtime cost of `if TYPE_CHECKING` imports
  is zero.
- Same-package relative imports (`from .module import …`) are the default.
- Move type-only imports into a `TYPE_CHECKING` block (Ruff `TC001`/`TC003`):

  ```python
  from __future__ import annotations
  from typing import TYPE_CHECKING

  if TYPE_CHECKING:
      from collections.abc import Mapping
      from .data import MetroSPLine
  ```

- `noqa` comments are reserved for unavoidable framework constraints (e.g.
  `# noqa: ARG001` for HA-framework callback parameters that must exist but go
  unused). Document the reason inline if non-obvious. Never silence to "make
  ruff happy" — fix the underlying code.

## Docstrings

- Every public class, function, method (including `@property`) and `__init__`
  has a docstring. Ruff enforces this via `D102`/`D107`.
- A single sentence is usually enough. Describe the *contract* or the *why*,
  not the obvious implementation.
- Module-level docstring at the top of every `.py` file.
- Avoid restating the type — the signature already does that.

## Comments

- Default to **no comments**. Add one only when the *why* is not obvious from
  the code: a hidden constraint, a workaround, a subtle invariant, or a
  deliberate type-system override.
- Never describe *what* the code does — well-named identifiers handle that.
- **No section dividers** like `# --- API payloads ---` to group related
  declarations. If a file has so many sections that you feel the need for
  visual separators, split it into multiple files instead.

## Coordinator and runtime data

- All API state flows through `entry.runtime_data: MetroSPData`
  (`data.py`). Never store integration state in `hass.data` (the only
  exception in this repo is the static-path registration sentinel
  `_STATIC_REGISTERED_KEY`, which is per-`hass`, not per-entry).
- The coordinator is typed as `DataUpdateCoordinator[dict[int, MetroSPLine]]`,
  keyed by line `Code`. `_async_update_data` returns the typed payload;
  client errors map to `UpdateFailed`.
- The Metrô SP API is unauthenticated, so no `ConfigEntryAuthFailed` /
  reauth flow exists. Do not add one unless the upstream API gains auth.

## Config / repairs / diagnostics

- `config_flow.py` carries a single `async_step_user` step backed by a
  `_validate` helper. The API has no credentials, so there is no reauth /
  reconfigure / options flow. Keep it that way until the API contract changes.
- `repairs.py` exposes `async_create_fix_flow`. Sample helpers like
  `async_raise_deprecated_api_issue` show how to register issues from anywhere
  in the integration.
- `diagnostics.py` returns `MetroSPDiagnosticsPayload`. There are no secrets
  in `entry.data`, so `TO_REDACT` is currently empty — keep the
  `async_redact_data` plumbing in place so adding a redacted key later is a
  one-line change.

## Translations

- Two locales: `en.json` and `pt-BR.json`. `tests/test_translations.py`
  parametrizes over every locale and fails if their nested key sets diverge.
- Issue strings live under `issues.<issue_id>`; flow strings under
  `config.step.<step_id>`; entity names under `entity.sensor.<key>.name`.

## Linting and verification

- Ruff configuration lives in `.ruff.toml` with `select = ["ALL"]`.
- Mypy configuration lives in `mypy.ini`. Both run from `scripts/lint`.
- After every change run `scripts/lint && pytest`. Both gates mirror CI
  (`.github/workflows/lint.yml`).
- Tests live in `tests/`, mirroring the production layout. The 95 % coverage
  gate (`pytest.ini`) prevents untested code from sneaking in. When a test
  exercises a state that is impossible under the new types, update or remove
  it — never weaken the type to satisfy the test.
