"""Tests for MetroSPEntity base class."""

from __future__ import annotations

from unittest.mock import MagicMock

from custom_components.metro_sp.const import ATTRIBUTION, DOMAIN
from custom_components.metro_sp.entity import MetroSPEntity


def _make_entity(entry_id="test_entry_id") -> MetroSPEntity:
    coordinator = MagicMock()
    coordinator.config_entry.entry_id = entry_id
    return MetroSPEntity(coordinator=coordinator)


def test_attribution():
    assert _make_entity()._attr_attribution == ATTRIBUTION


def test_has_entity_name():
    assert _make_entity()._attr_has_entity_name is True


def test_device_info_name():
    assert _make_entity()._attr_device_info["name"] == "Metrô SP"


def test_device_info_manufacturer():
    assert _make_entity()._attr_device_info["manufacturer"] == "Metrô SP / CPTM"


def test_device_info_identifiers_contain_domain():
    identifiers = _make_entity()._attr_device_info["identifiers"]
    assert any(DOMAIN in str(i) for i in identifiers)


def test_device_info_identifiers_contain_entry_id():
    identifiers = _make_entity(entry_id="my_id")._attr_device_info["identifiers"]
    assert any("my_id" in str(i) for i in identifiers)


def test_coordinator_stored():
    coord = MagicMock()
    coord.config_entry.entry_id = "eid"
    assert MetroSPEntity(coordinator=coord).coordinator is coord
