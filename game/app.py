"""Main application window."""

from __future__ import annotations

import logging
from typing import Any

import arcade

from .core.config import load_config
from .core.scene import SceneStack


logger = logging.getLogger(__name__)


class MainApp(arcade.Window):
    """Main Arcade window hosting a SceneStack."""

    def __init__(self) -> None:
        cfg = load_config()
        super().__init__(cfg.window_width, cfg.window_height, cfg.window_title)
        logging.basicConfig(level=logging.INFO)
        self.scene_stack = SceneStack(self)
        self.save_slot: int | None = None
        self.save_data = None

        from .scenes.title import TitleScene

        self.scene_stack.push(TitleScene(self))

    def on_draw(self) -> None:
        self.clear()
        self.scene_stack.on_draw()

    def on_update(self, delta_time: float) -> None:
        self.scene_stack.on_update(delta_time)

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        self.scene_stack.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        self.scene_stack.on_key_release(symbol, modifiers)
