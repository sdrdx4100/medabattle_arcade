"""UI widgets for battle scenes."""

from __future__ import annotations

from collections import deque

import arcade

from ..core.models import Unit

BAR_W = 60
BAR_H = 6


def draw_atb_bar(unit: Unit) -> None:  # pragma: no cover - visual
    """Draw a simple ATB gauge under a unit."""
    ratio = unit.atb / unit.stats.threshold if unit.stats.threshold else 0
    x, y = unit.pos
    left = x - BAR_W / 2
    bottom = y - 30
    color = arcade.color.GREEN if unit.side == "ally" else arcade.color.ORANGE
    arcade.draw_rectangle_filled(  # type: ignore[attr-defined]
        left + BAR_W / 2,
        bottom + BAR_H / 2,
        BAR_W,
        BAR_H,
        arcade.color.GRAY,
    )
    arcade.draw_rectangle_filled(  # type: ignore[attr-defined]
        left + (BAR_W * ratio) / 2,
        bottom + BAR_H / 2,
        BAR_W * ratio,
        BAR_H,
        color,
    )


class CommandMenu:
    """Simple vertical menu for unit commands."""

    def __init__(self) -> None:
        self.options = ["たたかう", "待機"]
        self.index = 0
        self.visible = False

    def draw(self) -> None:  # pragma: no cover - visual
        if not self.visible:
            return
        base_x, base_y = 20, 80
        arcade.draw_lbwh_rectangle_filled(
            base_x - 10,
            base_y - 30 * len(self.options),
            120,
            30 * len(self.options),
            (0, 0, 0, 200),
        )  # type: ignore[attr-defined]
        for i, opt in enumerate(self.options):
            color = arcade.color.YELLOW if i == self.index else arcade.color.WHITE
            arcade.draw_text(opt, base_x, base_y - i * 30, color, 16)


class MessageWindow:
    """Bottom message log displaying up to two lines."""

    def __init__(self) -> None:
        self.lines: deque[str] = deque(maxlen=2)

    def push(self, text: str) -> None:
        self.lines.append(text)

    def draw(self, width: int, height: int) -> None:  # pragma: no cover - visual
        arcade.draw_lbwh_rectangle_filled(0, 0, width, 40, (0, 0, 0, 200))  # type: ignore[attr-defined]
        for i, line in enumerate(self.lines):
            arcade.draw_text(line, 10, 10 + i * 18, arcade.color.WHITE, 14)
