"""Config flow for Metrô SP."""

from __future__ import annotations

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import (
    MetroSPApiClient,
    MetroSPApiClientCommunicationError,
    MetroSPApiClientError,
)
from .const import DOMAIN, LOGGER


class MetroSPFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Metrô SP."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                client = MetroSPApiClient(session=async_create_clientsession(self.hass))
                await client.async_get_lines()
            except MetroSPApiClientCommunicationError as exception:
                LOGGER.error(exception)
                errors["base"] = "connection"
            except MetroSPApiClientError as exception:
                LOGGER.exception(exception)
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(DOMAIN)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="Metrô SP", data={})

        return self.async_show_form(step_id="user", errors=errors)
