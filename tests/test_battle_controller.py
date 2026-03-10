"""Focused tests for the Medarot-like ATB battle controller."""

from __future__ import annotations

import unittest
from typing import Literal
from unittest.mock import patch

from game.battle.core.controller import BattleController
from game.battle.core.models import Part, PartSlot, Stats, Unit


def build_unit(
    unit_id: str,
    side: Literal["ally", "enemy"],
    *,
    lane: int = 0,
    head_hp: int = 12,
    right_hp: int = 10,
    left_hp: int = 11,
    legs_hp: int = 14,
    spd: float = 1.0,
) -> Unit:
    parts: dict[PartSlot, Part] = {
        "head": Part("head", "Head", "head_missile", head_hp, head_hp),
        "right_arm": Part("right_arm", "Right Arm", "right_rifle", right_hp, right_hp),
        "left_arm": Part("left_arm", "Left Arm", "left_hammer", left_hp, left_hp),
        "legs": Part("legs", "Legs", "leg_breaker", legs_hp, legs_hp),
    }
    unit = Unit(
        id=unit_id,
        name=unit_id,
        side=side,
        lane=lane,
        stats=Stats(
            max_hp=head_hp + right_hp + left_hp + legs_hp,
            atk=5,
            defn=3,
            spd=spd,
            atb_rate=50,
            threshold=100,
        ),
        hp=head_hp + right_hp + left_hp + legs_hp,
        parts=parts,
    )
    unit.sync_hp()
    return unit


class BattleControllerTests(unittest.TestCase):
    def test_apply_action_damages_targeted_part_and_syncs_hp(self) -> None:
        controller = BattleController()
        attacker = build_unit("ally", "ally")
        defender = build_unit("enemy", "enemy")
        controller.add_unit(attacker)
        controller.add_unit(defender)

        with patch("game.battle.core.controller.random", return_value=0.0):
            controller.decide_action(attacker, "right_rifle", defender, "right_arm")
            controller.apply_action(attacker.action_queue.pop(0))

        self.assertEqual(defender.parts["right_arm"].hp, 0)
        self.assertEqual(defender.hp, 37)
        self.assertNotEqual(defender.state, "DEAD")

    def test_head_break_defeats_unit(self) -> None:
        controller = BattleController()
        attacker = build_unit("ally", "ally")
        defender = build_unit("enemy", "enemy", head_hp=4)
        controller.add_unit(attacker)
        controller.add_unit(defender)

        with patch("game.battle.core.controller.random", return_value=0.0):
            controller.decide_action(attacker, "head_missile", defender, "head")
            controller.apply_action(attacker.action_queue.pop(0))

        self.assertEqual(defender.parts["head"].hp, 0)
        self.assertEqual(defender.hp, 0)
        self.assertEqual(defender.state, "DEAD")

    def test_second_ally_command_is_deferred_while_first_is_open(self) -> None:
        controller = BattleController()
        first_ally = build_unit("ally1", "ally", spd=2.0)
        second_ally = build_unit("ally2", "ally", spd=1.0)
        enemy = build_unit("enemy", "enemy")
        controller.add_unit(first_ally)
        controller.add_unit(second_ally)
        controller.add_unit(enemy)

        seen_commands: list[str] = []
        controller.on_command = lambda unit: seen_commands.append(unit.id)
        controller.ready_queue.append(first_ally)
        controller.ready_queue.append(second_ally)

        controller.enqueue_ready_units()

        self.assertEqual(seen_commands, ["ally1"])
        self.assertEqual(first_ally.state, "COMMAND")
        self.assertEqual(list(controller.ready_queue), [second_ally])


if __name__ == "__main__":
    unittest.main()
