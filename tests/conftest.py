"""Shared fixtures for metro_sp tests."""

from __future__ import annotations

import copy
from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytest_plugins = "pytest_homeassistant_custom_component"

SAMPLE_LINES = [
    {
        "Code": 1,
        "ColorName": "Azul",
        "ColorHex": "#0455A1",
        "Line": "1",
        "StatusCode": 1,
        "StatusLabel": "Operação Normal",
        "StatusColor": "#00FF00",
        "Description": "Linha operando normalmente.",
    },
    {
        "Code": 3,
        "ColorName": "Vermelha",
        "ColorHex": "#EE372F",
        "Line": "3",
        "StatusCode": 2,
        "StatusLabel": "Velocidade Reduzida",
        "StatusColor": "#FFFF00",
        "Description": "",
    },
]


@pytest.fixture
def sample_lines() -> list[dict]:
    return copy.deepcopy(SAMPLE_LINES)


@pytest.fixture
def sample_data(sample_lines) -> dict[int, dict]:
    return {line["Code"]: line for line in sample_lines}


@pytest.fixture
def enable_custom_integrations(hass):
    """Allow custom integrations to load."""
    from homeassistant.loader import DATA_CUSTOM_COMPONENTS
    hass.data.pop(DATA_CUSTOM_COMPONENTS, None)


@pytest.fixture
def mock_api_client(sample_lines) -> Generator:
    """Patch MetroSPApiClient so it never hits the real API."""
    with patch(
        "custom_components.metro_sp.MetroSPApiClient"
    ) as MockClass:
        instance = MockClass.return_value
        instance.async_get_lines = AsyncMock(return_value=sample_lines)
        yield instance


@pytest.fixture
async def setup_integration(hass, mock_api_client, enable_custom_integrations):
    """Set up the metro_sp integration and return the config entry."""
    from pytest_homeassistant_custom_component.common import MockConfigEntry
    from custom_components.metro_sp.const import DOMAIN

    entry = MockConfigEntry(domain=DOMAIN, data={})
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry
