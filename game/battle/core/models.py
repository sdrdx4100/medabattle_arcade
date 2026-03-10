"""Data models for shuttle-run battle."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Vec2 = tuple[float, float]
PartSlot = Literal["head", "right_arm", "left_arm", "legs"]


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
class Part:
    """An individual robot part that can be damaged and broken."""

    slot: PartSlot
    name: str
    skill_id: str
    max_hp: int
    hp: int
    armor: int = 0

    @property
    def is_operational(self) -> bool:
        return self.hp > 0


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
    parts: dict[PartSlot, Part] = field(default_factory=dict)
    action_queue: list[PlannedAction] = field(default_factory=list)
    target_id: str | None = None

    def sync_hp(self) -> None:
        """Synchronize aggregate HP from all parts."""
        if self.parts:
            self.hp = sum(max(part.hp, 0) for part in self.parts.values())

    def available_parts(self) -> list[Part]:
        """Return parts that can still execute commands."""
        return [part for part in self.parts.values() if part.is_operational]

    def get_part(self, slot: PartSlot) -> Part | None:
        """Look up a part by slot."""
        return self.parts.get(slot)


@dataclass
class PlannedAction:
    """Plan describing a pending skill execution."""

    skill_id: str
    user_id: str
    target_id: str
    source_slot: PartSlot | None = None
