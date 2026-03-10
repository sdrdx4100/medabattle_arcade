"""UI widgets for battle scenes."""

from __future__ import annotations

from collections import deque

import arcade

from ..core.models import PartSlot, Unit

BAR_W = 60
BAR_H = 6


def draw_atb_bar(unit: Unit) -> None:  # pragma: no cover - visual
    """Draw a simple ATB gauge under a unit."""
    ratio = unit.atb / unit.stats.threshold if unit.stats.threshold else 0
    x, y = unit.pos
    left = x - BAR_W / 2
    bottom = y - 30
    color = arcade.color.GREEN if unit.side == "ally" else arcade.color.ORANGE
    arcade.draw_lbwh_rectangle_filled(
        left,
        bottom,
        BAR_W,
        BAR_H,
        arcade.color.GRAY,
    )  # type: ignore[attr-defined]
    arcade.draw_lbwh_rectangle_filled(
        left,
        bottom,
        BAR_W * ratio,
        BAR_H,
        color,
    )  # type: ignore[attr-defined]


class CommandMenu:
    """Simple vertical menu for unit commands."""

    def __init__(self) -> None:
        self.title = "COMMAND"
        self.options: list[str] = []
        self.index = 0
        self.visible = False

    def set_options(self, title: str, options: list[str]) -> None:
        self.title = title
        self.options = options
        self.index = 0
        self.visible = bool(options)

    def draw(self) -> None:  # pragma: no cover - visual
        if not self.visible or not self.options:
            return
        base_x, base_y = 20, 170
        arcade.draw_lbwh_rectangle_filled(
            base_x - 10,
            base_y - 30 * len(self.options) - 35,
            260,
            30 * len(self.options) + 45,
            (0, 0, 0, 200),
        )  # type: ignore[attr-defined]
        arcade.draw_text(self.title, base_x, base_y + 5, arcade.color.CYAN, 16)
        for i, opt in enumerate(self.options):
            color = arcade.color.YELLOW if i == self.index else arcade.color.WHITE
            arcade.draw_text(opt, base_x, base_y - i * 30, color, 16)


class MessageWindow:
    """Bottom message log displaying up to two lines."""

    def __init__(self) -> None:
        self.lines: deque[str] = deque(maxlen=3)

    def push(self, text: str) -> None:
        self.lines.append(text)

    def draw(self, width: int, height: int) -> None:  # pragma: no cover - visual
        arcade.draw_lbwh_rectangle_filled(0, 0, width, 58, (0, 0, 0, 200))  # type: ignore[attr-defined]
        for i, line in enumerate(self.lines):
            arcade.draw_text(line, 10, 10 + i * 18, arcade.color.WHITE, 14)


def draw_team_panel(
    title: str,
    units: list[Unit],
    *,
    x: float,
    y: float,
    highlight_id: str | None = None,
) -> None:  # pragma: no cover - visual
    """Draw a compact status panel for a team."""
    line_height = 62
    width = 240
    height = 32 + line_height * len(units)
    arcade.draw_lbwh_rectangle_filled(x, y - height, width, height, (0, 0, 0, 150))  # type: ignore[attr-defined]
    arcade.draw_text(title, x + 10, y - 22, arcade.color.CYAN, 16)
    part_labels: dict[PartSlot, str] = {
        "head": "HEAD",
        "right_arm": "R-ARM",
        "left_arm": "L-ARM",
        "legs": "LEGS",
    }
    part_order: tuple[PartSlot, ...] = ("head", "right_arm", "left_arm", "legs")
    for i, unit in enumerate(units):
        base_y = y - 48 - i * line_height
        color = arcade.color.YELLOW if unit.id == highlight_id else arcade.color.WHITE
        state = "DOWN" if unit.state == "DEAD" else f"HP {unit.hp}"
        arcade.draw_text(f"{unit.name}  {state}", x + 10, base_y, color, 13)
        for offset, slot in enumerate(part_order):
            part = unit.get_part(slot)
            if part:
                part_text = (
                    f"{part_labels[slot]} {max(part.hp, 0)}/{part.max_hp}"
                    if part.is_operational
                    else f"{part_labels[slot]} BROKEN"
                )
                arcade.draw_text(
                    part_text,
                    x + 12,
                    base_y - 16 - offset * 11,
                    arcade.color.LIGHT_GRAY,
                    10,
                )
