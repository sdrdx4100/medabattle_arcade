"""Save file utilities."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from pydantic import BaseModel

from .config import DATA_DIR

SAVES_DIR = DATA_DIR / "saves"
SAVES_DIR.mkdir(exist_ok=True)


class SaveData(BaseModel):
    player_name: str = "Player"
    progress: int = 0


def slot_path(slot: int) -> Path:
    return SAVES_DIR / f"slot{slot}.json"


def load_slot(slot: int) -> Optional[SaveData]:
    path = slot_path(slot)
    if path.exists():
        return SaveData.model_validate_json(path.read_text())
    return None


def write_slot(slot: int, data: SaveData) -> None:
    path = slot_path(slot)
    path.write_text(data.model_dump_json(indent=2), encoding="utf-8")


def init_slot(slot: int) -> SaveData:
    data = SaveData()
    write_slot(slot, data)
    return data
