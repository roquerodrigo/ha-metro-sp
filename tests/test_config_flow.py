from __future__ import annotations

from unittest.mock import AsyncMock, patch

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType

from custom_components.metro_sp.api import (
    MetroSPApiClientCommunicationError,
    MetroSPApiClientError,
)
from custom_components.metro_sp.const import DOMAIN


async def _start_flow(hass):
    return await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )


async def test_step_user_shows_form(hass, enable_custom_integrations):
    result = await _start_flow(hass)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"


async def test_step_user_success_creates_entry(hass, enable_custom_integrations):
    with patch("custom_components.metro_sp.config_flow.MetroSPApiClient") as mock:
        mock.return_value.async_get_lines = AsyncMock(return_value=[])
        result = await _start_flow(hass)
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input={}
        )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Metrô SP"
    assert result["data"] == {}


async def test_step_user_success_sets_unique_id(hass, enable_custom_integrations):
    with patch("custom_components.metro_sp.config_flow.MetroSPApiClient") as mock:
        mock.return_value.async_get_lines = AsyncMock(return_value=[])
        await _start_flow(hass)
        await hass.config_entries.flow.async_configure(
            (await _start_flow(hass))["flow_id"], user_input={}
        )
    entry = hass.config_entries.async_entries(DOMAIN)[0]
    assert entry.unique_id == DOMAIN


async def test_step_user_duplicate_aborts(hass, enable_custom_integrations):
    with patch("custom_components.metro_sp.config_flow.MetroSPApiClient") as mock:
        mock.return_value.async_get_lines = AsyncMock(return_value=[])
        flow1 = await _start_flow(hass)
        await hass.config_entries.flow.async_configure(flow1["flow_id"], user_input={})
        flow2 = await _start_flow(hass)
        result = await hass.config_entries.flow.async_configure(
            flow2["flow_id"], user_input={}
        )
    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_step_user_communication_error_shows_connection_error(
    hass, enable_custom_integrations
):
    with patch("custom_components.metro_sp.config_flow.MetroSPApiClient") as mock:
        mock.return_value.async_get_lines = AsyncMock(
            side_effect=MetroSPApiClientCommunicationError("down")
        )
        result = await _start_flow(hass)
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input={}
        )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"]["base"] == "connection"


async def test_step_user_generic_error_shows_unknown_error(
    hass, enable_custom_integrations
):
    with patch("custom_components.metro_sp.config_flow.MetroSPApiClient") as mock:
        mock.return_value.async_get_lines = AsyncMock(
            side_effect=MetroSPApiClientError("oops")
        )
        result = await _start_flow(hass)
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input={}
        )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"]["base"] == "unknown"


async def test_flow_version(hass, enable_custom_integrations):
    result = await _start_flow(hass)
    assert result["type"] == FlowResultType.FORM
    flow = hass.config_entries.flow.async_get(result["flow_id"])
    assert flow["handler"] == DOMAIN
