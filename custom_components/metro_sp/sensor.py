"""Sensor platform for metro_sp."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.util import slugify

from .const import DOMAIN
from .entity import MetroSPEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import MetroSPDataUpdateCoordinator
    from .data import MetroSPConfigEntry

_SENSOR_KEYS = ("operacao", "detalhes")

_LINE_OPERATORS: dict[int, str] = {
    1: "Metrô SP",
    2: "Metrô SP",
    3: "Metrô SP",
    4: "ViaQuatro",
    5: "ViaMobilidade",
    7: "CPTM",
    8: "ViaMobilidade",
    9: "ViaMobilidade",
    10: "CPTM",
    11: "CPTM",
    12: "CPTM",
    13: "CPTM",
    15: "Metrô SP",
    17: "ViaMobilidade",
}


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: MetroSPConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors for all lines returned by the API."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        MetroSPLineSensor(coordinator=coordinator, line_code=code, sensor_key=key)
        for code in coordinator.data
        for key in _SENSOR_KEYS
    )


class MetroSPLineSensor(MetroSPEntity, SensorEntity):
    """Sensor for a single Metrô SP / CPTM line."""

    def __init__(
        self,
        coordinator: MetroSPDataUpdateCoordinator,
        line_code: int,
        sensor_key: str,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._line_code = line_code
        self._sensor_key = sensor_key
        line = coordinator.data[line_code]
        line_name = f"Linha {line['Code']} - {line['ColorName'].title()}"
        color_slug = slugify(line["ColorName"])
        base_id = f"metro_sp_linha_{line_code}_{color_slug}"

        self._attr_unique_id = f"sensor.{base_id}_{sensor_key}"
        self._attr_translation_key = sensor_key
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{coordinator.config_entry.entry_id}_{line_code}")},
            name=line_name,
            manufacturer=_LINE_OPERATORS.get(line_code, "Metrô SP / CPTM"),
        )
        self.entity_id = f"sensor.{base_id}_{sensor_key}"

    @property
    def _line_data(self) -> dict[str, Any]:
        return self.coordinator.data[self._line_code]

    @property
    def entity_picture(self) -> str:
        """Return an avatar URL with the line number and color."""
        color_hex = self._line_data.get("ColorHex", "#888888").lstrip("#")
        code = self._line_data.get("Code", "")
        return f"https://ui-avatars.com/api/?color=fff&name={code}&bold=true&format=svg&font-size=0.6&background={color_hex}"

    @property
    def native_value(self) -> str:
        """Return the current value for this sensor."""
        if self._sensor_key == "operacao":
            return self._line_data["StatusLabel"]
        return self._line_data.get("Description") or ""

    @property
    def icon(self) -> str:
        """Return the entity icon."""
        return "mdi:subway"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        data = self._line_data
        return {
            "status_code": data.get("StatusCode"),
            "status_color": data.get("StatusColor"),
            "color_name": data.get("ColorName"),
            "color_hex": data.get("ColorHex"),
            "line_code": data.get("Code"),
        }
