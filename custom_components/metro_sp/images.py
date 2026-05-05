"""Generate and store line images under HA's /local/ static path."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import TYPE_CHECKING, Any

import aiohttp
import async_timeout
from homeassistant.util import slugify

from .const import LOGGER

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

WWW_SUBDIR = "metro_sp"
_AVATAR_URL = (
    "https://ui-avatars.com/api/"
    "?color=fff&bold=true&format=png&font-size=0.6"
    "&name={code}&background={color}"
)
_DEFAULT_COLOR = "888888"


def line_image_filename(code: int, color_name: str) -> str:
    """Return the filename for a line image (kept stable per color)."""
    return f"linha_{code}_{slugify(color_name)}.png"


def line_image_local_url(code: int, color_name: str) -> str:
    """Return the public /local/ URL Home Assistant serves the image at."""
    return f"/local/{WWW_SUBDIR}/{line_image_filename(code, color_name)}"


async def async_generate_line_images(
    hass: HomeAssistant,
    session: aiohttp.ClientSession,
    lines: dict[int, dict[str, Any]],
) -> None:
    """Download one PNG per line into <config>/www/metro_sp/."""
    target_dir = Path(hass.config.path("www", WWW_SUBDIR))
    await hass.async_add_executor_job(_ensure_dir, target_dir)

    await asyncio.gather(
        *(
            _download_line_image(hass, session, target_dir, line)
            for line in lines.values()
        ),
        return_exceptions=True,
    )


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


async def _download_line_image(
    hass: HomeAssistant,
    session: aiohttp.ClientSession,
    target_dir: Path,
    line: dict[str, Any],
) -> None:
    code = line["Code"]
    color_name = line["ColorName"]
    color_hex = (line.get("ColorHex") or f"#{_DEFAULT_COLOR}").lstrip("#")
    target_path = target_dir / line_image_filename(code, color_name)

    if await hass.async_add_executor_job(target_path.exists):
        return

    url = _AVATAR_URL.format(code=code, color=color_hex)
    try:
        async with async_timeout.timeout(10):
            response = await session.get(url)
            response.raise_for_status()
            content = await response.read()
    except (TimeoutError, aiohttp.ClientError) as exc:
        LOGGER.warning("Failed to download image for line %s: %s", code, exc)
        return

    await hass.async_add_executor_job(target_path.write_bytes, content)
