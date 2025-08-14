"""Placeholder story scene."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Tuple

import arcade

from ..core.config import DATA_DIR
from ..core.input import InputRouter
from ..core.scene import BaseScene


class StoryScene(BaseScene):
    """Temporary story scene that goes to battle."""

    def __init__(self, window: arcade.Window) -> None:
        super().__init__(window)
        story_path = DATA_DIR / "story" / "episode01.json"
        raw: List[List[str]] = json.loads(story_path.read_text(encoding="utf-8"))
        self.messages: List[Tuple[str, str]] = [(m[0], m[1]) for m in raw]
        if not self.messages:
            # Fallback single empty message to avoid IndexError when story data is missing
            self.messages = [("", "")]
        self.index = 0
        self.router = InputRouter(confirm=self.advance, menu=self.open_menu)

    def on_draw(self) -> None:  # pragma: no cover - visuals
        self.window.clear()
        line1, line2 = self.messages[self.index]
        box_y = 100
        arcade.draw_lbwh_rectangle_filled(
            self.window.width / 2 - (self.window.width - 40) / 2,
            box_y - 100 / 2,
            self.window.width - 40,
            100,
            (0, 0, 0, 180),
        )
        arcade.draw_text(line1, 40, box_y + 20, arcade.color.WHITE, 18)
        arcade.draw_text(line2, 40, box_y - 10, arcade.color.WHITE, 18)

    def advance(self) -> None:
        self.index += 1
        if self.index >= len(self.messages):
            from .battle_atb import BattleScene

            self.window.scene_stack.replace(BattleScene(self.window))

    def open_menu(self) -> None:
        from .main_menu import MainMenuScene

        self.window.scene_stack.push(MainMenuScene(self.window))

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        self.router.on_key_press(symbol, modifiers)
