"""Title screen scene."""

from __future__ import annotations

import arcade

from ..core.input import InputRouter
from ..core.scene import BaseScene


class TitleScene(BaseScene):
    """Simple title screen with menu."""

    def __init__(self, window: arcade.Window) -> None:
        super().__init__(window)
        self.options = ["つづきから", "はじめから"]
        self.index = 0
        self.router = InputRouter(
            up=self.move_up,
            down=self.move_down,
            confirm=self.confirm,
            cancel=self.window.close,
        )

    def move_up(self) -> None:
        self.index = (self.index - 1) % len(self.options)

    def move_down(self) -> None:
        self.index = (self.index + 1) % len(self.options)

    def confirm(self) -> None:
        from .save_select import SaveSelectScene

        mode = "continue" if self.index == 0 else "new"
        self.window.scene_stack.push(SaveSelectScene(self.window, mode))

    # event forwarding
    def on_key_press(self, symbol: int, modifiers: int) -> None:
        self.router.on_key_press(symbol, modifiers)

    def on_draw(self) -> None:  # pragma: no cover - visuals
        self.window.clear()
        arcade.draw_text(
            "MEDABATTLE",
            self.window.width / 2,
            self.window.height - 100,
            anchor_x="center",
            font_size=40,
        )
        for i, opt in enumerate(self.options):
            color = arcade.color.YELLOW if i == self.index else arcade.color.WHITE
            arcade.draw_text(
                opt,
                self.window.width / 2,
                self.window.height / 2 - i * 40,
                color,
                font_size=24,
                anchor_x="center",
            )
