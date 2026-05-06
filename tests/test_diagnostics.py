from __future__ import annotations

from custom_components.metro_sp.diagnostics import (
    async_get_config_entry_diagnostics,
)


async def test_diagnostics_returns_entry_metadata(hass, setup_integration):
    diag = await async_get_config_entry_diagnostics(hass, setup_integration)
    assert diag["entry"]["domain"] == "metro_sp"
    assert diag["entry"]["version"] == 1
    assert "title" in diag["entry"]


async def test_diagnostics_data_section_is_dict(hass, setup_integration):
    diag = await async_get_config_entry_diagnostics(hass, setup_integration)
    assert isinstance(diag["entry"]["data"], dict)


async def test_diagnostics_options_section_is_dict(hass, setup_integration):
    diag = await async_get_config_entry_diagnostics(hass, setup_integration)
    assert isinstance(diag["entry"]["options"], dict)


async def test_diagnostics_includes_coordinator_data(hass, setup_integration):
    diag = await async_get_config_entry_diagnostics(hass, setup_integration)
    assert diag["coordinator_data"] is not None
    assert 1 in diag["coordinator_data"]
    assert diag["coordinator_data"][1]["ColorName"] == "Azul"


async def test_diagnostics_coordinator_data_keys_are_line_codes(
    hass, setup_integration
):
    diag = await async_get_config_entry_diagnostics(hass, setup_integration)
    assert set(diag["coordinator_data"].keys()) == {1, 3}
