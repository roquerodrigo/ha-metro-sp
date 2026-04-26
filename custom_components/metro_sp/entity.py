"""MetroSPEntity base class."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
from .coordinator import MetroSPDataUpdateCoordinator


class MetroSPEntity(CoordinatorEntity[MetroSPDataUpdateCoordinator]):
    """Base entity for Metrô SP."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(self, coordinator: MetroSPDataUpdateCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name="Metrô SP",
            manufacturer="Metrô SP / CPTM",
        )
