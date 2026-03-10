"""Battle controller managing shuttle-run combat."""

from __future__ import annotations

import json
import logging
from collections import deque
from collections.abc import Callable
from pathlib import Path
from random import random
from typing import cast

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
from .models import PART_SLOTS, Part, PartSlot, PlannedAction, Unit

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
        unit.sync_hp()
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
            arcade.draw_text(
                f"{unit.name}  HP {unit.hp}",
                x,
                y + 28,
                arcade.color.WHITE,
                12,
                anchor_x="center",
            )

    def draw_effect(self) -> None:  # pragma: no cover - visual
        anim_draw()

    # placeholders for API compatibility
    def enqueue_ready_units(self) -> None:
        ready = list(self.ready_queue)
        self.ready_queue.clear()
        ready.sort(key=lambda u: (-u.stats.spd, -u.atb, random()))  # noqa: S311
        player_command_open = any(
            unit.side == "ally" and unit.state == "COMMAND"
            for unit in self.units.values()
        )
        deferred_allies: list[Unit] = []
        for unit in ready:
            if unit.state != "IDLE":
                continue
            if unit.side == "ally":
                if player_command_open:
                    deferred_allies.append(unit)
                    continue
                self.start_command(unit)
                player_command_open = True
            else:
                self._decide_enemy_action(unit)
        for unit in deferred_allies:
            self.ready_queue.append(unit)

    def start_command(self, unit: Unit) -> None:
        unit.state = "COMMAND"
        if self.on_command:
            self.on_command(unit)

    def decide_action(
        self,
        unit: Unit,
        skill_id: str,
        target: Unit,
        source_slot: PartSlot | None = None,
    ) -> None:
        unit.action_queue.append(
            PlannedAction(
                skill_id=skill_id,
                user_id=unit.id,
                target_id=target.id,
                source_slot=source_slot,
            )
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
        if pa.source_slot:
            source_part = user.get_part(pa.source_slot)
            if not source_part or not source_part.is_operational:
                self.last_message = f"{user.name} cannot act: source part broken!"
                return
        play_effect(skill.get("effect", ""), user, target)
        if random() > skill.get("hit", 1.0):  # noqa: S311
            self.last_message = f"{user.name}'s {skill['name']} missed!"
            pop_damage(0, target.pos)
            return
        target_slot = skill.get("target_part", "head")
        if target_slot not in PART_SLOTS:
            target_slot = "head"
        target_part = self._resolve_target_part(target, cast(PartSlot, target_slot))
        if not target_part:
            self.last_message = f"{target.name} is already disabled!"
            target.state = "DEAD"
            target.hp = 0
            return
        dmg = max(
            1,
            skill["power"] + user.stats.atk - target.stats.defn - target_part.armor,
        )
        target_part.hp = max(0, target_part.hp - dmg)
        target.sync_hp()
        pop_damage(dmg, target.pos)
        if target_part.hp <= 0:
            part_break = f"{target.name}'s {target_part.name} broke!"
        else:
            part_break = ""
        if self._is_unit_destroyed(target):
            target.state = "DEAD"
            target.hp = 0
            self.last_message = f"{user.name}'s {skill['name']} disabled {target.name}!"
        else:
            action_message = (
                f"{user.name}'s {skill['name']} hit {target.name} for {dmg}"
            )
            self.last_message = (
                f"{action_message} / {part_break}" if part_break else action_message
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

    def _decide_enemy_action(self, unit: Unit) -> None:
        actions = unit.available_parts()
        if not actions:
            unit.atb = 0.0
            return
        target = self._find_weakest_target(unit)
        if not target:
            return
        chosen_part = max(actions, key=lambda part: SKILLS[part.skill_id]["power"])
        self.decide_action(unit, chosen_part.skill_id, target, chosen_part.slot)

    def _find_weakest_target(self, unit: Unit) -> Unit | None:
        enemies = [
            target
            for target in self.units.values()
            if target.side != unit.side and target.state != "DEAD"
        ]
        if not enemies:
            return None
        return min(enemies, key=lambda target: (target.hp, target.lane))

    def _resolve_target_part(self, target: Unit, preferred: PartSlot) -> Part | None:
        preferred_part = target.get_part(preferred) if preferred else None
        if preferred_part and preferred_part.is_operational:
            return preferred_part
        for part in target.parts.values():
            if part.is_operational:
                return part
        return None

    def _is_unit_destroyed(self, target: Unit) -> bool:
        head = target.get_part("head")
        return (head is not None and not head.is_operational) or all(
            not part.is_operational for part in target.parts.values()
        )
