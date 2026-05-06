"""MetroSPEntity base class."""

from __future__ import annotations

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION
from .coordinator import MetroSPDataUpdateCoordinator


class MetroSPEntity(CoordinatorEntity[MetroSPDataUpdateCoordinator]):
    """Base entity for Metrô SP. Per-line device_info is provided by subclasses."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True
