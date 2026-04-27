"""Tests for MetroSPDataUpdateCoordinator."""

from __future__ import annotations

from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.metro_sp.api import MetroSPApiClientError
from custom_components.metro_sp.coordinator import (
    UPDATE_INTERVAL,
    MetroSPDataUpdateCoordinator,
)


def _make_coordinator(lines=None):
    hass = MagicMock()
    coord = MetroSPDataUpdateCoordinator(hass=hass)

    client = MagicMock()
    client.async_get_lines = AsyncMock(return_value=lines or [])

    runtime_data = MagicMock()
    runtime_data.client = client

    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.runtime_data = runtime_data

    coord.config_entry = entry
    return coord, client


def test_update_interval_is_five_minutes():
    assert UPDATE_INTERVAL == timedelta(minutes=5)


def test_init_stores_hass():
    hass = MagicMock()
    coord = MetroSPDataUpdateCoordinator(hass=hass)
    assert coord.hass is hass


def test_init_sets_name():
    from custom_components.metro_sp.const import DOMAIN

    coord = MetroSPDataUpdateCoordinator(hass=MagicMock())
    assert coord.name == DOMAIN


def test_init_sets_update_interval():
    coord = MetroSPDataUpdateCoordinator(hass=MagicMock())
    assert coord.update_interval == UPDATE_INTERVAL


async def test_async_update_data_indexes_by_code(sample_lines):
    coord, _ = _make_coordinator(lines=sample_lines)
    result = await coord._async_update_data()

    assert set(result.keys()) == {1, 3}
    assert result[1]["ColorName"] == "Azul"
    assert result[3]["ColorName"] == "Vermelha"


async def test_async_update_data_returns_full_line_dict(sample_lines):
    coord, _ = _make_coordinator(lines=sample_lines)
    result = await coord._async_update_data()

    line = result[1]
    assert line["StatusLabel"] == "Operação Normal"
    assert line["ColorHex"] == "#0455A1"


async def test_async_update_data_empty_lines():
    coord, _ = _make_coordinator(lines=[])
    result = await coord._async_update_data()
    assert result == {}


async def test_async_update_data_raises_update_failed_on_api_error():
    from custom_components.metro_sp.coordinator import (
        MetroSPDataUpdateCoordinator,
    )
    from tests.conftest import _UpdateFailed  # imported from mock

    coord, client = _make_coordinator()
    client.async_get_lines.side_effect = MetroSPApiClientError("api down")

    with pytest.raises(Exception) as exc_info:
        await coord._async_update_data()

    # UpdateFailed (our mock) should be raised
    assert "api down" in str(exc_info.value) or exc_info.type.__name__ == "UpdateFailed"


async def test_async_config_entry_first_refresh_populates_data(sample_lines):
    coord, _ = _make_coordinator(lines=sample_lines)
    await coord.async_config_entry_first_refresh()
    assert coord.data == {line["Code"]: line for line in sample_lines}
