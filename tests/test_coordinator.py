from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.metro_sp.const import DOMAIN
from custom_components.metro_sp.coordinator import (
    FAILURE_GRACE_PERIOD,
    UPDATE_INTERVAL,
    MetroSPDataUpdateCoordinator,
)
from custom_components.metro_sp.exceptions import MetroSPApiClientError


def _make_coordinator(hass, lines=None):
    coord = MetroSPDataUpdateCoordinator(hass=hass)
    client = AsyncMock()
    client.async_get_lines = AsyncMock(return_value=lines or [])
    runtime_data = type("D", (), {"client": client})()
    entry = type("E", (), {"entry_id": "eid", "runtime_data": runtime_data})()
    coord.config_entry = entry
    return coord, client


def test_update_interval_is_one_minute():
    assert timedelta(minutes=1) == UPDATE_INTERVAL


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


async def test_update_data_normalizes_uppercase_color_name(hass, sample_lines):
    # CPTM lines come back with ColorName in all caps; it must be title-cased.
    sample_lines[0]["ColorName"] = "DIAMANTE"
    coord, _ = _make_coordinator(hass, lines=sample_lines)
    result = await coord._async_update_data()
    assert result[1]["ColorName"] == "Diamante"


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


def _utcnow_at(seconds: float) -> datetime:
    return datetime(2026, 1, 1, tzinfo=UTC) + timedelta(seconds=seconds)


_DT_UTIL = "custom_components.metro_sp.coordinator.dt_util.utcnow"


async def test_update_data_keeps_last_data_during_grace_period(hass, sample_lines):
    coord, client = _make_coordinator(hass, lines=sample_lines)
    first = await coord._async_update_data()
    coord.data = first

    client.async_get_lines.side_effect = MetroSPApiClientError("down")
    with patch(_DT_UTIL, return_value=_utcnow_at(0)):
        result = await coord._async_update_data()
    assert result == first


async def test_update_data_keeps_last_data_just_before_grace_expires(
    hass, sample_lines
):
    coord, client = _make_coordinator(hass, lines=sample_lines)
    coord.data = await coord._async_update_data()

    client.async_get_lines.side_effect = MetroSPApiClientError("down")
    with patch(_DT_UTIL, return_value=_utcnow_at(0)):
        await coord._async_update_data()
    just_before = FAILURE_GRACE_PERIOD.total_seconds() - 1
    with patch(_DT_UTIL, return_value=_utcnow_at(just_before)):
        result = await coord._async_update_data()
    assert result == coord.data


async def test_update_data_raises_after_grace_period(hass, sample_lines):
    coord, client = _make_coordinator(hass, lines=sample_lines)
    coord.data = await coord._async_update_data()

    client.async_get_lines.side_effect = MetroSPApiClientError("down")
    with patch(_DT_UTIL, return_value=_utcnow_at(0)):
        await coord._async_update_data()
    with (
        patch(_DT_UTIL, return_value=_utcnow_at(FAILURE_GRACE_PERIOD.total_seconds())),
        pytest.raises(UpdateFailed),
    ):
        await coord._async_update_data()


async def test_update_data_recovery_resets_grace_period(hass, sample_lines):
    coord, client = _make_coordinator(hass, lines=sample_lines)
    coord.data = await coord._async_update_data()

    client.async_get_lines.side_effect = MetroSPApiClientError("down")
    with patch(_DT_UTIL, return_value=_utcnow_at(0)):
        await coord._async_update_data()

    client.async_get_lines.side_effect = None
    coord.data = await coord._async_update_data()

    client.async_get_lines.side_effect = MetroSPApiClientError("down")
    with patch(_DT_UTIL, return_value=_utcnow_at(FAILURE_GRACE_PERIOD.total_seconds())):
        result = await coord._async_update_data()
    assert result == coord.data
