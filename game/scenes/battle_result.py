"""Battle result scene."""

from __future__ import annotations

import time
import arcade

from ..core.scene import BaseScene


class BattleResultScene(BaseScene):
    """Display battle outcome then return to main menu."""

    def __init__(self, window: arcade.Window, result: str) -> None:
        super().__init__(window)
        self.result = result
        self.start = time.time()

    def on_draw(self) -> None:  # pragma: no cover - visuals
        arcade.start_render()
        text = "勝利" if self.result == "win" else "敗北"
        arcade.draw_text(
            text,
            self.window.width / 2,
            self.window.height / 2,
            anchor_x="center",
            font_size=40,
            color=arcade.color.WHITE,
        )

    def on_update(self, delta_time: float) -> None:
        if time.time() - self.start > 2:
            from .main_menu import MainMenuScene

            self.window.scene_stack.replace(MainMenuScene(self.window))
