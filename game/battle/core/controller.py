"""Battle controller managing shuttle-run combat."""

from __future__ import annotations

import json
import logging
from collections import deque
from collections.abc import Callable
from pathlib import Path
from random import random

import arcade

from ..ui.widgets import draw_atb_bar
from .animations import (
    draw as anim_draw,
)
from .animations import (
    play_effect,
    pop_damage,
)
from .animations import (
    update as anim_update,
)
from .models import PlannedAction, Unit

PX_PER_SEC = 180
CENTER_X = 400
ALLY_X = 120
ENEMY_X = 680
LANE_Y = [360, 300, 240]

SKILL_PATH = Path(__file__).resolve().parent.parent / "data" / "skills.json"
with SKILL_PATH.open(encoding="utf-8") as f:
    SKILLS = {s["id"]: s for s in json.load(f)}

logger = logging.getLogger(__name__)


class BattleController:
    """Update and render logic for the shuttle-run battle."""

    def __init__(self) -> None:
        self.units: dict[str, Unit] = {}
        self.ready_queue: deque[Unit] = deque()
        self.on_command: Callable[[Unit], None] | None = None
        self.last_message: str | None = None

    def add_unit(self, unit: Unit) -> None:
        self.units[unit.id] = unit

    # update & draw
    def update(self, dt: float) -> None:
        for unit in self.units.values():
            if unit.state == "DEAD":
                continue
            if unit.state in {"CHARGE", "COOLDOWN"}:
                self._update_movement(unit, dt)
            elif unit.state == "ACT":
                if unit.action_queue:
                    pa = unit.action_queue.pop(0)
                    target = self.units.get(pa.target_id)
                    if not target or target.state == "DEAD":
                        new_target = self._find_target(unit)
                        if new_target:
                            pa.target_id = new_target.id
                        else:
                            unit.state = "COOLDOWN"
                            continue
                    self.apply_action(pa)
                unit.state = "COOLDOWN"
            elif unit.state == "IDLE":
                if unit.atb < unit.stats.threshold:
                    unit.atb = min(
                        unit.stats.threshold, unit.atb + unit.stats.atb_rate * dt
                    )
                if unit.atb >= unit.stats.threshold:
                    self.ready_queue.append(unit)

        self.enqueue_ready_units()
        anim_update(dt)

    def draw_field(self) -> None:  # pragma: no cover - visual
        for lane_y in LANE_Y:
            arcade.draw_line(0, lane_y, 800, lane_y, arcade.color.DARK_SLATE_GRAY)
        for unit in self.units.values():
            if unit.state == "DEAD":
                continue
            x, y = unit.pos
            color = arcade.color.BLUE if unit.side == "ally" else arcade.color.RED
            arcade.draw_circle_filled(x, y, 20, color)
            draw_atb_bar(unit)

    def draw_effect(self) -> None:  # pragma: no cover - visual
        anim_draw()

    # placeholders for API compatibility
    def enqueue_ready_units(self) -> None:
        ready = list(self.ready_queue)
        self.ready_queue.clear()
        ready.sort(key=lambda u: (-u.stats.spd, -u.atb, random()))  # noqa: S311
        for unit in ready:
            if unit.side == "ally":
                self.start_command(unit)
            else:
                target = self._find_target(unit)
                if target:
                    self.decide_action(unit, "melee_punch", target)

    def start_command(self, unit: Unit) -> None:
        unit.state = "COMMAND"
        if self.on_command:
            self.on_command(unit)

    def decide_action(self, unit: Unit, skill_id: str, target: Unit) -> None:
        unit.action_queue.append(
            PlannedAction(skill_id=skill_id, user_id=unit.id, target_id=target.id)
        )
        unit.state = "CHARGE"

    def apply_action(self, pa: PlannedAction) -> None:
        user = self.units.get(pa.user_id)
        target = self.units.get(pa.target_id)
        if not user or not target or target.state == "DEAD":
            return
        skill = SKILLS.get(pa.skill_id)
        if not skill:
            return
        play_effect(skill.get("effect", ""), user, target)
        if random() > skill.get("hit", 1.0):  # noqa: S311
            self.last_message = f"{user.name} の {skill['name']} は ミス！"
            pop_damage(0, target.pos)
            return
        dmg = max(1, skill["power"] + user.stats.atk - target.stats.defn)
        target.hp -= dmg
        pop_damage(dmg, target.pos)
        if target.hp <= 0:
            target.state = "DEAD"
            self.last_message = (
                f"{user.name} の {skill['name']}！ {target.name} を たおした!"
            )
        else:
            self.last_message = (
                f"{user.name} の {skill['name']}！ {target.name} に {dmg} ダメージ"
            )
        logger.info(self.last_message)

    def check_victory(self) -> str:
        allies = [
            u for u in self.units.values() if u.side == "ally" and u.state != "DEAD"
        ]
        enemies = [
            u for u in self.units.values() if u.side == "enemy" and u.state != "DEAD"
        ]
        if not allies:
            return "enemy"
        if not enemies:
            return "ally"
        return "ongoing"

    # helpers
    def _update_movement(self, unit: Unit, dt: float) -> None:
        speed = unit.stats.spd * PX_PER_SEC * dt * unit.facing
        unit.pos = (unit.pos[0] + speed, unit.pos[1])
        if unit.state == "CHARGE" and (
            (unit.facing > 0 and unit.pos[0] >= CENTER_X)
            or (unit.facing < 0 and unit.pos[0] <= CENTER_X)
        ):
            unit.pos = (CENTER_X, unit.pos[1])
            unit.state = "ACT"
        elif unit.state == "COOLDOWN" and (
            (unit.facing > 0 and unit.pos[0] >= unit.home_x)
            or (unit.facing < 0 and unit.pos[0] <= unit.home_x)
        ):
            unit.pos = (unit.home_x, unit.pos[1])
            unit.atb = 0.0
            unit.state = "IDLE"

    def _find_target(self, unit: Unit) -> Unit | None:
        enemies = [
            u for u in self.units.values() if u.side != unit.side and u.state != "DEAD"
        ]
        if not enemies:
            return None
        return min(enemies, key=lambda e: abs(e.pos[0] - unit.pos[0]))
