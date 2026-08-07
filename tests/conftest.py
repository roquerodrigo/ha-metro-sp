from __future__ import annotations

import copy
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, patch

import pytest

if TYPE_CHECKING:
    from collections.abc import Generator

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
def sample_data(sample_lines: list[dict]) -> dict[int, dict]:
    return {line["Code"]: line for line in sample_lines}


@pytest.fixture
def enable_custom_integrations(hass) -> None:
    from homeassistant.loader import DATA_CUSTOM_COMPONENTS

    hass.data.pop(DATA_CUSTOM_COMPONENTS, None)


@pytest.fixture
def mock_api_client(sample_lines: list[dict]) -> Generator:
    with patch("custom_components.metro_sp.MetroSPApiClient") as mock_class:
        instance = mock_class.return_value
        instance.async_get_lines = AsyncMock(return_value=sample_lines)
        yield instance


@pytest.fixture
async def setup_integration(hass, mock_api_client, enable_custom_integrations):
    from homeassistant.components.frontend import DATA_EXTRA_MODULE_URL, UrlManager
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    from custom_components.metro_sp.const import DOMAIN

    # metro_sp registers its Lovelace card as a dashboard resource, falling
    # back to add_extra_js_url when Lovelace storage is unavailable. The full
    # frontend component can't be set up in this minimal harness, so seed just
    # the store add_extra_js_url writes to (frontend does the same at setup).
    hass.data.setdefault(DATA_EXTRA_MODULE_URL, UrlManager(lambda *_: None, []))

    entry = MockConfigEntry(domain=DOMAIN, data={})
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry
