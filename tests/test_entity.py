from __future__ import annotations

from unittest.mock import MagicMock

from custom_components.metro_sp.const import ATTRIBUTION
from custom_components.metro_sp.entity import MetroSPEntity


def _make_entity(entry_id="test_entry_id") -> MetroSPEntity:
    coordinator = MagicMock()
    coordinator.config_entry.entry_id = entry_id
    return MetroSPEntity(coordinator=coordinator)


def test_attribution():
    assert _make_entity()._attr_attribution == ATTRIBUTION


def test_has_entity_name():
    assert _make_entity()._attr_has_entity_name is True


def test_base_does_not_carry_device_info():
    """Per-line device_info is set by subclasses; base must not stomp it."""
    entity = _make_entity()
    assert getattr(entity, "_attr_device_info", None) is None


def test_coordinator_stored():
    coord = MagicMock()
    coord.config_entry.entry_id = "eid"
    assert MetroSPEntity(coordinator=coord).coordinator is coord
