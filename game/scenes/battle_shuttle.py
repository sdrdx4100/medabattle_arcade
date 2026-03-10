"""Shuttle-run style battle scene."""

from __future__ import annotations

from typing import Literal

import arcade

from ..battle.core.controller import ALLY_X, ENEMY_X, LANE_Y, SKILLS, BattleController
from ..battle.core.models import Part, PartSlot, Stats, Unit
from ..battle.ui.widgets import CommandMenu, MessageWindow, draw_team_panel
from ..core.input import InputRouter
from ..core.scene import BaseScene


class BattleShuttleScene(BaseScene):
    """Main battle scene implementing shuttle-run ATB."""

    def __init__(self, window: arcade.Window) -> None:
        super().__init__(window)
        self.controller = BattleController()
        self.router = InputRouter(menu=self.open_menu)
        self.command_menu = CommandMenu()
        self.msg_window = MessageWindow()
        self.command_unit: Unit | None = None
        self.command_phase = "idle"
        self.pending_part: Part | None = None
        self.target_candidates: list[Unit] = []
        self.controller.on_command = self.start_command
        self._setup_units()

    def _setup_units(self) -> None:
        ally_specs = [
            ("a0", "KBT-00 Kabuto", 40, 5, 3, 1.0),
            ("a1", "KWG-01 Kuwagata", 46, 6, 2, 1.15),
            ("a2", "SUP-02 Supporter", 50, 4, 4, 0.95),
        ]
        enemy_specs = [
            ("e0", "NIN-10 Shinobi", 36, 5, 2, 1.2),
            ("e1", "TNK-20 Tank", 34, 6, 5, 0.9),
            ("e2", "BMR-30 Bomber", 42, 5, 3, 1.0),
        ]
        for lane, (unit_id, name, atb_rate, atk, defn, spd) in enumerate(ally_specs):
            self.controller.add_unit(
                self._build_unit(
                    unit_id,
                    name,
                    "ally",
                    lane,
                    atb_rate=atb_rate,
                    atk=atk,
                    defn=defn,
                    spd=spd,
                )
            )
        for lane, (unit_id, name, atb_rate, atk, defn, spd) in enumerate(enemy_specs):
            self.controller.add_unit(
                self._build_unit(
                    unit_id,
                    name,
                    "enemy",
                    lane,
                    atb_rate=atb_rate,
                    atk=atk,
                    defn=defn,
                    spd=spd,
                )
            )

    def _build_unit(
        self,
        unit_id: str,
        name: str,
        side: Literal["ally", "enemy"],
        lane: int,
        *,
        atb_rate: float,
        atk: int,
        defn: int,
        spd: float,
    ) -> Unit:
        part_specs: list[tuple[PartSlot, str, str, int, int]] = [
            ("head", "Head", "head_missile", 12, 0),
            ("right_arm", "Right Arm", "right_rifle", 10, 1),
            ("left_arm", "Left Arm", "left_hammer", 11, 2),
            ("legs", "Legs", "leg_breaker", 14, 1),
        ]
        parts = {
            slot: Part(
                slot=slot,
                name=part_name,
                skill_id=skill_id,
                max_hp=hp,
                hp=hp,
                armor=armor,
            )
            for slot, part_name, skill_id, hp, armor in part_specs
        }
        max_hp = sum(part.max_hp for part in parts.values())
        home_x = ALLY_X if side == "ally" else ENEMY_X
        facing = 1 if side == "ally" else -1
        return Unit(
            id=unit_id,
            name=name,
            side=side,
            lane=lane,
            stats=Stats(
                max_hp=max_hp,
                atk=atk,
                defn=defn,
                spd=spd,
                atb_rate=atb_rate,
                threshold=100,
            ),
            hp=max_hp,
            pos=(home_x, LANE_Y[lane]),
            home_x=home_x,
            facing=facing,
            parts=parts,
        )

    def open_menu(self) -> None:
        from .main_menu import MainMenuScene  # type: ignore

        self.window.scene_stack.push(MainMenuScene(self.window))  # type: ignore[attr-defined]

    # event hooks
    def on_draw(self) -> None:  # pragma: no cover - visual
        self.window.clear()
        self.controller.draw_field()
        self._draw_target_highlight()
        draw_team_panel(
            "ALLY TEAM",
            self._team_units("ally"),
            x=10,
            y=self.window.height - 10,
            highlight_id=self.command_unit.id if self.command_unit else None,
        )
        draw_team_panel(
            "ENEMY TEAM",
            self._team_units("enemy"),
            x=self.window.width - 250,
            y=self.window.height - 10,
            highlight_id=self._selected_target_id(),
        )
        arcade.draw_text(
            "ATB COMMAND BATTLE  /  ↑↓:選択  Enter:決定  Esc:戻る  Tab:メニュー",
            self.window.width / 2,
            self.window.height - 22,
            arcade.color.WHITE,
            13,
            anchor_x="center",
        )
        self.command_menu.draw()
        self.msg_window.draw(self.window.width, self.window.height)
        self.controller.draw_effect()

    def on_update(self, delta_time: float) -> None:
        self.controller.update(delta_time)
        if self.command_unit and self.command_unit.state == "DEAD":
            self.msg_window.push(
                f"{self.command_unit.name} was disabled during command"
            )
            self._close_command_ui()
        if self.controller.last_message:
            self.msg_window.push(self.controller.last_message)
            self.controller.last_message = None
        result = self.controller.check_victory()
        if result != "ongoing":
            from .battle_result import BattleResultScene

            outcome = "win" if result == "ally" else "lose"
            self.window.scene_stack.replace(  # type: ignore[attr-defined]
                BattleResultScene(self.window, outcome)
            )

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        self.router.on_key_press(symbol, modifiers)

    # command menu handlers
    def start_command(self, unit: Unit) -> None:
        self.command_unit = unit
        self.command_phase = "command"
        self.pending_part = None
        self.command_menu.set_options("PART COMMAND", self._command_options(unit))
        self.router = InputRouter(
            up=self.cmd_up,
            down=self.cmd_down,
            confirm=self.cmd_confirm,
            cancel=self.cmd_cancel,
            menu=self.open_menu,
        )

    def cmd_up(self) -> None:
        self.command_menu.index = (self.command_menu.index - 1) % len(
            self.command_menu.options
        )

    def cmd_down(self) -> None:
        self.command_menu.index = (self.command_menu.index + 1) % len(
            self.command_menu.options
        )

    def cmd_confirm(self) -> None:
        if not self.command_unit:
            return
        if self.command_phase == "command":
            parts = self.command_unit.available_parts()
            if self.command_menu.index >= len(parts):
                self.command_unit.atb = 0.0
                self.command_unit.state = "IDLE"
                self.msg_window.push(f"{self.command_unit.name} waits")
                self._close_command_ui()
                return
            self.pending_part = parts[self.command_menu.index]
            self.target_candidates = self._living_targets("enemy")
            if not self.target_candidates:
                self.msg_window.push("No target available")
                self.command_unit.atb = 0.0
                self.command_unit.state = "IDLE"
                self._close_command_ui()
                return
            self.command_phase = "target"
            self.command_menu.set_options(
                "TARGET SELECT",
                [
                    f"{target.name} / HP {target.hp}"
                    for target in self.target_candidates
                ],
            )
        else:
            if not self.pending_part or not self.target_candidates:
                return
            target = self.target_candidates[self.command_menu.index]
            self.controller.decide_action(
                self.command_unit,
                self.pending_part.skill_id,
                target,
                self.pending_part.slot,
            )
            skill_name = SKILLS[self.pending_part.skill_id]["name"]
            self.msg_window.push(
                f"{self.command_unit.name} selected "
                f"{self.pending_part.name} / {skill_name}"
            )
            self._close_command_ui()

    def cmd_cancel(self) -> None:
        if self.command_phase == "target":
            if self.command_unit:
                self.command_phase = "command"
                self.pending_part = None
                self.command_menu.set_options(
                    "PART COMMAND", self._command_options(self.command_unit)
                )
            return
        if self.command_unit:
            self.command_unit.atb = 0.0
            self.command_unit.state = "IDLE"
            self.msg_window.push(f"{self.command_unit.name} waits")
        self._close_command_ui()

    def _command_options(self, unit: Unit) -> list[str]:
        options = []
        for part in unit.available_parts():
            skill = SKILLS[part.skill_id]
            options.append(
                f"{part.name:<10} / {skill['name']} / aim {skill['target_part']}"
            )
        options.append("Wait")
        return options

    def _team_units(self, side: str) -> list[Unit]:
        return [unit for unit in self.controller.units.values() if unit.side == side]

    def _living_targets(self, side: str) -> list[Unit]:
        return [unit for unit in self._team_units(side) if unit.state != "DEAD"]

    def _close_command_ui(self) -> None:
        self.command_menu.visible = False
        self.command_phase = "idle"
        self.pending_part = None
        self.target_candidates = []
        self.command_unit = None
        self.router = InputRouter(menu=self.open_menu)

    def _selected_target_id(self) -> str | None:
        if (
            self.command_phase == "target"
            and self.target_candidates
            and self.command_menu.index < len(self.target_candidates)
        ):
            return self.target_candidates[self.command_menu.index].id
        return None

    def _draw_target_highlight(self) -> None:  # pragma: no cover - visual
        target_id = self._selected_target_id()
        if not target_id:
            return
        target = self.controller.units[target_id]
        arcade.draw_circle_outline(
            target.pos[0],
            target.pos[1],
            30,
            arcade.color.YELLOW,
            3,
        )
