"""Metrô SP integration for Home Assistant."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.const import Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.loader import async_get_loaded_integration

from .api import MetroSPApiClient
from .const import DOMAIN, STATIC_URL_PREFIX
from .coordinator import MetroSPDataUpdateCoordinator
from .data import MetroSPData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import MetroSPConfigEntry

PLATFORMS: list[Platform] = [Platform.SENSOR]
_STATIC_REGISTERED_KEY = f"{DOMAIN}_static_registered"
_WWW_DIR = Path(__file__).parent / "www"
_CARD_URL = f"{STATIC_URL_PREFIX}/metro-card.js"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MetroSPConfigEntry,
) -> bool:
    """Set up Metrô SP from a config entry."""
    integration = async_get_loaded_integration(hass, entry.domain)

    if not hass.data.get(_STATIC_REGISTERED_KEY):
        await hass.http.async_register_static_paths(
            [StaticPathConfig(STATIC_URL_PREFIX, str(_WWW_DIR), cache_headers=True)]
        )
        # Ship the Lovelace card with the integration: serve it from the same
        # static dir and auto-register it as a frontend module so users don't
        # have to add a dashboard resource by hand. The version query busts the
        # browser cache on every release.
        add_extra_js_url(hass, f"{_CARD_URL}?v={integration.version}")
        hass.data[_STATIC_REGISTERED_KEY] = True

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


async def async_reload_entry(
    hass: HomeAssistant,
    entry: MetroSPConfigEntry,
) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)
