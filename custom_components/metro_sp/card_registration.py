"""Registro do card Lovelace embutido no frontend."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, TypedDict, cast

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.components.lovelace import LOVELACE_DATA
from homeassistant.components.lovelace.resources import ResourceStorageCollection

from .const import DOMAIN, STATIC_URL_PREFIX

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

_STATIC_PATH_REGISTERED_KEY = f"{DOMAIN}_static_path_registered"
_EXTRA_MODULE_REGISTERED_KEY = f"{DOMAIN}_extra_module_registered"
_CARD_URL = f"{STATIC_URL_PREFIX}/metro-card.js"
_WWW_DIR = Path(__file__).parent / "www"


class MetroSPDashboardResource(TypedDict):
    """Recurso de dashboard como armazenado pela coleção de recursos do Lovelace."""

    id: str
    url: str


class MetroSPCardRegistration:
    """
    Serve o card embutido e o mantém registrado nos dashboards.

    O card é registrado como recurso de dashboard do Lovelace, e não como
    módulo extra do frontend: módulos extras só são embutidos no index.html
    das páginas servidas depois que esta integração começa o setup, então um
    dashboard aberto enquanto o Home Assistant ainda iniciava exibia um erro
    de configuração até um reload manual. Recursos de dashboard persistem em
    storage e são buscados a cada carregamento do dashboard, o que fecha essa
    janela de inicialização. O add_extra_js_url() permanece apenas como
    fallback para recursos em modo YAML, que não podem ser gerenciados por
    código.
    """

    def __init__(self, hass: HomeAssistant, version: str) -> None:
        """Inicializa o registro para uma versão do card."""
        self._hass = hass
        self._versioned_url = f"{_CARD_URL}?v={version}"

    async def async_register(self) -> None:
        """Serve os arquivos do card e garante que os dashboards os carreguem."""
        await self._async_register_static_path()
        if (resources := self._storage_resources()) is None:
            self._register_extra_module()
        else:
            await self._async_ensure_resource(resources)

    async def async_remove(self) -> None:
        """Remove o recurso de dashboard do card."""
        if (resources := self._storage_resources()) is None:
            return
        if not resources.loaded:
            await resources.async_load()
        for item in _resource_items(resources):
            if item["url"].startswith(_CARD_URL):
                await resources.async_delete_item(item["id"])

    async def _async_register_static_path(self) -> None:
        if self._hass.data.get(_STATIC_PATH_REGISTERED_KEY):
            return
        await self._hass.http.async_register_static_paths(
            [StaticPathConfig(STATIC_URL_PREFIX, str(_WWW_DIR), cache_headers=True)]
        )
        self._hass.data[_STATIC_PATH_REGISTERED_KEY] = True

    def _register_extra_module(self) -> None:
        if self._hass.data.get(_EXTRA_MODULE_REGISTERED_KEY):
            return
        add_extra_js_url(self._hass, self._versioned_url)
        self._hass.data[_EXTRA_MODULE_REGISTERED_KEY] = True

    def _storage_resources(self) -> ResourceStorageCollection | None:
        if (lovelace := self._hass.data.get(LOVELACE_DATA)) is None:
            return None
        resources = lovelace.resources
        if not isinstance(resources, ResourceStorageCollection):
            return None
        return resources

    async def _async_ensure_resource(
        self, resources: ResourceStorageCollection
    ) -> None:
        if not resources.loaded:
            await resources.async_load()
        for item in _resource_items(resources):
            if not item["url"].startswith(_CARD_URL):
                continue
            if item["url"] != self._versioned_url:
                await resources.async_update_item(
                    item["id"], {"url": self._versioned_url}
                )
            return
        await resources.async_create_item(
            {"res_type": "module", "url": self._versioned_url}
        )


def _resource_items(
    resources: ResourceStorageCollection,
) -> list[MetroSPDashboardResource]:
    return [cast("MetroSPDashboardResource", item) for item in resources.async_items()]
