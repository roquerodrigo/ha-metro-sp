from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock

import aiohttp

from custom_components.metro_sp.images import (
    async_generate_line_images,
    line_image_filename,
    line_image_local_url,
)

if TYPE_CHECKING:
    from pathlib import Path


def _line(code=1, color_name="Azul", color_hex="#0455A1"):
    return {"Code": code, "ColorName": color_name, "ColorHex": color_hex}


def _make_session(content=b"PNG", side_effect=None):
    response = AsyncMock()
    response.raise_for_status = MagicMock()
    response.read = AsyncMock(return_value=content)
    session = MagicMock()
    if side_effect is not None:
        session.get = AsyncMock(side_effect=side_effect)
    else:
        session.get = AsyncMock(return_value=response)
    return session, response


def test_line_image_filename_uses_slug():
    assert line_image_filename(5, "Lilás") == "linha_5_lilas.png"


def test_line_image_local_url_format():
    assert line_image_local_url(1, "Azul") == "/local/metro_sp/linha_1_azul.png"


async def test_generate_creates_target_dir(hass, tmp_path):
    hass.config.config_dir = str(tmp_path)
    session, _ = _make_session()
    await async_generate_line_images(hass, session, {1: _line()})
    assert (tmp_path / "www" / "metro_sp").is_dir()


async def test_generate_writes_png_per_line(hass, tmp_path):
    hass.config.config_dir = str(tmp_path)
    session, _ = _make_session(content=b"PNGDATA")
    lines = {1: _line(1, "Azul"), 3: _line(3, "Vermelha")}
    await async_generate_line_images(hass, session, lines)
    written = sorted((tmp_path / "www" / "metro_sp").iterdir())
    assert [p.name for p in written] == ["linha_1_azul.png", "linha_3_vermelha.png"]
    assert written[0].read_bytes() == b"PNGDATA"


def _seed_existing_image(tmp_path: Path) -> Path:
    target_dir = tmp_path / "www" / "metro_sp"
    target_dir.mkdir(parents=True)
    (target_dir / "linha_1_azul.png").write_bytes(b"OLD")
    return target_dir


async def test_generate_skips_existing_file(hass, tmp_path):
    target_dir = _seed_existing_image(tmp_path)
    hass.config.config_dir = str(tmp_path)
    session, _ = _make_session(content=b"NEW")
    await async_generate_line_images(hass, session, {1: _line()})
    assert (target_dir / "linha_1_azul.png").read_bytes() == b"OLD"
    session.get.assert_not_awaited()


async def test_generate_uses_png_format(hass, tmp_path):
    hass.config.config_dir = str(tmp_path)
    session, _ = _make_session()
    await async_generate_line_images(hass, session, {1: _line(color_hex="#0455A1")})
    url = session.get.call_args.args[0]
    assert "format=png" in url
    assert "background=0455A1" in url
    assert "name=1" in url


async def test_generate_falls_back_to_default_color(hass, tmp_path):
    hass.config.config_dir = str(tmp_path)
    session, _ = _make_session()
    line = _line()
    line.pop("ColorHex")
    await async_generate_line_images(hass, session, {1: line})
    assert "background=888888" in session.get.call_args.args[0]


async def test_generate_swallows_http_errors(hass, tmp_path):
    hass.config.config_dir = str(tmp_path)
    session, _ = _make_session(side_effect=aiohttp.ClientError("nope"))
    await async_generate_line_images(hass, session, {1: _line()})
    target = tmp_path / "www" / "metro_sp" / "linha_1_azul.png"
    assert not target.exists()
