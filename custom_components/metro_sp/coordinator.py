"""DataUpdateCoordinator for metro_sp."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import DOMAIN, LOGGER
from .exceptions import MetroSPApiClientError

if TYPE_CHECKING:
    from datetime import datetime

    from homeassistant.core import HomeAssistant

    from .data import MetroSPConfigEntry, MetroSPLine

UPDATE_INTERVAL = timedelta(minutes=1)
FAILURE_GRACE_PERIOD = timedelta(minutes=5)


def _normalize_line(line: MetroSPLine) -> MetroSPLine:
    """
    Normalize upstream fields so consumers see consistent values.

    CPTM lines come back with ``ColorName`` in all caps (e.g. ``DIAMANTE``)
    while Metrô lines are title-cased (``Azul``). Title-case it once here so
    the whole integration — attributes, device names, cards — is consistent.
    """
    return {**line, "ColorName": line["ColorName"].title()}


class MetroSPDataUpdateCoordinator(DataUpdateCoordinator["dict[int, MetroSPLine]"]):
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
        self._first_failure_at: datetime | None = None

    async def _async_update_data(self) -> dict[int, MetroSPLine]:
        """Fetch data from API; tolerate failures shorter than the grace period."""
        try:
            lines = await self.config_entry.runtime_data.client.async_get_lines()
        except MetroSPApiClientError as exception:
            return self._handle_failure(exception)

        self._first_failure_at = None
        return {line["Code"]: _normalize_line(line) for line in lines}

    def _handle_failure(
        self, exception: MetroSPApiClientError
    ) -> dict[int, MetroSPLine]:
        """Suppress transient errors; raise UpdateFailed past the grace period."""
        now = dt_util.utcnow()
        if self._first_failure_at is None:
            self._first_failure_at = now
        if (
            self.data is not None
            and now - self._first_failure_at < FAILURE_GRACE_PERIOD
        ):
            LOGGER.warning("Metrô SP API error; keeping last known data: %s", exception)
            return self.data
        raise UpdateFailed(exception) from exception
