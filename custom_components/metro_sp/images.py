"""Static-path serving for line images bundled with the integration."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from homeassistant.components.http import StaticPathConfig
from homeassistant.util import slugify

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

STATIC_URL_PATH = "/api/metro_sp/lines"
_IMAGES_DIR = Path(__file__).parent / "lines"
_REGISTERED_KEY = "metro_sp_static_paths_registered"


def line_image_url(code: int, color_name: str) -> str:
    """Return the URL Home Assistant serves the per-line PNG at."""
    return f"{STATIC_URL_PATH}/linha_{code}_{slugify(color_name)}.png"


async def async_register_line_images(hass: HomeAssistant) -> None:
    """Expose the bundled line images under STATIC_URL_PATH (idempotent)."""
    if hass.data.get(_REGISTERED_KEY):
        return
    await hass.http.async_register_static_paths(
        [StaticPathConfig(STATIC_URL_PATH, str(_IMAGES_DIR), cache_headers=True)]
    )
    hass.data[_REGISTERED_KEY] = True
