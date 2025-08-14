"""Asset loading helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import arcade

from .config import DATA_DIR

ASSET_DIR = Path(__file__).resolve().parent.parent / "assets"
FONTS_DIR = ASSET_DIR / "fonts"
IMAGES_DIR = ASSET_DIR / "images"
SOUNDS_DIR = ASSET_DIR / "sounds"

_loaded_textures: Dict[str, arcade.Texture] = {}


def load_texture(name: str) -> arcade.Texture:
    path = IMAGES_DIR / name
    if name not in _loaded_textures:
        _loaded_textures[name] = arcade.load_texture(str(path))
    return _loaded_textures[name]
