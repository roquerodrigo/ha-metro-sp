"""Config flow do Metrô SP."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import MetroSPApiClient
from .const import DOMAIN, LOGGER
from .exceptions import (
    MetroSPApiClientCommunicationError,
    MetroSPApiClientError,
)

if TYPE_CHECKING:
    from .data import JsonObject


class MetroSPFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow do Metrô SP."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: JsonObject | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Trata o passo inicial. A API é pública — sem credenciais."""
        errors: dict[str, str] = {}

        if user_input is not None:
            errors = await self._validate()
            if not errors:
                await self.async_set_unique_id(DOMAIN)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="Metrô SP", data={})

        return self.async_show_form(step_id="user", errors=errors)

    async def _validate(self) -> dict[str, str]:
        """Testa a conectividade e devolve um dict de erros (vazio no sucesso)."""
        try:
            await self._test_connectivity()
        except MetroSPApiClientCommunicationError as exception:
            LOGGER.error("Failed to connect to the Metrô SP API: %s", exception)
            return {"base": "connection"}
        except MetroSPApiClientError:
            LOGGER.exception("Failed to validate the Metrô SP API")
            return {"base": "unknown"}
        return {}

    async def _test_connectivity(self) -> None:
        """Consulta a API uma vez para confirmar que ela responde."""
        client = MetroSPApiClient(session=async_create_clientsession(self.hass))
        await client.async_get_lines()
