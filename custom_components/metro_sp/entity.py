"""Classe base MetroSPEntity."""

from __future__ import annotations

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION
from .coordinator import MetroSPDataUpdateCoordinator


class MetroSPEntity(CoordinatorEntity[MetroSPDataUpdateCoordinator]):
    """Entidade base do Metrô SP. O device_info por linha vem das subclasses."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True
