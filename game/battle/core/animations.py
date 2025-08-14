"""Simple placeholders for battle effects and damage pops."""

from __future__ import annotations

import time
from dataclasses import dataclass

import arcade


@dataclass
class DamagePop:
    value: str
    pos: tuple[float, float]
    start: float


_effects: list[tuple[str, float, tuple[float, float]]] = []
_damage: list[DamagePop] = []


def update(dt: float) -> None:
    now = time.time()
    _effects[:] = [e for e in _effects if now - e[1] < 0.5]
    _damage[:] = [d for d in _damage if now - d.start < 1.0]


def draw() -> None:  # pragma: no cover - visuals
    for name, _start, pos in _effects:
        if name == "flash":
            arcade.draw_circle_filled(pos[0], pos[1], 30, arcade.color.WHITE)
    for dmg in _damage:
        alpha = int(255 * (1 - (time.time() - dmg.start)))
        arcade.draw_text(dmg.value, dmg.pos[0], dmg.pos[1] + 20, (255, 0, 0, alpha), 16)


def play_effect(name: str, user, target) -> None:
    _effects.append((name, time.time(), target.pos))


def pop_damage(value: int, pos: tuple[float, float]) -> None:
    _damage.append(DamagePop(str(value), pos, time.time()))


def shake(duration: float, magnitude: float) -> None:
    # Placeholder: no camera implementation
    pass
