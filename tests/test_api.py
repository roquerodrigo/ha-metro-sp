"""Tests for the API client."""

from __future__ import annotations

import socket
from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest

from custom_components.metro_sp.api import (
    MetroSPApiClient,
    MetroSPApiClientCommunicationError,
    MetroSPApiClientError,
    _verify_response_or_raise,
)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _make_session(payload=None, side_effect=None):
    """Return a session mock whose request() is an AsyncMock."""
    response = AsyncMock()
    response.raise_for_status = MagicMock()
    response.json = AsyncMock(return_value=payload or {})

    session = MagicMock()
    if side_effect is not None:
        session.request = AsyncMock(side_effect=side_effect)
    else:
        session.request = AsyncMock(return_value=response)
    return session, response


# ---------------------------------------------------------------------------
# Exceptions hierarchy
# ---------------------------------------------------------------------------


def test_communication_error_is_api_error():
    assert issubclass(MetroSPApiClientCommunicationError, MetroSPApiClientError)


def test_api_error_is_exception():
    assert issubclass(MetroSPApiClientError, Exception)


# ---------------------------------------------------------------------------
# _verify_response_or_raise
# ---------------------------------------------------------------------------


def test_verify_response_calls_raise_for_status():
    response = MagicMock()
    _verify_response_or_raise(response)
    response.raise_for_status.assert_called_once()


def test_verify_response_propagates_http_error():
    response = MagicMock()
    response.raise_for_status.side_effect = aiohttp.ClientResponseError(
        request_info=MagicMock(), history=()
    )
    with pytest.raises(aiohttp.ClientResponseError):
        _verify_response_or_raise(response)


# ---------------------------------------------------------------------------
# MetroSPApiClient.async_get_lines — happy path
# ---------------------------------------------------------------------------


async def test_async_get_lines_returns_data(sample_lines):
    session, _ = _make_session({"Data": sample_lines})
    client = MetroSPApiClient(session=session)
    result = await client.async_get_lines()

    assert result == sample_lines


async def test_async_get_lines_uses_correct_url():
    from custom_components.metro_sp.const import API_BASE_URL

    session, _ = _make_session({"Data": []})
    client = MetroSPApiClient(session=session)
    await client.async_get_lines()

    call_kwargs = session.request.call_args.kwargs
    assert call_kwargs["url"] == f"{API_BASE_URL}/lines"
    assert call_kwargs["method"] == "get"


async def test_async_get_lines_calls_request_once(sample_lines):
    session, _ = _make_session({"Data": sample_lines})
    client = MetroSPApiClient(session=session)
    await client.async_get_lines()

    session.request.assert_awaited_once()


# ---------------------------------------------------------------------------
# MetroSPApiClient._api_wrapper — error paths
# ---------------------------------------------------------------------------


async def test_api_wrapper_raises_communication_error_on_timeout():
    session, _ = _make_session(side_effect=TimeoutError("timed out"))
    client = MetroSPApiClient(session=session)

    with pytest.raises(MetroSPApiClientCommunicationError, match="Timeout"):
        await client._api_wrapper(method="get", url="http://x")


async def test_api_wrapper_raises_communication_error_on_client_error():
    session, _ = _make_session(
        side_effect=aiohttp.ClientError("connection refused")
    )
    client = MetroSPApiClient(session=session)

    with pytest.raises(MetroSPApiClientCommunicationError, match="Error fetching"):
        await client._api_wrapper(method="get", url="http://x")


async def test_api_wrapper_raises_communication_error_on_socket_error():
    session, _ = _make_session(side_effect=socket.gaierror("dns failed"))
    client = MetroSPApiClient(session=session)

    with pytest.raises(MetroSPApiClientCommunicationError, match="Error fetching"):
        await client._api_wrapper(method="get", url="http://x")


async def test_api_wrapper_raises_api_error_on_unexpected_exception():
    session, _ = _make_session(side_effect=RuntimeError("boom"))
    client = MetroSPApiClient(session=session)

    with pytest.raises(MetroSPApiClientError, match="Something really wrong"):
        await client._api_wrapper(method="get", url="http://x")


async def test_api_wrapper_raises_api_error_on_http_status_error():
    session, response = _make_session()
    response.raise_for_status.side_effect = aiohttp.ClientResponseError(
        request_info=MagicMock(), history=()
    )
    client = MetroSPApiClient(session=session)

    with pytest.raises(MetroSPApiClientError):
        await client._api_wrapper(method="get", url="http://x")


async def test_api_wrapper_returns_json_on_success():
    payload = {"Data": [{"Code": 1}]}
    session, _ = _make_session(payload)
    client = MetroSPApiClient(session=session)

    result = await client._api_wrapper(method="get", url="http://x")
    assert result == payload
