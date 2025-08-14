"""Scene base classes and stack manager."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import arcade


class BaseScene:
    """Base class for scenes."""

    def __init__(self, window: arcade.Window) -> None:
        self.window = window

    def on_draw(self) -> None:  # pragma: no cover - visual
        pass

    def on_update(self, delta_time: float) -> None:  # pragma: no cover - visual
        pass

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        pass

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        pass


class SceneStack:
    """Simple stack-based scene manager."""

    def __init__(self, window: arcade.Window) -> None:
        self.window = window
        self._stack: List[BaseScene] = []

    # stack operations
    def push(self, scene: BaseScene) -> None:
        self._stack.append(scene)

    def pop(self) -> Optional[BaseScene]:
        return self._stack.pop() if self._stack else None

    def replace(self, scene: BaseScene) -> None:
        self.pop()
        self.push(scene)

    # event forwarding
    def on_draw(self) -> None:
        if self._stack:
            self._stack[-1].on_draw()

    def on_update(self, delta_time: float) -> None:
        if self._stack:
            self._stack[-1].on_update(delta_time)

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if self._stack:
            self._stack[-1].on_key_press(symbol, modifiers)

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        if self._stack:
            self._stack[-1].on_key_release(symbol, modifiers)
