"""Save slot selection scene."""

from __future__ import annotations

import arcade

from ..core.input import InputRouter
from ..core.saveio import SaveData, init_slot, load_slot
from ..core.scene import BaseScene


class SaveSelectScene(BaseScene):
    """Allow the player to choose a save slot."""

    def __init__(self, window: arcade.Window, mode: str) -> None:
        super().__init__(window)
        self.mode = mode  # "continue" or "new"
        self.index = 0
        self.router = InputRouter(
            up=self.move_up,
            down=self.move_down,
            confirm=self.confirm,
            cancel=self.cancel,
        )

    def move_up(self) -> None:
        self.index = (self.index - 1) % 3

    def move_down(self) -> None:
        self.index = (self.index + 1) % 3

    def cancel(self) -> None:
        self.window.scene_stack.pop()

    def confirm(self) -> None:
        slot = self.index + 1
        data = load_slot(slot)
        if self.mode == "new" and data is None:
            data = init_slot(slot)
        if data is None:
            return  # cannot continue empty slot
        self.window.save_slot = slot  # type: ignore[attr-defined]
        self.window.save_data = data  # type: ignore[attr-defined]
        from .story import StoryScene
        from .main_menu import MainMenuScene

        story = StoryScene(self.window)
        self.window.scene_stack.replace(story)
        self.window.scene_stack.push(MainMenuScene(self.window))

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        self.router.on_key_press(symbol, modifiers)

    def on_draw(self) -> None:  # pragma: no cover - visuals
        self.window.clear()
        arcade.draw_text(
            "セーブスロット",
            self.window.width / 2,
            self.window.height - 100,
            anchor_x="center",
            font_size=32,
        )
        for i in range(3):
            slot = i + 1
            data = load_slot(slot)
            text = f"{slot}: " + (
                f"{data.player_name} Lv{data.progress}" if data else "----"
            )
            color = arcade.color.YELLOW if i == self.index else arcade.color.WHITE
            arcade.draw_text(
                text,
                self.window.width / 2,
                self.window.height / 2 - i * 40,
                color,
                font_size=24,
                anchor_x="center",
            )
