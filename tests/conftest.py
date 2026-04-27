"""Shared fixtures and HA module mocks."""

from __future__ import annotations

import copy
import sys
from dataclasses import dataclass
from datetime import timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest


# ---------------------------------------------------------------------------
# Fake HA classes used across the mock tree
# ---------------------------------------------------------------------------


class _UpdateFailed(Exception):
    pass


class _DataUpdateCoordinator:
    def __init__(self, hass=None, logger=None, name=None, update_interval=None):
        self.hass = hass
        self.logger = logger
        self.name = name
        self.update_interval = update_interval
        self.config_entry: Any = None
        self.data: dict = {}

    def __class_getitem__(cls, item):
        return cls

    async def async_config_entry_first_refresh(self):
        self.data = await self._async_update_data()

    async def _async_update_data(self):
        return {}


class _CoordinatorEntity:
    # Class-level defaults (subclasses override these as class attrs)
    _attr_attribution: str | None = None
    _attr_has_entity_name: bool = False

    def __init__(self, coordinator):
        self.coordinator = coordinator

    def __class_getitem__(cls, item):
        return cls


class _SensorEntity:
    pass


class _ConfigFlow:
    VERSION = 1
    hass: Any = None

    def __init_subclass__(cls, domain=None, **kwargs):
        super().__init_subclass__(**kwargs)

    async def async_set_unique_id(self, unique_id: str):
        self._unique_id = unique_id

    def _abort_if_unique_id_configured(self):
        pass

    def async_create_entry(self, title: str, data: dict):
        return {"type": "create_entry", "title": title, "data": data}

    def async_show_form(self, step_id: str, errors: dict | None = None):
        return {"type": "form", "step_id": step_id, "errors": errors or {}}


class _DeviceInfo(dict):
    def __init__(self, identifiers=None, name=None, manufacturer=None, **kwargs):
        super().__init__(
            identifiers=identifiers or set(),
            name=name,
            manufacturer=manufacturer,
            **kwargs,
        )


def _slugify(text: str) -> str:
    return text.lower().replace(" ", "_").replace("-", "_")


# ---------------------------------------------------------------------------
# Build and register the mock HA module tree
# ---------------------------------------------------------------------------

def _build_ha_mocks() -> None:
    config_entries_mod = MagicMock(name="homeassistant.config_entries")
    config_entries_mod.ConfigFlow = _ConfigFlow
    config_entries_mod.ConfigFlowResult = dict

    update_coordinator_mod = MagicMock(name="homeassistant.helpers.update_coordinator")
    update_coordinator_mod.DataUpdateCoordinator = _DataUpdateCoordinator
    update_coordinator_mod.CoordinatorEntity = _CoordinatorEntity
    update_coordinator_mod.UpdateFailed = _UpdateFailed

    device_registry_mod = MagicMock(name="homeassistant.helpers.device_registry")
    device_registry_mod.DeviceInfo = _DeviceInfo

    sensor_mod = MagicMock(name="homeassistant.components.sensor")
    sensor_mod.SensorEntity = _SensorEntity

    ha_const_mod = MagicMock(name="homeassistant.const")
    ha_const_mod.Platform = MagicMock()
    ha_const_mod.Platform.SENSOR = "sensor"

    util_mod = MagicMock(name="homeassistant.util")
    util_mod.slugify = _slugify

    helpers_mod = MagicMock(name="homeassistant.helpers")
    aiohttp_client_mod = MagicMock(name="homeassistant.helpers.aiohttp_client")
    aiohttp_client_mod.async_create_clientsession = MagicMock(return_value=MagicMock())
    aiohttp_client_mod.async_get_clientsession = MagicMock(return_value=MagicMock())

    loader_mod = MagicMock(name="homeassistant.loader")
    loader_mod.async_get_loaded_integration = AsyncMock(return_value=MagicMock())

    ha_mod = MagicMock(name="homeassistant")
    ha_mod.config_entries = config_entries_mod

    sys.modules.update(
        {
            "homeassistant": ha_mod,
            "homeassistant.config_entries": config_entries_mod,
            "homeassistant.const": ha_const_mod,
            "homeassistant.helpers": helpers_mod,
            "homeassistant.helpers.update_coordinator": update_coordinator_mod,
            "homeassistant.helpers.device_registry": device_registry_mod,
            "homeassistant.helpers.aiohttp_client": aiohttp_client_mod,
            "homeassistant.components": MagicMock(name="homeassistant.components"),
            "homeassistant.components.sensor": sensor_mod,
            "homeassistant.util": util_mod,
            "homeassistant.loader": loader_mod,
        }
    )


_build_ha_mocks()


# ---------------------------------------------------------------------------
# Sample data fixture
# ---------------------------------------------------------------------------

SAMPLE_LINES = [
    {
        "Code": 1,
        "ColorName": "Azul",
        "ColorHex": "#0455A1",
        "Line": "1",
        "StatusCode": 1,
        "StatusLabel": "Operação Normal",
        "StatusColor": "#00FF00",
        "Description": "Linha operando normalmente.",
    },
    {
        "Code": 3,
        "ColorName": "Vermelha",
        "ColorHex": "#EE372F",
        "Line": "3",
        "StatusCode": 2,
        "StatusLabel": "Velocidade Reduzida",
        "StatusColor": "#FFFF00",
        "Description": "",
    },
]

SAMPLE_DATA: dict[int, dict] = {line["Code"]: line for line in SAMPLE_LINES}


@pytest.fixture
def sample_lines():
    return copy.deepcopy(SAMPLE_LINES)


@pytest.fixture
def sample_data():
    return copy.deepcopy(SAMPLE_DATA)


@pytest.fixture
def mock_coordinator(sample_data):
    coord = MagicMock()
    coord.data = sample_data
    coord.config_entry = MagicMock()
    coord.config_entry.entry_id = "test_entry_id"
    return coord
