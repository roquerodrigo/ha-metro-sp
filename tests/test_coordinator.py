from __future__ import annotations

from datetime import timedelta
from unittest.mock import AsyncMock

import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.metro_sp.api import MetroSPApiClientError
from custom_components.metro_sp.const import DOMAIN
from custom_components.metro_sp.coordinator import (
    UPDATE_INTERVAL,
    MetroSPDataUpdateCoordinator,
)


def _make_coordinator(hass, lines=None):
    coord = MetroSPDataUpdateCoordinator(hass=hass)
    client = AsyncMock()
    client.async_get_lines = AsyncMock(return_value=lines or [])
    runtime_data = type("D", (), {"client": client})()
    entry = type("E", (), {"entry_id": "eid", "runtime_data": runtime_data})()
    coord.config_entry = entry
    return coord, client


def test_update_interval_is_five_minutes():
    assert timedelta(minutes=5) == UPDATE_INTERVAL


def test_init_sets_domain_name(hass):
    assert MetroSPDataUpdateCoordinator(hass=hass).name == DOMAIN


def test_init_sets_update_interval(hass):
    assert MetroSPDataUpdateCoordinator(hass=hass).update_interval == UPDATE_INTERVAL


async def test_update_data_indexes_by_code(hass, sample_lines):
    coord, _ = _make_coordinator(hass, lines=sample_lines)
    result = await coord._async_update_data()
    assert set(result.keys()) == {1, 3}
    assert result[1]["ColorName"] == "Azul"
    assert result[3]["ColorName"] == "Vermelha"


async def test_update_data_returns_full_line_dict(hass, sample_lines):
    coord, _ = _make_coordinator(hass, lines=sample_lines)
    result = await coord._async_update_data()
    assert result[1]["StatusLabel"] == "Operação Normal"
    assert result[1]["ColorHex"] == "#0455A1"


async def test_update_data_empty_lines(hass):
    coord, _ = _make_coordinator(hass, lines=[])
    assert await coord._async_update_data() == {}


async def test_update_data_raises_update_failed_on_api_error(hass):
    coord, client = _make_coordinator(hass)
    client.async_get_lines.side_effect = MetroSPApiClientError("down")
    with pytest.raises(UpdateFailed):
        await coord._async_update_data()


async def test_update_data_preserves_all_line_fields(hass, sample_lines):
    coord, _ = _make_coordinator(hass, lines=sample_lines)
    result = await coord._async_update_data()
    for key in (
        "Code",
        "ColorName",
        "ColorHex",
        "StatusCode",
        "StatusLabel",
        "Description",
    ):
        assert key in result[1]
