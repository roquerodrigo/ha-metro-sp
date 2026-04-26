"""Custom types for metro_sp."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import MetroSPApiClient
    from .coordinator import MetroSPDataUpdateCoordinator


type MetroSPConfigEntry = ConfigEntry[MetroSPData]


@dataclass
class MetroSPData:
    """Data for the Metrô SP integration."""

    client: MetroSPApiClient
    coordinator: MetroSPDataUpdateCoordinator
    integration: Integration
