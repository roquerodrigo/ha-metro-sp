"""Tests for MetroSPEntity base class."""

from __future__ import annotations

from unittest.mock import MagicMock

from custom_components.metro_sp.const import ATTRIBUTION, DOMAIN
from custom_components.metro_sp.entity import MetroSPEntity


def _make_entity(entry_id="test_entry_id") -> MetroSPEntity:
    coordinator = MagicMock()
    coordinator.config_entry = MagicMock()
    coordinator.config_entry.entry_id = entry_id
    return MetroSPEntity(coordinator=coordinator)


def test_entity_has_attribution():
    entity = _make_entity()
    assert entity._attr_attribution == ATTRIBUTION


def test_entity_has_entity_name():
    entity = _make_entity()
    assert entity._attr_has_entity_name is True


def test_entity_device_info_set():
    entity = _make_entity()
    assert entity._attr_device_info is not None


def test_entity_device_info_name():
    entity = _make_entity()
    assert entity._attr_device_info["name"] == "Metrô SP"


def test_entity_device_info_manufacturer():
    entity = _make_entity()
    assert entity._attr_device_info["manufacturer"] == "Metrô SP / CPTM"


def test_entity_device_info_identifiers_contains_domain():
    entity = _make_entity()
    identifiers = entity._attr_device_info["identifiers"]
    assert any(DOMAIN in str(i) for i in identifiers)


def test_entity_device_info_identifiers_contains_entry_id():
    entity = _make_entity(entry_id="unique_id_123")
    identifiers = entity._attr_device_info["identifiers"]
    assert any("unique_id_123" in str(i) for i in identifiers)


def test_entity_stores_coordinator():
    coordinator = MagicMock()
    coordinator.config_entry.entry_id = "eid"
    entity = MetroSPEntity(coordinator=coordinator)
    assert entity.coordinator is coordinator
