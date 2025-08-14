"""Common input routing utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict

import arcade


@dataclass
class InputRouter:
    """Routes high level actions to callback functions."""

    up: Callable[[], None] | None = None
    down: Callable[[], None] | None = None
    left: Callable[[], None] | None = None
    right: Callable[[], None] | None = None
    confirm: Callable[[], None] | None = None
    cancel: Callable[[], None] | None = None
    menu: Callable[[], None] | None = None

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        mapping: Dict[int, Callable[[], None] | None] = {
            arcade.key.UP: self.up,
            arcade.key.DOWN: self.down,
            arcade.key.LEFT: self.left,
            arcade.key.RIGHT: self.right,
            arcade.key.ENTER: self.confirm,
            arcade.key.SPACE: self.confirm,
            arcade.key.ESCAPE: self.cancel,
            arcade.key.TAB: self.menu,
            arcade.key.M: self.menu,
        }
        cb = mapping.get(symbol)
        if cb:
            cb()
