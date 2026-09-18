"""Cliente da API do Metrô SP."""

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
    """Verifica se a resposta é válida."""
    response.raise_for_status()


class MetroSPApiClient:
    """Cliente da API do Metrô SP."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Inicializa o cliente."""
        self._session = session

    async def async_get_lines(self) -> list[MetroSPLine]:
        """Obtém da API o status de todas as linhas."""
        raw = await self._api_wrapper(method="get", url=f"{API_BASE_URL}/lines")
        payload = cast("MetroSPLinesResponse", raw)
        return list(payload["Data"])

    async def _api_wrapper(self, method: str, url: str) -> JsonObject:
        """Executa uma requisição HTTP e devolve o objeto JSON interpretado."""
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
        except Exception as exception:
            msg = f"Failed to fetch information from the Metrô SP API: {exception}"
            raise MetroSPApiClientError(msg) from exception
