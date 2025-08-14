"""Data models for shuttle-run battle."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Vec2 = tuple[float, float]


@dataclass
class Stats:
    """Basic combat statistics for a unit."""

    max_hp: int
    atk: int
    defn: int
    spd: float
    atb_rate: float
    threshold: float


@dataclass
class Unit:
    """A battle participant in the shuttle-run system."""

    id: str
    name: str
    side: Literal["ally", "enemy"]
    lane: int
    stats: Stats
    hp: int
    atb: float = 0.0
    state: Literal["IDLE", "COMMAND", "CHARGE", "ACT", "COOLDOWN", "DEAD"] = "IDLE"
    pos: Vec2 = (0.0, 0.0)
    home_x: float = 0.0
    facing: int = 1
    action_queue: list[PlannedAction] = field(default_factory=list)
    target_id: str | None = None


@dataclass
class PlannedAction:
    """Plan describing a pending skill execution."""

    skill_id: str
    user_id: str
    target_id: str
