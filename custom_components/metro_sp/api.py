"""Metrô SP API Client."""

from __future__ import annotations

import socket
from typing import Any

import aiohttp
import async_timeout

from .const import API_BASE_URL


class MetroSPApiClientError(Exception):
    """Exception to indicate a general API error."""


class MetroSPApiClientCommunicationError(MetroSPApiClientError):
    """Exception to indicate a communication error."""


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """Verify that the response is valid."""
    response.raise_for_status()


class MetroSPApiClient:
    """Metrô SP API Client."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Initialize."""
        self._session = session

    async def async_get_lines(self) -> list[dict[str, Any]]:
        """Get all lines status from the API."""
        result = await self._api_wrapper(method="get", url=f"{API_BASE_URL}/lines")
        return result["Data"]

    async def _api_wrapper(self, method: str, url: str) -> Any:
        """Perform an HTTP request."""
        try:
            async with async_timeout.timeout(10):
                response = await self._session.request(method=method, url=url)
                _verify_response_or_raise(response)
                return await response.json()

        except TimeoutError as exception:
            msg = f"Timeout error fetching information - {exception}"
            raise MetroSPApiClientCommunicationError(msg) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information - {exception}"
            raise MetroSPApiClientCommunicationError(msg) from exception
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Something really wrong happened! - {exception}"
            raise MetroSPApiClientError(msg) from exception
