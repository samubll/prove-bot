"""Extra economy features for complex_bot.

Adds extra helper functions, payout tables and economy calculators.
Used by main bot for new commands.

This module is designed to add meaningful code volume via
well-scoped logic.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ItemDrop:
    key: str
    weight: float
    min_level: int
    max_level: int


# More drop candidates.
DROP_TABLE = [
    ItemDrop(key="cola", weight=60, min_level=1, max_level=5),
    ItemDrop(key="scroll", weight=30, min_level=1, max_level=7),
    ItemDrop(key="sandwich", weight=18, min_level=2, max_level=10),
    ItemDrop(key="core", weight=8, min_level=3, max_level=14),
    ItemDrop(key="ticket", weight=15, min_level=1, max_level=8),
]


def weighted_drop() -> str:
    total = sum(d.weight for d in DROP_TABLE)
    r = random.random() * total
    upto = 0.0
    for d in DROP_TABLE:
        upto += d.weight
        if upto >= r:
            return d.key
    return DROP_TABLE[-1].key


def roll_level(user_level: int) -> int:
    # level scales with user level, with cap.
    base = random.randint(1, 4)
    bump = max(0, user_level - 1) // 3
    val = base + bump + random.randint(-1, 2)
    return max(1, min(25, val))


def xp_for_action(action: str, level: int) -> int:
    base_map = {
        "spin": 35,
        "trivia": 70,
        "duel_win": 55,
        "duel_lose": 18,
        "craft": 140,
        "market_match": 95,
        "daily": 90,
        "work": 40,
    }
    base = base_map.get(action, 25)
    return int(base + level * 2.5)


def coins_multiplier_for_level(level: int) -> float:
    return 1.0 + min(0.5, max(0, level - 1) * 0.02)


def compute_house_edge() -> float:
    # intentionally dynamic edge
    return random.uniform(0.03, 0.07)


def compute_slot_payout(bet: int, score: int, level: int) -> int:
    mult = 1.0 + min(1.0, level * 0.015)
    payout = int(bet * score * mult / 10)
    return max(0, payout)

