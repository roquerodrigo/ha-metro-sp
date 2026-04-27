"""Tests for MetroSPFlowHandler config flow."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.metro_sp.api import (
    MetroSPApiClientCommunicationError,
    MetroSPApiClientError,
)
from custom_components.metro_sp.config_flow import MetroSPFlowHandler


def _make_flow() -> MetroSPFlowHandler:
    flow = MetroSPFlowHandler()
    flow.hass = MagicMock()
    return flow


# ---------------------------------------------------------------------------
# async_step_user with None input (first visit)
# ---------------------------------------------------------------------------


async def test_step_user_none_shows_form():
    flow = _make_flow()
    result = await flow.async_step_user(user_input=None)
    assert result["type"] == "form"
    assert result["step_id"] == "user"
    assert result["errors"] == {}


# ---------------------------------------------------------------------------
# async_step_user with user_input (connectivity test)
# ---------------------------------------------------------------------------


async def test_step_user_success_creates_entry():
    flow = _make_flow()
    flow.async_set_unique_id = AsyncMock()
    flow._abort_if_unique_id_configured = MagicMock()
    flow.async_create_entry = MagicMock(
        return_value={"type": "create_entry", "title": "Metrô SP", "data": {}}
    )

    with patch(
        "custom_components.metro_sp.config_flow.MetroSPApiClient"
    ) as MockClient:
        instance = MockClient.return_value
        instance.async_get_lines = AsyncMock(return_value=[])

        result = await flow.async_step_user(user_input={})

    assert result["type"] == "create_entry"
    assert result["title"] == "Metrô SP"
    assert result["data"] == {}


async def test_step_user_success_sets_unique_id():
    from custom_components.metro_sp.const import DOMAIN

    flow = _make_flow()
    flow.async_set_unique_id = AsyncMock()
    flow._abort_if_unique_id_configured = MagicMock()
    flow.async_create_entry = MagicMock(
        return_value={"type": "create_entry", "title": "Metrô SP", "data": {}}
    )

    with patch("custom_components.metro_sp.config_flow.MetroSPApiClient") as MockClient:
        instance = MockClient.return_value
        instance.async_get_lines = AsyncMock(return_value=[])
        await flow.async_step_user(user_input={})

    flow.async_set_unique_id.assert_awaited_once_with(DOMAIN)


async def test_step_user_communication_error_shows_connection_error():
    flow = _make_flow()

    with patch("custom_components.metro_sp.config_flow.MetroSPApiClient") as MockClient:
        instance = MockClient.return_value
        instance.async_get_lines = AsyncMock(
            side_effect=MetroSPApiClientCommunicationError("network down")
        )
        result = await flow.async_step_user(user_input={})

    assert result["type"] == "form"
    assert result["errors"]["base"] == "connection"


async def test_step_user_generic_api_error_shows_unknown_error():
    flow = _make_flow()

    with patch("custom_components.metro_sp.config_flow.MetroSPApiClient") as MockClient:
        instance = MockClient.return_value
        instance.async_get_lines = AsyncMock(
            side_effect=MetroSPApiClientError("unexpected")
        )
        result = await flow.async_step_user(user_input={})

    assert result["type"] == "form"
    assert result["errors"]["base"] == "unknown"


async def test_step_user_empty_input_triggers_api_call():
    flow = _make_flow()
    flow.async_set_unique_id = AsyncMock()
    flow._abort_if_unique_id_configured = MagicMock()
    flow.async_create_entry = MagicMock(
        return_value={"type": "create_entry", "title": "Metrô SP", "data": {}}
    )

    with patch("custom_components.metro_sp.config_flow.MetroSPApiClient") as MockClient:
        instance = MockClient.return_value
        instance.async_get_lines = AsyncMock(return_value=[])
        await flow.async_step_user(user_input={})

    instance.async_get_lines.assert_awaited_once()


async def test_flow_version():
    assert MetroSPFlowHandler.VERSION == 1
