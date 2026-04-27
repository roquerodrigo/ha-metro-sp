"""Tests for MetroSPLineSensor."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from custom_components.metro_sp.sensor import MetroSPLineSensor, async_setup_entry


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_sensor(coordinator, line_code: int, sensor_key: str) -> MetroSPLineSensor:
    return MetroSPLineSensor(
        coordinator=coordinator, line_code=line_code, sensor_key=sensor_key
    )


# ---------------------------------------------------------------------------
# async_setup_entry
# ---------------------------------------------------------------------------


async def test_async_setup_entry_creates_two_sensors_per_line(
    mock_coordinator, sample_data
):
    entry = MagicMock()
    entry.runtime_data.coordinator = mock_coordinator

    added = []
    async_add_entities = lambda entities, **_: added.extend(entities)

    await async_setup_entry(hass=MagicMock(), entry=entry, async_add_entities=async_add_entities)

    assert len(added) == len(sample_data) * 2


async def test_async_setup_entry_creates_operacao_and_detalhes(mock_coordinator):
    entry = MagicMock()
    entry.runtime_data.coordinator = mock_coordinator

    added = []
    async_add_entities = lambda entities, **_: added.extend(entities)
    await async_setup_entry(hass=MagicMock(), entry=entry, async_add_entities=async_add_entities)

    keys = {s._sensor_key for s in added}
    assert keys == {"operacao", "detalhes"}


# ---------------------------------------------------------------------------
# MetroSPLineSensor.__init__
# ---------------------------------------------------------------------------


def test_sensor_unique_id_format(mock_coordinator):
    sensor = _make_sensor(mock_coordinator, line_code=1, sensor_key="operacao")
    assert "metro_sp_linha_1" in sensor._attr_unique_id
    assert "operacao" in sensor._attr_unique_id


def test_sensor_entity_id_format(mock_coordinator):
    sensor = _make_sensor(mock_coordinator, line_code=1, sensor_key="operacao")
    assert sensor.entity_id.startswith("sensor.metro_sp_linha_1")
    assert sensor.entity_id.endswith("_operacao")


def test_sensor_translation_key(mock_coordinator):
    sensor = _make_sensor(mock_coordinator, line_code=1, sensor_key="detalhes")
    assert sensor._attr_translation_key == "detalhes"


def test_sensor_device_info_set(mock_coordinator):
    sensor = _make_sensor(mock_coordinator, line_code=1, sensor_key="operacao")
    assert sensor._attr_device_info is not None


def test_sensor_device_info_manufacturer_known_line(mock_coordinator):
    sensor = _make_sensor(mock_coordinator, line_code=1, sensor_key="operacao")
    assert sensor._attr_device_info["manufacturer"] == "Metrô SP"


def test_sensor_device_info_manufacturer_cptm(mock_coordinator, sample_data):
    # Line 7 is CPTM – add it to coordinator data
    mock_coordinator.data[7] = {
        "Code": 7,
        "ColorName": "Rubi",
        "ColorHex": "#FF0000",
        "Line": "7",
        "StatusCode": 1,
        "StatusLabel": "Operação Normal",
        "StatusColor": "#00FF00",
        "Description": "",
    }
    sensor = _make_sensor(mock_coordinator, line_code=7, sensor_key="operacao")
    assert sensor._attr_device_info["manufacturer"] == "CPTM"


def test_sensor_device_info_manufacturer_fallback(mock_coordinator, sample_data):
    # Line 99 is unknown
    mock_coordinator.data[99] = {
        "Code": 99,
        "ColorName": "Preta",
        "ColorHex": "#000000",
        "Line": "99",
        "StatusCode": 1,
        "StatusLabel": "Operação Normal",
        "StatusColor": "#00FF00",
        "Description": "",
    }
    sensor = _make_sensor(mock_coordinator, line_code=99, sensor_key="operacao")
    assert sensor._attr_device_info["manufacturer"] == "Metrô SP / CPTM"


def test_sensor_device_info_contains_entry_id(mock_coordinator):
    sensor = _make_sensor(mock_coordinator, line_code=1, sensor_key="operacao")
    ids = sensor._attr_device_info["identifiers"]
    found = any("test_entry_id" in str(i) for i in ids)
    assert found


# ---------------------------------------------------------------------------
# native_value
# ---------------------------------------------------------------------------


def test_native_value_operacao_returns_status_label(mock_coordinator):
    sensor = _make_sensor(mock_coordinator, line_code=1, sensor_key="operacao")
    assert sensor.native_value == "Operação Normal"


def test_native_value_detalhes_returns_description(mock_coordinator):
    sensor = _make_sensor(mock_coordinator, line_code=1, sensor_key="detalhes")
    assert sensor.native_value == "Linha operando normalmente."


def test_native_value_detalhes_empty_description(mock_coordinator):
    sensor = _make_sensor(mock_coordinator, line_code=3, sensor_key="detalhes")
    assert sensor.native_value == ""


def test_native_value_detalhes_none_description(mock_coordinator):
    mock_coordinator.data[1]["Description"] = None
    sensor = _make_sensor(mock_coordinator, line_code=1, sensor_key="detalhes")
    assert sensor.native_value == ""


# ---------------------------------------------------------------------------
# entity_picture
# ---------------------------------------------------------------------------


def test_entity_picture_contains_color_hex(mock_coordinator):
    sensor = _make_sensor(mock_coordinator, line_code=1, sensor_key="operacao")
    assert "0455A1" in sensor.entity_picture


def test_entity_picture_contains_line_code(mock_coordinator):
    sensor = _make_sensor(mock_coordinator, line_code=1, sensor_key="operacao")
    assert "1" in sensor.entity_picture


def test_entity_picture_uses_ui_avatars(mock_coordinator):
    sensor = _make_sensor(mock_coordinator, line_code=1, sensor_key="operacao")
    assert "ui-avatars.com" in sensor.entity_picture


def test_entity_picture_strips_hash_from_hex(mock_coordinator):
    sensor = _make_sensor(mock_coordinator, line_code=1, sensor_key="operacao")
    assert "#" not in sensor.entity_picture


def test_entity_picture_defaults_when_no_color_hex(mock_coordinator):
    mock_coordinator.data[1].pop("ColorHex", None)
    sensor = _make_sensor(mock_coordinator, line_code=1, sensor_key="operacao")
    assert "888888" in sensor.entity_picture


# ---------------------------------------------------------------------------
# icon
# ---------------------------------------------------------------------------


def test_icon_is_subway(mock_coordinator):
    sensor = _make_sensor(mock_coordinator, line_code=1, sensor_key="operacao")
    assert sensor.icon == "mdi:subway"


# ---------------------------------------------------------------------------
# extra_state_attributes
# ---------------------------------------------------------------------------


def test_extra_state_attributes_keys(mock_coordinator):
    sensor = _make_sensor(mock_coordinator, line_code=1, sensor_key="operacao")
    attrs = sensor.extra_state_attributes
    assert set(attrs.keys()) == {
        "status_code",
        "status_color",
        "color_name",
        "color_hex",
        "line_code",
    }


def test_extra_state_attributes_values(mock_coordinator):
    sensor = _make_sensor(mock_coordinator, line_code=1, sensor_key="operacao")
    attrs = sensor.extra_state_attributes
    assert attrs["status_code"] == 1
    assert attrs["color_name"] == "Azul"
    assert attrs["color_hex"] == "#0455A1"
    assert attrs["line_code"] == 1


def test_extra_state_attributes_detalhes_same_values(mock_coordinator):
    sensor = _make_sensor(mock_coordinator, line_code=1, sensor_key="detalhes")
    attrs = sensor.extra_state_attributes
    assert attrs["status_code"] == 1


# ---------------------------------------------------------------------------
# _line_data property
# ---------------------------------------------------------------------------


def test_line_data_returns_current_coordinator_data(mock_coordinator):
    sensor = _make_sensor(mock_coordinator, line_code=1, sensor_key="operacao")
    assert sensor._line_data is mock_coordinator.data[1]
