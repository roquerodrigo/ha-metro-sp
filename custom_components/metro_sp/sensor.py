"""Sensor platform for metro_sp."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.util import slugify

from .const import DOMAIN, STATIC_URL_PREFIX
from .entity import MetroSPEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import MetroSPDataUpdateCoordinator
    from .data import (
        MetroSPConfigEntry,
        MetroSPLine,
        MetroSPSensorAttributes,
    )

_DEFAULT_OPERATOR = "Metrô SP / CPTM"

_LINE_OPERATORS: dict[int, str] = {
    1: "Metrô SP",
    2: "Metrô SP",
    3: "Metrô SP",
    4: "ViaQuatro",
    5: "ViaMobilidade",
    6: "Linha Uni",
    7: "TIC Trens",
    8: "ViaMobilidade",
    9: "ViaMobilidade",
    10: "CPTM",
    11: "Trivia Trens",
    12: "Trivia Trens",
    13: "Trivia Trens",
    15: "Metrô SP",
    17: "ViaMobilidade",
}


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: MetroSPConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up one sensor per line, adding sensors for lines that appear later."""
    coordinator = entry.runtime_data.coordinator
    known_line_codes: set[int] = set()

    def _async_add_new_line_sensors() -> None:
        new_line_codes = set(coordinator.data) - known_line_codes
        if not new_line_codes:
            return
        known_line_codes.update(new_line_codes)
        async_add_entities(
            MetroSPLineSensor(coordinator=coordinator, line_code=code)
            for code in new_line_codes
        )

    _async_add_new_line_sensors()
    entry.async_on_unload(coordinator.async_add_listener(_async_add_new_line_sensors))


class MetroSPLineSensor(MetroSPEntity, SensorEntity):
    """Sensor for a single Metrô SP / CPTM line."""

    _attr_translation_key = "operation"
    _attr_icon = "mdi:subway"

    def __init__(
        self,
        coordinator: MetroSPDataUpdateCoordinator,
        line_code: int,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._line_code = line_code
        color_slug = slugify(coordinator.data[line_code]["ColorName"])
        self._base_id = f"metro_sp_linha_{line_code}_{color_slug}"
        # entity_id must be set in __init__ — HA reads it as suggested_object_id
        # before the entity is registered.
        self.entity_id = f"sensor.{self._base_id}_operacao"

    @property
    def _line_data(self) -> MetroSPLine:
        """Return the latest payload for this sensor's line."""
        return self.coordinator.data[self._line_code]

    @property
    def available(self) -> bool:
        """Report unavailable while the upstream API stops listing this line."""
        return super().available and self._line_code in self.coordinator.data

    @property
    def unique_id(self) -> str:
        """Return the unique id derived from the entry and the line code."""
        entry_id = self.coordinator.config_entry.entry_id
        return f"{entry_id}_{self._line_code}_operation"

    @property
    def device_info(self) -> DeviceInfo:
        """Return per-line device info; manufacturer is operator-mapped."""
        line = self._line_data
        # ColorName is already normalized (title-cased) by the coordinator.
        line_name = f"Line {line['Code']} - {line['ColorName']}"
        entry_id = self.coordinator.config_entry.entry_id
        return DeviceInfo(
            identifiers={(DOMAIN, f"{entry_id}_{self._line_code}")},
            name=line_name,
            manufacturer=_LINE_OPERATORS.get(self._line_code, _DEFAULT_OPERATOR),
        )

    @property
    def entity_picture(self) -> str:
        """Return the local static image for this line."""
        return f"{STATIC_URL_PREFIX}/linha_{self._line_code}.png"

    @property
    def native_value(self) -> str:
        """Return the line's status label."""
        return self._line_data["StatusLabel"]

    @property
    def extra_state_attributes(self) -> MetroSPSensorAttributes:
        """
        Return extra state attributes.

        ``description`` carries the upstream incident text (or the status
        label as a fallback) — kept off the state so the 255-char HA limit
        cannot drop the value to ``unknown``.
        """
        data = self._line_data
        return {
            "status_code": data["StatusCode"],
            "status_color": data["StatusColor"],
            "color_name": data["ColorName"],
            "color_hex": data["ColorHex"],
            "line_code": data["Code"],
            "description": data.get("Description") or data["StatusLabel"],
        }
