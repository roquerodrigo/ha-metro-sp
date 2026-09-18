"""Suporte a diagnostics do metro_sp."""

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

# A API do Metrô SP não tem autenticação; entry.data está vazio hoje.
# A chamada de redact permanece para que adicionar uma chave a ocultar no
# futuro seja uma mudança de uma linha.
TO_REDACT: frozenset[str] = frozenset()


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,  # noqa: ARG001
    entry: MetroSPConfigEntry,
) -> MetroSPDiagnosticsPayload:
    """Devolve os diagnostics de uma config entry."""
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
