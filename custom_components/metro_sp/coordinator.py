"""DataUpdateCoordinator do metro_sp."""

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
    Normaliza os campos da origem para que os consumidores vejam valores consistentes.

    As linhas da CPTM chegam com ``ColorName`` em maiúsculas (ex.: ``DIAMANTE``),
    enquanto as do Metrô vêm só com a inicial maiúscula (``Azul``). A conversão
    é feita uma única vez aqui, para que toda a integração — atributos, nomes
    de device, cards — fique consistente.
    """
    return {**line, "ColorName": line["ColorName"].title()}


class MetroSPDataUpdateCoordinator(DataUpdateCoordinator["dict[int, MetroSPLine]"]):
    """Coordinator que busca os dados das linhas do Metrô SP."""

    config_entry: MetroSPConfigEntry

    def __init__(self, hass: HomeAssistant) -> None:
        """Inicializa o coordinator."""
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )
        self._first_failure_at: datetime | None = None

    async def _async_update_data(self) -> dict[int, MetroSPLine]:
        """Busca os dados na API; tolera falhas dentro do período de tolerância."""
        try:
            lines = await self.config_entry.runtime_data.client.async_get_lines()
        except MetroSPApiClientError as exception:
            return self._handle_failure(exception)

        self._first_failure_at = None
        return {line["Code"]: _normalize_line(line) for line in lines}

    def _handle_failure(
        self, exception: MetroSPApiClientError
    ) -> dict[int, MetroSPLine]:
        """Suprime erros transitórios; levanta UpdateFailed após a tolerância."""
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
