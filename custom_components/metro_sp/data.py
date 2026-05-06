"""Custom types for metro_sp."""

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
    """Shape of a single entry in the /lines API response."""

    Code: int
    ColorName: str
    ColorHex: str
    Line: str
    StatusCode: int
    StatusLabel: str
    StatusColor: str
    Description: NotRequired[str | None]


class MetroSPLinesResponse(TypedDict):
    """Top-level wrapper of the /lines API response."""

    Data: list[MetroSPLine]


class MetroSPSensorAttributes(TypedDict):
    """Shape of extra_state_attributes returned by MetroSPLineSensor."""

    status_code: int
    status_color: str
    color_name: str
    color_hex: str
    line_code: int


class MetroSPDiagnosticsEntry(TypedDict):
    """Entry section of the diagnostics dump."""

    title: str
    version: int
    domain: str
    data: Mapping[str, JsonValue]
    options: Mapping[str, JsonValue]


class MetroSPDiagnosticsPayload(TypedDict):
    """Top-level shape returned by async_get_config_entry_diagnostics."""

    entry: MetroSPDiagnosticsEntry
    coordinator_data: Mapping[int, MetroSPLine] | None


type MetroSPConfigEntry = ConfigEntry[MetroSPData]


@dataclass
class MetroSPData:
    """Data stored on entry.runtime_data for the Metrô SP integration."""

    client: MetroSPApiClient
    coordinator: MetroSPDataUpdateCoordinator
    integration: Integration
