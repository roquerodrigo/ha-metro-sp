from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from custom_components.metro_sp.sensor import MetroSPLineSensor


def _sensor(line_data: dict, sensor_key: str) -> MetroSPLineSensor:
    line_code = line_data["Code"]
    coord = MagicMock()
    coord.data = {line_code: line_data}
    coord.config_entry.entry_id = "eid"
    return MetroSPLineSensor(
        coordinator=coord, line_code=line_code, sensor_key=sensor_key
    )


def _line(
    code=1, color_name="Azul", color_hex="#0455A1", status_label="OK", description=""
):
    return {
        "Code": code,
        "ColorName": color_name,
        "ColorHex": color_hex,
        "StatusLabel": status_label,
        "Description": description,
    }


async def test_sensor_count(hass, setup_integration):
    assert len(hass.states.async_all("sensor")) == 4


async def test_operacao_state_value(hass, setup_integration):
    assert (
        hass.states.get("sensor.metro_sp_linha_1_azul_operacao").state
        == "Operação Normal"
    )


async def test_detalhes_state_value(hass, setup_integration):
    assert (
        hass.states.get("sensor.metro_sp_linha_1_azul_detalhes").state
        == "Linha operando normalmente."
    )


async def test_detalhes_empty_description(hass, setup_integration):
    assert hass.states.get("sensor.metro_sp_linha_3_vermelha_detalhes").state == ""


async def test_operacao_attributes_keys(hass, setup_integration):
    attrs = hass.states.get("sensor.metro_sp_linha_1_azul_operacao").attributes
    assert {
        "status_code",
        "status_color",
        "color_name",
        "color_hex",
        "line_code",
    } <= set(attrs)


async def test_operacao_attributes_values(hass, setup_integration):
    attrs = hass.states.get("sensor.metro_sp_linha_1_azul_operacao").attributes
    assert attrs["status_code"] == 1
    assert attrs["color_name"] == "Azul"
    assert attrs["color_hex"] == "#0455A1"
    assert attrs["line_code"] == 1
    assert attrs["status_color"] == "#00FF00"


def test_entity_picture_uses_static_path():
    sensor = _sensor(_line(code=1, color_name="Azul"), "operacao")
    assert sensor.entity_picture == "/api/metro_sp/lines/linha_1_azul.png"


def test_entity_picture_slugifies_color_name():
    sensor = _sensor(_line(code=5, color_name="Lilás"), "operacao")
    assert sensor.entity_picture == "/api/metro_sp/lines/linha_5_lilas.png"


def test_icon_is_mdi_subway():
    assert _sensor(_line(), "operacao").icon == "mdi:subway"


def test_detalhes_none_description_returns_empty_string():
    assert _sensor(_line(description=None), "detalhes").native_value == ""


def test_operacao_returns_status_label():
    assert (
        _sensor(_line(status_label="Paralisação"), "operacao").native_value
        == "Paralisação"
    )


@pytest.mark.parametrize(
    ("line_code", "expected_manufacturer"),
    [
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
    ],
)
def test_operator_mapping(line_code, expected_manufacturer):
    sensor = _sensor(_line(code=line_code), "operacao")
    assert sensor._attr_device_info["manufacturer"] == expected_manufacturer
