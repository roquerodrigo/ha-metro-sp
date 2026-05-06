"""Config flow for Metrô SP."""

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
    """Config flow for Metrô SP."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: JsonObject | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step. The API is public — no credentials."""
        errors: dict[str, str] = {}

        if user_input is not None:
            errors = await self._validate()
            if not errors:
                await self.async_set_unique_id(DOMAIN)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="Metrô SP", data={})

        return self.async_show_form(step_id="user", errors=errors)

    async def _validate(self) -> dict[str, str]:
        """Test connectivity and return an errors dict (empty on success)."""
        try:
            await self._test_connectivity()
        except MetroSPApiClientCommunicationError as exception:
            LOGGER.error(exception)
            return {"base": "connection"}
        except MetroSPApiClientError as exception:
            LOGGER.exception(exception)
            return {"base": "unknown"}
        return {}

    async def _test_connectivity(self) -> None:
        """Hit the API once to confirm it answers."""
        client = MetroSPApiClient(session=async_create_clientsession(self.hass))
        await client.async_get_lines()
