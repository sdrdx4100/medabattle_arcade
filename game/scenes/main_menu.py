"""Main menu overlay scene."""

from __future__ import annotations

import time
import arcade

from ..core.input import InputRouter
from ..core.saveio import write_slot
from ..core.scene import BaseScene


class MainMenuScene(BaseScene):
    """Overlay menu with save option."""

    def __init__(self, window: arcade.Window) -> None:
        super().__init__(window)
        self.options = ["アイテム", "セーブ", "戻る"]
        self.index = 0
        self.toast: str | None = None
        self.toast_time = 0.0
        self.router = InputRouter(
            up=self.move_up,
            down=self.move_down,
            confirm=self.confirm,
            cancel=self.close,
        )

    def move_up(self) -> None:
        self.index = (self.index - 1) % len(self.options)

    def move_down(self) -> None:
        self.index = (self.index + 1) % len(self.options)

    def close(self) -> None:
        self.window.scene_stack.pop()

    def confirm(self) -> None:
        opt = self.options[self.index]
        if opt == "セーブ":
            slot = getattr(self.window, "save_slot", None)
            data = getattr(self.window, "save_data", None)
            if slot and data:
                write_slot(slot, data)
                self.toast = "セーブしました"
                self.toast_time = time.time()
        elif opt == "戻る":
            self.close()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        self.router.on_key_press(symbol, modifiers)

    def on_draw(self) -> None:  # pragma: no cover - visuals
        self.window.clear()
        arcade.draw_lbwh_rectangle_filled(
            self.window.width / 2 - 300 / 2,
            self.window.height / 2 - 300 / 2,
            300,
            300,
            (0, 0, 0, 180),
        )
        for i, opt in enumerate(self.options):
            color = arcade.color.YELLOW if i == self.index else arcade.color.WHITE
            arcade.draw_text(
                opt,
                self.window.width / 2,
                self.window.height / 2 - i * 40 + 80,
                color,
                font_size=24,
                anchor_x="center",
            )
        if self.toast and time.time() - self.toast_time < 2:
            arcade.draw_text(
                self.toast,
                self.window.width - 10,
                self.window.height - 30,
                arcade.color.WHITE,
                font_size=16,
                anchor_x="right",
            )
