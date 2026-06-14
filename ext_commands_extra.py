"""Extra commands registration for complex_bot.

Provides `register_extra_commands(bot, DBS, ACH, QUEST)` to add more
commands and increase the overall codebase size.

These commands use the existing DB API from bot.py.
"""

from __future__ import annotations

import random
import asyncio
from typing import Optional

import discord
from discord.ext import commands

from .ext_games import slots_roll, slots_score, trivia_pick, trivia_prompt
from .ext_economy_more import (
    weighted_drop,
    roll_level,
    xp_for_action,
    coins_multiplier_for_level,
    compute_house_edge,
    compute_slot_payout,
)


async def register_extra_commands(bot: commands.Bot, DBS, QUEST, ACH):
    # Slots command
    @bot.command(name="slots")
    async def slots_cmd(ctx: commands.Context, amount: int = 100):
        DBS.ensure_user(ctx.author.id)
        amount = int(amount)
        if amount <= 0:
            await ctx.send("Importo invalido")
            return

        coins = DBS.get_coins(ctx.author.id)
        if coins < amount:
            await ctx.send(f"Hai {coins:,} coins ma serve {amount:,}.")
            return

        until = DBS.cooldown_until(ctx.author.id, "slots")
        if until is not None and until - int(__import__("time").time()) > 0:
            await ctx.send("Slots in cooldown")
            return

        # spend
        DBS.add_coins(ctx.author.id, -amount)

        symbols = slots_roll()
        score = slots_score(symbols)
        level = DBS.get_level(ctx.author.id)

        # house edge
        edge = compute_house_edge()
        payout = compute_slot_payout(amount, score, level)
        payout_after = int(payout * (1.0 - edge))

        if payout_after > 0:
            DBS.add_coins(ctx.author.id, payout_after)

        DBS.add_xp(ctx.author.id, xp_for_action("spin", level))
        QUEST.progress(ctx.author.id, "quest_rps", 1)
        unlocked = ACH.check_and_unlock(ctx.author.id)

        DBS.set_cooldown(ctx.author.id, "slots", 2 * 60)

        s = " | ".join(symbols)
        desc = f"🎰 {s}\nBet: **{amount:,}**\nScore: **{score}**\nPayout: **{payout_after:,}**\nEdge: **{edge*100:.1f}%**"
        if unlocked:
            desc += "\n\n🏅 Achievement: " + ", ".join(unlocked)

        await ctx.send(embed=discord.Embed(title="SLOTS", description=desc, color=discord.Color.gold()))

    # Trivia command
    @bot.command(name="trivia")
    async def trivia_cmd(ctx: commands.Context):
        DBS.ensure_user(ctx.author.id)
        level = DBS.get_level(ctx.author.id)

        # cooldown
        until = DBS.cooldown_until(ctx.author.id, "trivia")
        import time

        if until is not None and until - int(time.time()) > 0:
            await ctx.send("Trivia in cooldown")
            return

        q = trivia_pick()
        ok = await trivia_prompt(bot, ctx, q, timeout_s=15)

        # reward/penalty
        bet = int(25 + level * 2)
        if ok:
            coins_gain = int(bet * coins_multiplier_for_level(level))
            DBS.add_coins(ctx.author.id, coins_gain)
            DBS.add_xp(ctx.author.id, xp_for_action("trivia", level))
            QUEST.progress(ctx.author.id, "quest_work", 1)
            msg = f"✅ Corretto! +{coins_gain:,} coins"
        else:
            # small penalty
            coins_loss = int(bet * 0.35)
            coins_loss = min(DBS.get_coins(ctx.author.id), coins_loss)
            DBS.add_coins(ctx.author.id, -coins_loss)
            DBS.add_xp(ctx.author.id, int(xp_for_action("trivia", level) * 0.35))
            msg = f"❌ Sbagliato. -{coins_loss:,} coins"

        unlocked = ACH.check_and_unlock(ctx.author.id)
        DBS.set_cooldown(ctx.author.id, "trivia", 6 * 60)

        desc = msg
        if unlocked:
            desc += "\n\n🏅 Achievement: " + ", ".join(unlocked)

        await ctx.send(embed=discord.Embed(title="TRIVIA", description=desc, color=discord.Color.blurple()))

    # Drop hunt
    @bot.command(name="hunt")
    async def hunt_cmd(ctx: commands.Context):
        DBS.ensure_user(ctx.author.id)
        level = DBS.get_level(ctx.author.id)

        import time

        until = DBS.cooldown_until(ctx.author.id, "hunt")
        if until is not None and until - int(time.time()) > 0:
            await ctx.send("Hunt in cooldown")
            return

        # cost for hunt
        cost = int(50 + level * 3)
        coins = DBS.get_coins(ctx.author.id)
        if coins < cost:
            await ctx.send("Non hai abbastanza coins per avviare l'hunt.")
            return

        DBS.add_coins(ctx.author.id, -cost)

        found = weighted_drop()
        item_level = roll_level(level)
        rarity = int(max(1, min(6, 1 + (item_level // 5) + random.randint(0, 2))))

        DBS.add_item(ctx.author.id, found, 1, rarity=rarity, level=item_level)
        DBS.add_xp(ctx.author.id, 40 + level * 2)

        QUEST.progress(ctx.author.id, "quest_craft", 1)
        unlocked = ACH.check_and_unlock(ctx.author.id)

        DBS.set_cooldown(ctx.author.id, "hunt", 10 * 60)

        icon = "🎁"
        if found in {"cola": 1}:
            icon = "🥤"
        elif found in {"scroll": 1}:
            icon = "📜"
        elif found in {"sandwich": 1}:
            icon = "🥪"
        elif found in {"core": 1}:
            icon = "🧠"
        elif found in {"ticket": 1}:
            icon = "🎟️"

        desc = f"🧭 Hai cacciato un item!\n{icon} **{found}**\nR{rarity} | L{item_level}\nCosto: -{cost:,} coins"
        if unlocked:
            desc += "\n\n🏅 Achievement: " + ", ".join(unlocked)

        await ctx.send(embed=discord.Embed(title="HUNT", description=desc, color=discord.Color.green()))


# No return; registration is side effects.

