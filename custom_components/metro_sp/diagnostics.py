"""Diagnostics support for metro_sp."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from homeassistant.components.diagnostics import async_redact_data

if TYPE_CHECKING:
    from collections.abc import Mapping

    from homeassistant.core import HomeAssistant

    from .data import (
        JsonValue,
        MetroSPConfigEntry,
        MetroSPDiagnosticsEntry,
        MetroSPDiagnosticsPayload,
    )

# The Metrô SP API has no auth; entry.data is empty today.
# We keep the redact plumbing in place so adding a redacted key later is a
# one-line change.
TO_REDACT: frozenset[str] = frozenset()


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,  # noqa: ARG001
    entry: MetroSPConfigEntry,
) -> MetroSPDiagnosticsPayload:
    """Return diagnostics for a config entry."""
    redacted_data = cast(
        "Mapping[str, JsonValue]",
        async_redact_data(dict(entry.data), set(TO_REDACT)),
    )
    redacted_options = cast(
        "Mapping[str, JsonValue]",
        async_redact_data(dict(entry.options), set(TO_REDACT)),
    )
    diag_entry: MetroSPDiagnosticsEntry = {
        "title": entry.title,
        "version": entry.version,
        "domain": entry.domain,
        "data": redacted_data,
        "options": redacted_options,
    }
    return {
        "entry": diag_entry,
        "coordinator_data": entry.runtime_data.coordinator.data,
    }
