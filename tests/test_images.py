from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from custom_components.metro_sp import images
from custom_components.metro_sp.images import (
    STATIC_URL_PATH,
    async_register_line_images,
    line_image_url,
)

LINE_NUMBERS = (1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 15, 17)


def test_line_image_url_format():
    assert line_image_url(1, "Azul") == f"{STATIC_URL_PATH}/linha_1_azul.png"


def test_line_image_url_slugifies_color():
    assert line_image_url(5, "Lilás") == f"{STATIC_URL_PATH}/linha_5_lilas.png"


@pytest.mark.parametrize("line_code", LINE_NUMBERS)
def test_bundled_png_exists_for_each_line(line_code):
    package_dir = Path(images.__file__).parent
    matches = list(package_dir.glob(f"lines/linha_{line_code}_*.png"))
    assert matches, f"missing PNG for line {line_code}"
    assert matches[0].read_bytes().startswith(b"\x89PNG"), "not a PNG file"


async def test_register_line_images_registers_static_path(hass):
    hass.http = AsyncMock()
    hass.data.pop("metro_sp_static_paths_registered", None)
    await async_register_line_images(hass)
    hass.http.async_register_static_paths.assert_awaited_once()
    configs = hass.http.async_register_static_paths.call_args.args[0]
    assert configs[0].url_path == STATIC_URL_PATH
    assert configs[0].path.endswith("/lines")


async def test_register_line_images_is_idempotent(hass):
    hass.http = AsyncMock()
    hass.data.pop("metro_sp_static_paths_registered", None)
    await async_register_line_images(hass)
    await async_register_line_images(hass)
    hass.http.async_register_static_paths.assert_awaited_once()
