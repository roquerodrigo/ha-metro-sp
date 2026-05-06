"""Metrô SP API Client."""

from __future__ import annotations

import asyncio
import socket
from typing import TYPE_CHECKING, cast

import aiohttp

from .const import API_BASE_URL
from .exceptions import (
    MetroSPApiClientCommunicationError,
    MetroSPApiClientError,
)

if TYPE_CHECKING:
    from .data import JsonObject, MetroSPLine, MetroSPLinesResponse


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """Verify that the response is valid."""
    response.raise_for_status()


class MetroSPApiClient:
    """Metrô SP API Client."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Initialize."""
        self._session = session

    async def async_get_lines(self) -> list[MetroSPLine]:
        """Get all lines status from the API."""
        raw = await self._api_wrapper(method="get", url=f"{API_BASE_URL}/lines")
        payload = cast("MetroSPLinesResponse", raw)
        return list(payload["Data"])

    async def _api_wrapper(self, method: str, url: str) -> JsonObject:
        """Perform an HTTP request and return the parsed JSON object."""
        try:
            async with asyncio.timeout(10):
                response = await self._session.request(method=method, url=url)
                _verify_response_or_raise(response)
                return cast("JsonObject", await response.json())

        except TimeoutError as exception:
            msg = f"Timeout error fetching information - {exception}"
            raise MetroSPApiClientCommunicationError(msg) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information - {exception}"
            raise MetroSPApiClientCommunicationError(msg) from exception
        except MetroSPApiClientError:
            raise
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Something really wrong happened! - {exception}"
            raise MetroSPApiClientError(msg) from exception
