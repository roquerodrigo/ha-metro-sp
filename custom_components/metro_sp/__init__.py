"""Metrô SP integration for Home Assistant."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.loader import async_get_loaded_integration

from .api import MetroSPApiClient
from .card_registration import MetroSPCardRegistration
from .const import DOMAIN
from .coordinator import MetroSPDataUpdateCoordinator
from .data import MetroSPData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import MetroSPConfigEntry

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MetroSPConfigEntry,
) -> bool:
    """Set up Metrô SP from a config entry."""
    integration = async_get_loaded_integration(hass, entry.domain)

    await MetroSPCardRegistration(hass, str(integration.version)).async_register()

    coordinator = MetroSPDataUpdateCoordinator(hass=hass)
    entry.runtime_data = MetroSPData(
        client=MetroSPApiClient(session=async_get_clientsession(hass)),
        integration=integration,
        coordinator=coordinator,
    )

    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: MetroSPConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_remove_entry(
    hass: HomeAssistant,
    entry: MetroSPConfigEntry,
) -> None:
    """Clean up the card registration when the last entry is removed."""
    if hass.config_entries.async_entries(DOMAIN):
        return
    integration = async_get_loaded_integration(hass, entry.domain)
    await MetroSPCardRegistration(hass, str(integration.version)).async_remove()


async def async_reload_entry(
    hass: HomeAssistant,
    entry: MetroSPConfigEntry,
) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)
