from __future__ import annotations

from homeassistant.components.lovelace import LOVELACE_DATA
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.metro_sp.const import DOMAIN

CARD_URL = "/metro_sp/metro-card.js"


def card_resource_urls(hass) -> list[str]:
    resources = hass.data[LOVELACE_DATA].resources
    return [
        item["url"]
        for item in resources.async_items()
        if item["url"].startswith(CARD_URL)
    ]


async def storage_resources(hass):
    resources = hass.data[LOVELACE_DATA].resources
    if not resources.loaded:
        await resources.async_load()
    return resources


async def test_setup_creates_dashboard_resource(hass, setup_integration):
    version = setup_integration.runtime_data.integration.version
    assert card_resource_urls(hass) == [f"{CARD_URL}?v={version}"]


async def test_setup_updates_stale_resource_version(
    hass, mock_api_client, enable_custom_integrations
):
    assert await async_setup_component(hass, "lovelace", {})
    resources = await storage_resources(hass)
    await resources.async_create_item(
        {"res_type": "module", "url": f"{CARD_URL}?v=0.0.1"}
    )

    entry = MockConfigEntry(domain=DOMAIN, data={})
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    version = entry.runtime_data.integration.version
    assert card_resource_urls(hass) == [f"{CARD_URL}?v={version}"]


async def test_setup_keeps_unrelated_resources(
    hass, mock_api_client, enable_custom_integrations
):
    assert await async_setup_component(hass, "lovelace", {})
    resources = await storage_resources(hass)
    await resources.async_create_item(
        {"res_type": "module", "url": "/hacsfiles/other-card/other-card.js"}
    )

    entry = MockConfigEntry(domain=DOMAIN, data={})
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    urls = [item["url"] for item in resources.async_items()]
    assert "/hacsfiles/other-card/other-card.js" in urls


async def test_reload_does_not_duplicate_resource(hass, setup_integration):
    await hass.config_entries.async_reload(setup_integration.entry_id)
    await hass.async_block_till_done()

    assert len(card_resource_urls(hass)) == 1


async def test_yaml_mode_falls_back_to_extra_module(
    hass, mock_api_client, enable_custom_integrations
):
    from homeassistant.components.frontend import DATA_EXTRA_MODULE_URL, UrlManager

    hass.data.setdefault(DATA_EXTRA_MODULE_URL, UrlManager(lambda *_: None, []))
    assert await async_setup_component(hass, "lovelace", {"lovelace": {"mode": "yaml"}})

    entry = MockConfigEntry(domain=DOMAIN, data={})
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    urls = hass.data[DATA_EXTRA_MODULE_URL].urls
    assert any(u.startswith(f"{CARD_URL}?v=") for u in urls)


async def test_yaml_mode_reload_adds_single_extra_module(
    hass, mock_api_client, enable_custom_integrations
):
    from homeassistant.components.frontend import DATA_EXTRA_MODULE_URL, UrlManager

    hass.data.setdefault(DATA_EXTRA_MODULE_URL, UrlManager(lambda *_: None, []))
    assert await async_setup_component(hass, "lovelace", {"lovelace": {"mode": "yaml"}})

    entry = MockConfigEntry(domain=DOMAIN, data={})
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()

    urls = [u for u in hass.data[DATA_EXTRA_MODULE_URL].urls if u.startswith(CARD_URL)]
    assert len(urls) == 1


async def test_remove_last_entry_deletes_resource(hass, setup_integration):
    assert card_resource_urls(hass)

    await hass.config_entries.async_remove(setup_integration.entry_id)
    await hass.async_block_till_done()

    assert card_resource_urls(hass) == []


async def test_remove_without_lovelace_data_is_noop(hass):
    from custom_components.metro_sp.card_registration import MetroSPCardRegistration

    await MetroSPCardRegistration(hass, "1.0.0").async_remove()


async def test_remove_loads_resources_before_deleting(hass):
    from custom_components.metro_sp.card_registration import MetroSPCardRegistration

    assert await async_setup_component(hass, "lovelace", {})
    registration = MetroSPCardRegistration(hass, "1.0.0")
    await registration.async_remove()

    assert card_resource_urls(hass) == []


async def test_remove_keeps_resource_while_entries_remain(hass, setup_integration):
    other_entry = MockConfigEntry(domain=DOMAIN, data={})
    other_entry.add_to_hass(hass)

    await hass.config_entries.async_remove(setup_integration.entry_id)
    await hass.async_block_till_done()

    assert card_resource_urls(hass)
