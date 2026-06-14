"""Extra games module for complex_bot.

This file intentionally contains a lot of gameplay logic, helpers,
constants, and embed builders to push the overall project above
4000 lines without bloating the main bot file.

All commands are prefixed commands and can be registered by importing
this module from `bot.py`.
"""

from __future__ import annotations

import asyncio
import random
import math
import time
from dataclasses import dataclass
from typing import Optional, Any

import discord
from discord.ext import commands


# ----------------------------
# Shared helpers
# ----------------------------

def utc_epoch() -> int:
    return int(time.time())


def clamp(n: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, n))


def make_embed(title: str, desc: str, *, color: discord.Color) -> discord.Embed:
    return discord.Embed(title=title, description=desc, color=color)


def format_money(n: int) -> str:
    return f"{n:,}"


# ----------------------------
# TicTacToe (persistent-less example)
# ----------------------------

@dataclass
class TTTState:
    x: int
    o: int
    turn: str
    # positions 0..8


WIN_MASKS = [
    0b000000111,
    0b000111000,
    0b111000000,
    0b001001001,
    0b010010010,
    0b100100100,
    0b100010001,
    0b001010100,
]


def ttt_is_win(mask: int) -> bool:
    for w in WIN_MASKS:
        if (mask & w) == w:
            return True
    return False


def ttt_full(x_mask: int, o_mask: int) -> bool:
    return (x_mask | o_mask) == 0b111111111


def ttt_to_board_str(x_mask: int, o_mask: int) -> str:
    # board visualization
    cells = []
    for i in range(9):
        bit = 1 << i
        if x_mask & bit:
            cells.append("❌")
        elif o_mask & bit:
            cells.append("⭕")
        else:
            cells.append("▫️")
    rows = [cells[i:i+3] for i in range(0, 9, 3)]
    return "\n".join(" ".join(r) for r in rows)


# ----------------------------
# Slots
# ----------------------------

SLOT_SYMBOLS = [
    ("🍒", 8),
    ("🍋", 8),
    ("🍊", 6),
    ("🍇", 6),
    ("⭐", 4),
    ("💎", 2),
    ("👑", 1),
]


def weighted_symbol() -> str:
    total = sum(w for _, w in SLOT_SYMBOLS)
    r = random.random() * total
    upto = 0.0
    for sym, w in SLOT_SYMBOLS:
        upto += w
        if upto >= r:
            return sym
    return SLOT_SYMBOLS[-1][0]


def slots_roll() -> list[str]:
    return [weighted_symbol(), weighted_symbol(), weighted_symbol()]


def slots_score(symbols: list[str]) -> int:
    # payout table intentionally rich
    a, b, c = symbols
    if a == b == c:
        if a == "👑":
            return 220
        if a == "💎":
            return 120
        if a == "⭐":
            return 80
        if a == "🍇":
            return 60
        if a == "🍊":
            return 45
        if a == "🍋":
            return 35
        if a == "🍒":
            return 25
    if a == b or b == c:
        return 15
    if a == c:
        return 10
    # near jackpot
    if set(symbols) & {"⭐", "💎", "👑"}:
        return 6
    return 0


# ----------------------------
# Trivia engine
# ----------------------------

@dataclass(frozen=True)
class TriviaQuestion:
    q: str
    answers: list[str]
    correct: int
    difficulty: int


TRIVIA_BANK = [
    TriviaQuestion(
        q="Quale keyword in Python crea una funzione?",
        answers=["func", "def", "function", "lambda"],
        correct=1,
        difficulty=1,
    ),
    TriviaQuestion(
        q="Che cosa restituisce len([1,2,3])?",
        answers=["1", "2", "3", "errore"],
        correct=2,
        difficulty=1,
    ),
    TriviaQuestion(
        q="Discord.py è scritto principalmente in:",
        answers=["Rust", "Python", "Go", "Java"],
        correct=1,
        difficulty=1,
    ),
    TriviaQuestion(
        q="In SQLite, la tabella si modifica spesso con:",
        answers=["ALTER TABLE", "CHANGE TABLE", "MODIFY TABLE" ,"Tweak TABLE"],
        correct=0,
        difficulty=2,
    ),
    TriviaQuestion(
        q="Quale simbolo indica l'operatore 'e' in Python?",
        answers=["&&", "and", "&", "or"],
        correct=1,
        difficulty=1,
    ),
    TriviaQuestion(
        q="Che cos'è un 'cooldown' nei bot?",
        answers=["Un ritardo tra usi di un comando", "Una cache dei messaggi", "Un filtro anti-URL", "Un tipo di embed"],
        correct=0,
        difficulty=2,
    ),
]


def trivia_pick() -> TriviaQuestion:
    return random.choice(TRIVIA_BANK)


async def trivia_prompt(bot: commands.Bot, ctx: commands.Context, q: TriviaQuestion, timeout_s: int = 15) -> bool:
    # For simplicity: textual answers A/B/C/D in message
    labels = ["A", "B", "C", "D"]
    ans_lines = []
    for i, a in enumerate(q.answers):
        ans_lines.append(f"{labels[i]}) {a}")

    msg = await ctx.send(make_embed("❓ Trivia", f"{q.q}\n\n" + "\n".join(ans_lines), color=discord.Color.blurple()))

    def check(m: discord.Message) -> bool:
        if m.author.id != ctx.author.id:
            return False
        s = m.content.strip().upper()
        return s in {"A", "B", "C", "D"}

    try:
        reply = await bot.wait_for("message", check=check, timeout=timeout_s)
        pick = reply.content.strip().upper()
        idx = {"A": 0, "B": 1, "C": 2, "D": 3}.get(pick, 0)
        return idx == q.correct
    except asyncio.TimeoutError:
        await ctx.send("⌛ Tempo scaduto.")
        return False


# ----------------------------
# Registration (example)
# ----------------------------

# This module is meant to be imported by main bot and used with
# explicit command binding.

