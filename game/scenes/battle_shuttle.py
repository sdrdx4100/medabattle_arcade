"""Shuttle-run style battle scene."""

from __future__ import annotations

import arcade

from ..battle.core.controller import ALLY_X, ENEMY_X, LANE_Y, BattleController
from ..battle.core.models import Stats, Unit
from ..battle.ui.widgets import CommandMenu, MessageWindow
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
        self.controller.on_command = self.start_command
        self._setup_units()

    def _setup_units(self) -> None:
        ally_rates = [40, 45, 50]
        enemy_rates = [35, 40, 45]
        for i in range(3):
            stats_a = Stats(
                max_hp=30,
                atk=5,
                defn=3,
                spd=1.0,
                atb_rate=ally_rates[i],
                threshold=100,
            )
            u = Unit(
                id=f"a{i}",
                name=f"Ally{i}",
                side="ally",
                lane=i,
                stats=stats_a,
                hp=stats_a.max_hp,
                pos=(ALLY_X, LANE_Y[i]),
                home_x=ALLY_X,
                facing=1,
            )
            self.controller.add_unit(u)
        for i in range(3):
            stats_b = Stats(
                max_hp=30,
                atk=5,
                defn=3,
                spd=1.0,
                atb_rate=enemy_rates[i],
                threshold=100,
            )
            u = Unit(
                id=f"e{i}",
                name=f"Enemy{i}",
                side="enemy",
                lane=i,
                stats=stats_b,
                hp=stats_b.max_hp,
                pos=(ENEMY_X, LANE_Y[i]),
                home_x=ENEMY_X,
                facing=-1,
            )
            self.controller.add_unit(u)

    def open_menu(self) -> None:
        from .main_menu import MainMenuScene  # type: ignore

        self.window.scene_stack.push(MainMenuScene(self.window))  # type: ignore[attr-defined]

    # event hooks
    def on_draw(self) -> None:  # pragma: no cover - visual
        self.window.clear()
        self.controller.draw_field()
        self.command_menu.draw()
        self.msg_window.draw(self.window.width, self.window.height)
        self.controller.draw_effect()

    def on_update(self, delta_time: float) -> None:
        self.controller.update(delta_time)
        if self.controller.last_message:
            self.msg_window.push(self.controller.last_message)
            self.controller.last_message = None
        self.controller.check_victory()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        self.router.on_key_press(symbol, modifiers)

    # command menu handlers
    def start_command(self, unit: Unit) -> None:
        self.command_unit = unit
        self.command_menu.visible = True
        self.command_menu.index = 0
        self.router = InputRouter(
            up=self.cmd_up,
            down=self.cmd_down,
            confirm=self.cmd_confirm,
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
        choice = self.command_menu.options[self.command_menu.index]
        if choice == "たたかう":
            target = self.controller._find_target(self.command_unit)
            if target:
                self.controller.decide_action(self.command_unit, "melee_punch", target)
            else:
                self.msg_window.push("ターゲットがいない")
                self.command_unit.atb = 0.0
                self.command_unit.state = "IDLE"
        else:
            self.command_unit.atb = 0.0
            self.command_unit.state = "IDLE"
            self.msg_window.push(f"{self.command_unit.name} は まった")
        self.command_menu.visible = False
        self.command_unit = None
        self.router = InputRouter(menu=self.open_menu)
