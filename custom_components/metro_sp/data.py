"""Tipos próprios do metro_sp."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, NotRequired, TypedDict

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import MetroSPApiClient
    from .coordinator import MetroSPDataUpdateCoordinator


type JsonPrimitive = str | int | float | bool | None
type JsonValue = JsonPrimitive | list[JsonValue] | Mapping[str, JsonValue]
type JsonObject = Mapping[str, JsonValue]


class MetroSPLine(TypedDict):
    """Forma de um item da resposta de /lines da API."""

    Code: int
    ColorName: str
    ColorHex: str
    Line: str
    StatusCode: int
    StatusLabel: str
    StatusColor: str
    Description: NotRequired[str | None]


class MetroSPLinesResponse(TypedDict):
    """Envelope de nível superior da resposta de /lines da API."""

    Data: list[MetroSPLine]


class MetroSPSensorAttributes(TypedDict):
    """Forma do extra_state_attributes devolvido por MetroSPLineSensor."""

    status_code: int
    status_color: str
    color_name: str
    color_hex: str
    line_code: int
    description: str


class MetroSPDiagnosticsEntry(TypedDict):
    """Seção da entry no arquivo de diagnóstico."""

    title: str
    version: int
    domain: str
    data: Mapping[str, JsonValue]
    options: Mapping[str, JsonValue]


class MetroSPDiagnosticsPayload(TypedDict):
    """Forma de nível superior devolvida por async_get_config_entry_diagnostics."""

    entry: MetroSPDiagnosticsEntry
    coordinator_data: Mapping[int, MetroSPLine] | None


type MetroSPConfigEntry = ConfigEntry[MetroSPData]


@dataclass
class MetroSPData:
    """Dados guardados em entry.runtime_data pela integração Metrô SP."""

    client: MetroSPApiClient
    coordinator: MetroSPDataUpdateCoordinator
    integration: Integration
