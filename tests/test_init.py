"""Tests for integration setup, unload and reload."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from homeassistant.config_entries import ConfigEntryState

from custom_components.metro_sp.const import DOMAIN


# ---------------------------------------------------------------------------
# async_setup_entry
# ---------------------------------------------------------------------------

async def test_setup_entry_loads_successfully(hass, setup_integration):
    entry = setup_integration
    assert entry.state == ConfigEntryState.LOADED


async def test_setup_entry_creates_sensor_entities(hass, setup_integration):
    states = hass.states.async_all("sensor")
    # 2 sample lines × 2 sensors each = 4
    assert len(states) == 4


async def test_setup_entry_sensor_entity_ids(hass, setup_integration):
    entity_ids = {s.entity_id for s in hass.states.async_all("sensor")}
    assert "sensor.metro_sp_linha_1_azul_operacao" in entity_ids
    assert "sensor.metro_sp_linha_1_azul_detalhes" in entity_ids
    assert "sensor.metro_sp_linha_3_vermelha_operacao" in entity_ids
    assert "sensor.metro_sp_linha_3_vermelha_detalhes" in entity_ids


async def test_setup_entry_operacao_state(hass, setup_integration):
    state = hass.states.get("sensor.metro_sp_linha_1_azul_operacao")
    assert state is not None
    assert state.state == "Operação Normal"


async def test_setup_entry_detalhes_state(hass, setup_integration):
    state = hass.states.get("sensor.metro_sp_linha_1_azul_detalhes")
    assert state is not None
    assert state.state == "Linha operando normalmente."


async def test_setup_entry_registers_update_listener(hass, setup_integration):
    entry = setup_integration
    assert len(entry.update_listeners) == 1


# ---------------------------------------------------------------------------
# async_unload_entry
# ---------------------------------------------------------------------------

async def test_unload_entry_succeeds(hass, setup_integration):
    entry = setup_integration
    assert await hass.config_entries.async_unload(entry.entry_id)
    assert entry.state == ConfigEntryState.NOT_LOADED


async def test_unload_entry_makes_entities_unavailable(hass, setup_integration):
    entry = setup_integration
    await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    for state in hass.states.async_all("sensor"):
        assert state.state == "unavailable"


# ---------------------------------------------------------------------------
# async_reload_entry
# ---------------------------------------------------------------------------

async def test_reload_entry_restores_loaded_state(hass, setup_integration, mock_api_client):
    entry = setup_integration
    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state == ConfigEntryState.LOADED


async def test_async_reload_entry_calls_reload(hass, setup_integration, mock_api_client):
    from custom_components.metro_sp import async_reload_entry

    entry = setup_integration
    await async_reload_entry(hass, entry)
    await hass.async_block_till_done()
    assert entry.state == ConfigEntryState.LOADED
