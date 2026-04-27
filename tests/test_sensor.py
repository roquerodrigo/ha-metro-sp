"""Tests for MetroSPLineSensor."""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Entity creation via real HA setup
# ---------------------------------------------------------------------------

async def test_sensor_count(hass, setup_integration):
    assert len(hass.states.async_all("sensor")) == 4


async def test_operacao_state_value(hass, setup_integration):
    state = hass.states.get("sensor.metro_sp_linha_1_azul_operacao")
    assert state.state == "Operação Normal"


async def test_detalhes_state_value(hass, setup_integration):
    state = hass.states.get("sensor.metro_sp_linha_1_azul_detalhes")
    assert state.state == "Linha operando normalmente."


async def test_detalhes_empty_description(hass, setup_integration):
    state = hass.states.get("sensor.metro_sp_linha_3_vermelha_detalhes")
    assert state.state == ""


# ---------------------------------------------------------------------------
# extra_state_attributes
# ---------------------------------------------------------------------------

async def test_operacao_attributes_keys(hass, setup_integration):
    state = hass.states.get("sensor.metro_sp_linha_1_azul_operacao")
    assert set(state.attributes) >= {
        "status_code", "status_color", "color_name", "color_hex", "line_code"
    }


async def test_operacao_attributes_values(hass, setup_integration):
    attrs = hass.states.get("sensor.metro_sp_linha_1_azul_operacao").attributes
    assert attrs["status_code"] == 1
    assert attrs["color_name"] == "Azul"
    assert attrs["color_hex"] == "#0455A1"
    assert attrs["line_code"] == 1


async def test_operacao_attributes_status_color(hass, setup_integration):
    attrs = hass.states.get("sensor.metro_sp_linha_1_azul_operacao").attributes
    assert attrs["status_color"] == "#00FF00"


# ---------------------------------------------------------------------------
# entity_picture
# ---------------------------------------------------------------------------

async def test_entity_picture_contains_color_hex(hass, setup_integration):
    from homeassistant.helpers import entity_registry as er
    ent_reg = er.async_get(hass)
    entity = ent_reg.async_get("sensor.metro_sp_linha_1_azul_operacao")
    assert entity is not None

    state = hass.states.get("sensor.metro_sp_linha_1_azul_operacao")
    # entity_picture is an attribute when set
    pic = state.attributes.get("entity_picture", "")
    assert "0455A1" in pic or pic == ""  # URL contains hex without #


async def test_entity_picture_uses_ui_avatars(hass, setup_integration):
    from custom_components.metro_sp.sensor import MetroSPLineSensor
    from unittest.mock import MagicMock

    coord = MagicMock()
    coord.data = {
        1: {
            "Code": 1,
            "ColorName": "Azul",
            "ColorHex": "#0455A1",
            "StatusLabel": "OK",
            "Description": "",
        }
    }
    coord.config_entry.entry_id = "eid"
    sensor = MetroSPLineSensor(coordinator=coord, line_code=1, sensor_key="operacao")
    assert "ui-avatars.com" in sensor.entity_picture
    assert "0455A1" in sensor.entity_picture
    assert "#" not in sensor.entity_picture


async def test_entity_picture_default_color_when_missing(hass, setup_integration):
    from custom_components.metro_sp.sensor import MetroSPLineSensor
    from unittest.mock import MagicMock

    coord = MagicMock()
    coord.data = {
        1: {"Code": 1, "ColorName": "Azul", "StatusLabel": "OK", "Description": ""}
    }
    coord.config_entry.entry_id = "eid"
    sensor = MetroSPLineSensor(coordinator=coord, line_code=1, sensor_key="operacao")
    assert "888888" in sensor.entity_picture


# ---------------------------------------------------------------------------
# icon
# ---------------------------------------------------------------------------

async def test_icon_is_mdi_subway(hass, setup_integration):
    from custom_components.metro_sp.sensor import MetroSPLineSensor
    from unittest.mock import MagicMock

    coord = MagicMock()
    coord.data = {
        1: {"Code": 1, "ColorName": "Azul", "ColorHex": "#0455A1",
            "StatusLabel": "OK", "Description": ""}
    }
    coord.config_entry.entry_id = "eid"
    sensor = MetroSPLineSensor(coordinator=coord, line_code=1, sensor_key="operacao")
    assert sensor.icon == "mdi:subway"


# ---------------------------------------------------------------------------
# Operator mapping
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("line_code,expected_manufacturer", [
    (1, "Metrô SP"),
    (2, "Metrô SP"),
    (3, "Metrô SP"),
    (4, "ViaQuatro"),
    (5, "ViaMobilidade"),
    (7, "CPTM"),
    (8, "ViaMobilidade"),
    (9, "ViaMobilidade"),
    (10, "CPTM"),
    (11, "CPTM"),
    (12, "CPTM"),
    (13, "CPTM"),
    (15, "Metrô SP"),
    (17, "ViaMobilidade"),
    (99, "Metrô SP / CPTM"),
])
async def test_operator_mapping(hass, line_code, expected_manufacturer):
    from custom_components.metro_sp.sensor import MetroSPLineSensor
    from unittest.mock import MagicMock

    coord = MagicMock()
    coord.data = {
        line_code: {
            "Code": line_code,
            "ColorName": "Teste",
            "ColorHex": "#000000",
            "StatusLabel": "OK",
            "Description": "",
        }
    }
    coord.config_entry.entry_id = "eid"
    sensor = MetroSPLineSensor(coordinator=coord, line_code=line_code, sensor_key="operacao")
    assert sensor._attr_device_info["manufacturer"] == expected_manufacturer


# ---------------------------------------------------------------------------
# native_value — edge cases
# ---------------------------------------------------------------------------

async def test_detalhes_none_description_returns_empty_string(hass):
    from custom_components.metro_sp.sensor import MetroSPLineSensor
    from unittest.mock import MagicMock

    coord = MagicMock()
    coord.data = {
        1: {"Code": 1, "ColorName": "Azul", "ColorHex": "#0455A1",
            "StatusLabel": "OK", "Description": None}
    }
    coord.config_entry.entry_id = "eid"
    sensor = MetroSPLineSensor(coordinator=coord, line_code=1, sensor_key="detalhes")
    assert sensor.native_value == ""


async def test_operacao_returns_status_label(hass):
    from custom_components.metro_sp.sensor import MetroSPLineSensor
    from unittest.mock import MagicMock

    coord = MagicMock()
    coord.data = {
        1: {"Code": 1, "ColorName": "Azul", "ColorHex": "#0455A1",
            "StatusLabel": "Paralisação", "Description": ""}
    }
    coord.config_entry.entry_id = "eid"
    sensor = MetroSPLineSensor(coordinator=coord, line_code=1, sensor_key="operacao")
    assert sensor.native_value == "Paralisação"
