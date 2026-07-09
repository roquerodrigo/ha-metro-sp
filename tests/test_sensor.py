from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from custom_components.metro_sp.sensor import MetroSPLineSensor


def _sensor(line_data: dict) -> MetroSPLineSensor:
    line_code = line_data["Code"]
    coord = MagicMock()
    coord.data = {line_code: line_data}
    coord.config_entry.entry_id = "eid"
    return MetroSPLineSensor(coordinator=coord, line_code=line_code)


def _line(  # noqa: PLR0913
    *,
    code=1,
    color_name="Azul",
    color_hex="#0455A1",
    status_label="OK",
    description="",
    status_code=1,
    status_color="#00FF00",
    line_str="1",
):
    return {
        "Code": code,
        "ColorName": color_name,
        "ColorHex": color_hex,
        "Line": line_str,
        "StatusCode": status_code,
        "StatusLabel": status_label,
        "StatusColor": status_color,
        "Description": description,
    }


async def test_sensor_count(hass, setup_integration):
    assert len(hass.states.async_all("sensor")) == 2


async def test_operacao_state_value(hass, setup_integration):
    assert (
        hass.states.get("sensor.metro_sp_linha_1_azul_operacao").state
        == "Operação Normal"
    )


async def test_operacao_description_attribute_value(hass, setup_integration):
    attrs = hass.states.get("sensor.metro_sp_linha_1_azul_operacao").attributes
    assert attrs["description"] == "Linha operando normalmente."


async def test_description_attribute_falls_back_to_status_label(
    hass, setup_integration
):
    attrs = hass.states.get("sensor.metro_sp_linha_3_vermelha_operacao").attributes
    assert attrs["description"] == "Velocidade Reduzida"


async def test_operacao_attributes_keys(hass, setup_integration):
    attrs = hass.states.get("sensor.metro_sp_linha_1_azul_operacao").attributes
    assert {
        "status_code",
        "status_color",
        "color_name",
        "color_hex",
        "line_code",
        "description",
    } <= set(attrs)


async def test_operacao_attributes_values(hass, setup_integration):
    attrs = hass.states.get("sensor.metro_sp_linha_1_azul_operacao").attributes
    assert attrs["status_code"] == 1
    assert attrs["color_name"] == "Azul"
    assert attrs["color_hex"] == "#0455A1"
    assert attrs["line_code"] == 1
    assert attrs["status_color"] == "#00FF00"


def test_entity_picture_points_to_local_static_file():
    assert _sensor(_line(code=4)).entity_picture == "/metro_sp/linha_4.png"


def test_icon_is_mdi_subway():
    assert _sensor(_line()).icon == "mdi:subway"


def test_native_value_returns_status_label():
    assert _sensor(_line(status_label="Paralisação")).native_value == "Paralisação"


def test_description_attribute_returns_description_when_present():
    attrs = _sensor(
        _line(description="Linha operando normalmente.")
    ).extra_state_attributes
    assert attrs["description"] == "Linha operando normalmente."


def test_description_attribute_falls_back_when_none():
    attrs = _sensor(
        _line(status_label="Paralisação", description=None)
    ).extra_state_attributes
    assert attrs["description"] == "Paralisação"


def test_description_attribute_falls_back_when_empty_string():
    attrs = _sensor(
        _line(status_label="Velocidade Reduzida", description="")
    ).extra_state_attributes
    assert attrs["description"] == "Velocidade Reduzida"


def test_description_attribute_accepts_text_longer_than_state_limit():
    long_description = "x" * 600
    attrs = _sensor(_line(description=long_description)).extra_state_attributes
    assert attrs["description"] == long_description


def test_device_info_includes_entry_id_and_line_code():
    info = _sensor(_line(code=4)).device_info
    assert info is not None
    assert any("eid_4" in str(i) for i in info["identifiers"])


def test_device_info_name_uses_color_titlecased():
    sensor = _sensor(_line(code=3, color_name="vermelha"))
    assert sensor.device_info["name"] == "Linha 3 - Vermelha"


@pytest.mark.parametrize(
    ("line_code", "expected_manufacturer"),
    [
        (1, "Metrô SP"),
        (2, "Metrô SP"),
        (3, "Metrô SP"),
        (4, "ViaQuatro"),
        (5, "ViaMobilidade"),
        (6, "Linha Uni"),
        (7, "TIC Trens"),
        (8, "ViaMobilidade"),
        (9, "ViaMobilidade"),
        (10, "CPTM"),
        (11, "Trivia Trens"),
        (12, "Trivia Trens"),
        (13, "Trivia Trens"),
        (15, "Metrô SP"),
        (17, "ViaMobilidade"),
        (99, "Metrô SP / CPTM"),
    ],
)
def test_operator_mapping(line_code, expected_manufacturer):
    sensor = _sensor(_line(code=line_code))
    assert sensor.device_info["manufacturer"] == expected_manufacturer
