"""Metrô SP integration for Home Assistant."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from homeassistant.const import Platform
from homeassistant.helpers import entity_registry as er
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

_LEGACY_UNIQUE_ID_PATTERN = re.compile(r"^sensor\.metro_sp_linha_(\d+)_.+_operacao$")


async def _async_migrate_legacy_unique_ids(
    hass: HomeAssistant,
    entry: MetroSPConfigEntry,
) -> None:
    """
    Rewrite legacy unique ids to the entry-scoped format.

    The legacy format embedded the entity_id and the line's color slug; a
    color rename upstream changed the unique id and orphaned the entity.
    """

    def _migrate(registry_entry: er.RegistryEntry) -> dict[str, str] | None:
        match = _LEGACY_UNIQUE_ID_PATTERN.match(registry_entry.unique_id)
        if match is None:
            return None
        return {"new_unique_id": f"{entry.entry_id}_{match.group(1)}_operation"}

    await er.async_migrate_entries(hass, entry.entry_id, _migrate)


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

    await _async_migrate_legacy_unique_ids(hass, entry)
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
