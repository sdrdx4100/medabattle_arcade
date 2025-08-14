"""Simple ATB battle scene."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import arcade

from ..core.input import InputRouter
from ..core.scene import BaseScene

GRID_W, GRID_H = 15, 9
TILE = 32
ATB_RATE = 0.5


@dataclass
class Unit:
    team: str
    x: int
    y: int
    color: arcade.Color
    hp: int = 10
    atb: float = 0.0

    @property
    def alive(self) -> bool:
        return self.hp > 0


class BattleScene(BaseScene):
    """Minimal ATB battle implementation."""

    def __init__(self, window: arcade.Window) -> None:
        super().__init__(window)
        self.units: List[Unit] = [
            Unit("player", 1, 2, arcade.color.BLUE),
            Unit("player", 1, 6, arcade.color.BLUE),
            Unit("enemy", 13, 2, arcade.color.RED),
            Unit("enemy", 13, 6, arcade.color.RED),
        ]
        self.queue: List[Unit] = []
        self.acting: Optional[Unit] = None
        self.state = "idle"
        self.command_index = 0
        self.router = InputRouter(menu=self.open_menu)

    # coordinate helpers
    def to_screen(self, x: int, y: int) -> tuple[float, float]:
        return (x * TILE + TILE / 2, y * TILE + TILE / 2)

    def open_menu(self) -> None:
        from .main_menu import MainMenuScene

        self.window.scene_stack.push(MainMenuScene(self.window))

    # drawing
    def on_draw(self) -> None:  # pragma: no cover - visuals
        arcade.start_render()
        # grid
        for x in range(GRID_W):
            arcade.draw_line(x * TILE, 0, x * TILE, GRID_H * TILE, arcade.color.GRAY)
        for y in range(GRID_H):
            arcade.draw_line(0, y * TILE, GRID_W * TILE, y * TILE, arcade.color.GRAY)
        # units
        for u in self.units:
            if not u.alive:
                continue
            sx, sy = self.to_screen(u.x, u.y)
            arcade.draw_rectangle_filled(sx, sy, TILE - 4, TILE - 4, u.color)
            # ATB bar
            bar_w = (TILE - 4) * min(u.atb, 1.0)
            arcade.draw_rectangle_filled(
                sx - (TILE - 4) / 2 + bar_w / 2,
                sy + TILE / 2,
                bar_w,
                4,
                arcade.color.GREEN,
            )
            # hp text
            arcade.draw_text(str(u.hp), sx - 8, sy - 8, arcade.color.WHITE, 12)
        # command menu
        if self.state == "command" and self.acting:
            opts = ["移動", "攻撃", "待機"]
            for i, opt in enumerate(opts):
                color = (
                    arcade.color.YELLOW
                    if i == self.command_index
                    else arcade.color.WHITE
                )
                arcade.draw_text(
                    opt, GRID_W * TILE + 20, GRID_H * TILE - 40 - i * 20, color, 14
                )

    # update loop
    def on_update(self, delta_time: float) -> None:
        if self.state != "idle":
            return
        for u in self.units:
            if not u.alive:
                continue
            if u.atb < 1.0:
                u.atb += delta_time * ATB_RATE
            if u.atb >= 1.0 and u not in self.queue:
                self.queue.append(u)
        if not self.acting and self.queue:
            self.acting = self.queue.pop(0)
            if self.acting.team == "player":
                self.state = "command"
                self.router = InputRouter(
                    up=self.cmd_up,
                    down=self.cmd_down,
                    confirm=self.cmd_confirm,
                    menu=self.open_menu,
                )
            else:
                self.enemy_act(self.acting)
                self.end_action()

    # player command handlers
    def cmd_up(self) -> None:
        self.command_index = (self.command_index - 1) % 3

    def cmd_down(self) -> None:
        self.command_index = (self.command_index + 1) % 3

    def cmd_confirm(self) -> None:
        assert self.acting
        if self.command_index == 0:
            # move: ask direction via arrow once
            self.state = "move"
            self.router = InputRouter(
                up=lambda: self.do_move(0, 1),
                down=lambda: self.do_move(0, -1),
                left=lambda: self.do_move(-1, 0),
                right=lambda: self.do_move(1, 0),
            )
        elif self.command_index == 1:
            self.do_attack()
            self.end_action()
        else:
            self.end_action()

    def do_move(self, dx: int, dy: int) -> None:
        assert self.acting
        nx, ny = self.acting.x + dx, self.acting.y + dy
        if 0 <= nx < GRID_W and 0 <= ny < GRID_H and not self.unit_at(nx, ny):
            self.acting.x, self.acting.y = nx, ny
        self.end_action()

    def do_attack(self) -> None:
        assert self.acting
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            target = self.unit_at(self.acting.x + dx, self.acting.y + dy, team="enemy")
            if target:
                target.hp -= 5
                break

    # utilities
    def unit_at(self, x: int, y: int, team: str | None = None) -> Optional[Unit]:
        for u in self.units:
            if u.alive and u.x == x and u.y == y and (team is None or u.team == team):
                return u
        return None

    def enemy_act(self, unit: Unit) -> None:
        # simple AI: move toward nearest player; if adjacent attack
        target = min(
            (u for u in self.units if u.team == "player" and u.alive),
            key=lambda p: abs(p.x - unit.x) + abs(p.y - unit.y),
        )
        if abs(target.x - unit.x) + abs(target.y - unit.y) == 1:
            target.hp -= 5
        else:
            dx = 1 if target.x > unit.x else -1 if target.x < unit.x else 0
            dy = 1 if target.y > unit.y else -1 if target.y < unit.y else 0
            if not self.unit_at(unit.x + dx, unit.y + dy):
                unit.x += dx
                unit.y += dy

    def end_action(self) -> None:
        assert self.acting
        self.acting.atb = 0.0
        self.state = "idle"
        self.acting = None
        self.router = InputRouter(menu=self.open_menu)
        self.check_end()

    def check_end(self) -> None:
        if not any(u.alive and u.team == "enemy" for u in self.units):
            from .battle_result import BattleResultScene

            self.window.scene_stack.replace(BattleResultScene(self.window, "win"))
        if not any(u.alive and u.team == "player" for u in self.units):
            from .battle_result import BattleResultScene

            self.window.scene_stack.replace(BattleResultScene(self.window, "lose"))

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        self.router.on_key_press(symbol, modifiers)
