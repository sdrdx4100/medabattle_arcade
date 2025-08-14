"""Configuration loading utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CONFIG_PATH = DATA_DIR / "config.json"


class Config(BaseModel):
    window_width: int = 800
    window_height: int = 600
    window_title: str = "Medabattle Arcade"
    font_name: str = "Arial"


def load_config() -> Config:
    if CONFIG_PATH.exists():
        return Config.model_validate_json(CONFIG_PATH.read_text(encoding="utf-8"))
    return Config()


__all__ = ["Config", "load_config", "DATA_DIR"]
