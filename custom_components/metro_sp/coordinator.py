"""DataUpdateCoordinator for metro_sp."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import MetroSPApiClientError
from .const import DOMAIN, LOGGER

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import MetroSPConfigEntry

UPDATE_INTERVAL = timedelta(minutes=5)


class MetroSPDataUpdateCoordinator(DataUpdateCoordinator[dict[int, dict[str, Any]]]):
    """Coordinator for fetching Metrô SP line data."""

    config_entry: MetroSPConfigEntry

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize."""
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )

    async def _async_update_data(self) -> dict[int, dict[str, Any]]:
        """Fetch data from API and index by line code."""
        try:
            lines = await self.config_entry.runtime_data.client.async_get_lines()
            return {line["Code"]: line for line in lines}
        except MetroSPApiClientError as exception:
            raise UpdateFailed(exception) from exception
