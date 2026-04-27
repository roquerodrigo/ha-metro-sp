"""Tests for integration __init__.py setup/unload/reload."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def _make_hass_and_entry(api_lines=None):
    hass = MagicMock()
    hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=True)
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
    hass.config_entries.async_reload = AsyncMock()

    entry = MagicMock()
    entry.domain = "metro_sp"
    entry.entry_id = "test_entry_id"
    entry.async_on_unload = MagicMock()
    entry.add_update_listener = MagicMock(return_value=MagicMock())

    return hass, entry


# ---------------------------------------------------------------------------
# async_setup_entry
# ---------------------------------------------------------------------------


async def test_async_setup_entry_returns_true(sample_lines):
    from custom_components.metro_sp import async_setup_entry

    hass, entry = _make_hass_and_entry()

    with (
        patch(
            "custom_components.metro_sp.async_get_clientsession",
            return_value=MagicMock(),
        ),
        patch(
            "custom_components.metro_sp.async_get_loaded_integration",
            new_callable=lambda: lambda *a, **k: MagicMock(),
        ),
        patch(
            "custom_components.metro_sp.MetroSPApiClient"
        ) as MockApiClient,
        patch(
            "custom_components.metro_sp.MetroSPDataUpdateCoordinator"
        ) as MockCoord,
    ):
        coord_instance = MagicMock()
        coord_instance.async_config_entry_first_refresh = AsyncMock()
        MockCoord.return_value = coord_instance

        result = await async_setup_entry(hass, entry)

    assert result is True


async def test_async_setup_entry_creates_coordinator(sample_lines):
    from custom_components.metro_sp import async_setup_entry

    hass, entry = _make_hass_and_entry()

    with (
        patch("custom_components.metro_sp.async_get_clientsession", return_value=MagicMock()),
        patch("custom_components.metro_sp.async_get_loaded_integration", return_value=MagicMock()),
        patch("custom_components.metro_sp.MetroSPApiClient"),
        patch("custom_components.metro_sp.MetroSPDataUpdateCoordinator") as MockCoord,
    ):
        coord_instance = MagicMock()
        coord_instance.async_config_entry_first_refresh = AsyncMock()
        MockCoord.return_value = coord_instance

        await async_setup_entry(hass, entry)

    MockCoord.assert_called_once_with(hass=hass)


async def test_async_setup_entry_calls_first_refresh():
    from custom_components.metro_sp import async_setup_entry

    hass, entry = _make_hass_and_entry()

    with (
        patch("custom_components.metro_sp.async_get_clientsession", return_value=MagicMock()),
        patch("custom_components.metro_sp.async_get_loaded_integration", return_value=MagicMock()),
        patch("custom_components.metro_sp.MetroSPApiClient"),
        patch("custom_components.metro_sp.MetroSPDataUpdateCoordinator") as MockCoord,
    ):
        coord_instance = MagicMock()
        coord_instance.async_config_entry_first_refresh = AsyncMock()
        MockCoord.return_value = coord_instance

        await async_setup_entry(hass, entry)

    coord_instance.async_config_entry_first_refresh.assert_awaited_once()


async def test_async_setup_entry_forwards_sensor_platform():
    from custom_components.metro_sp import async_setup_entry, PLATFORMS

    hass, entry = _make_hass_and_entry()

    with (
        patch("custom_components.metro_sp.async_get_clientsession", return_value=MagicMock()),
        patch("custom_components.metro_sp.async_get_loaded_integration", return_value=MagicMock()),
        patch("custom_components.metro_sp.MetroSPApiClient"),
        patch("custom_components.metro_sp.MetroSPDataUpdateCoordinator") as MockCoord,
    ):
        coord_instance = MagicMock()
        coord_instance.async_config_entry_first_refresh = AsyncMock()
        MockCoord.return_value = coord_instance

        await async_setup_entry(hass, entry)

    hass.config_entries.async_forward_entry_setups.assert_awaited_once_with(entry, PLATFORMS)


async def test_async_setup_entry_registers_update_listener():
    from custom_components.metro_sp import async_setup_entry

    hass, entry = _make_hass_and_entry()

    with (
        patch("custom_components.metro_sp.async_get_clientsession", return_value=MagicMock()),
        patch("custom_components.metro_sp.async_get_loaded_integration", return_value=MagicMock()),
        patch("custom_components.metro_sp.MetroSPApiClient"),
        patch("custom_components.metro_sp.MetroSPDataUpdateCoordinator") as MockCoord,
    ):
        coord_instance = MagicMock()
        coord_instance.async_config_entry_first_refresh = AsyncMock()
        MockCoord.return_value = coord_instance

        await async_setup_entry(hass, entry)

    entry.add_update_listener.assert_called_once()
    entry.async_on_unload.assert_called_once()


# ---------------------------------------------------------------------------
# async_unload_entry
# ---------------------------------------------------------------------------


async def test_async_unload_entry_returns_true():
    from custom_components.metro_sp import async_unload_entry, PLATFORMS

    hass, entry = _make_hass_and_entry()
    result = await async_unload_entry(hass, entry)

    assert result is True
    hass.config_entries.async_unload_platforms.assert_awaited_once_with(entry, PLATFORMS)


async def test_async_unload_entry_returns_false_when_platform_fails():
    from custom_components.metro_sp import async_unload_entry

    hass, entry = _make_hass_and_entry()
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=False)

    result = await async_unload_entry(hass, entry)
    assert result is False


# ---------------------------------------------------------------------------
# async_reload_entry
# ---------------------------------------------------------------------------


async def test_async_reload_entry_calls_reload():
    from custom_components.metro_sp import async_reload_entry

    hass, entry = _make_hass_and_entry()
    entry.entry_id = "my_entry_id"

    await async_reload_entry(hass, entry)

    hass.config_entries.async_reload.assert_awaited_once_with("my_entry_id")


# ---------------------------------------------------------------------------
# PLATFORMS constant
# ---------------------------------------------------------------------------


def test_platforms_contains_sensor():
    from custom_components.metro_sp import PLATFORMS

    platform_values = [str(p) for p in PLATFORMS]
    assert any("sensor" in v.lower() for v in platform_values)
