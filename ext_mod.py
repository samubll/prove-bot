"""Extra moderation module for complex_bot.

Contains additional commands and helpers to push complexity.

Commands here are prefixed commands that operate on the existing
SQLite schema in complex_bot/bot.py (warns table), plus extra
in-memory helpers.

When imported by `bot.py`, you can call register_mod_commands(bot).
"""

from __future__ import annotations

import time
from typing import Optional

import discord
from discord.ext import commands


def utc_epoch() -> int:
    return int(time.time())


def make_embed(title: str, desc: str, *, color: discord.Color) -> discord.Embed:
    return discord.Embed(title=title, description=desc, color=color)


# The following functions assume `db` object exposing get_conn() and get_conn().

async def purge_user_messages(ctx: commands.Context, user: discord.Member, limit: int = 50):
    if not ctx.guild:
        await ctx.send("Devi essere in un server")
        return

    # Bulk purge with predicate.
    async def predicate(m: discord.Message) -> bool:
        try:
            return m.author.id == user.id
        except Exception:
            return False

    deleted = await ctx.channel.purge(limit=limit, check=lambda m: getattr(m, "author", None) and m.author.id == user.id)
    await ctx.send(f"🧹 Eliminati {len(deleted)} messaggi di {user.mention}.")


async def role_autoban(ctx: commands.Context, target: discord.Member):
    # A lightweight example: remove roles except @everyone.
    if not ctx.guild:
        return

    if ctx.author.guild_permissions.manage_roles is False:
        await ctx.send("Non hai permessi")
        return

    roles = [r for r in target.roles if r.is_assignable() and r.name != "@everyone"]
    for r in roles:
        try:
            await target.remove_roles(r, reason="Auto mod")
        except Exception:
            pass
    await ctx.send(f"🧯 Auto-muta: rimossi ruoli a {target.mention}")


def register_mod_commands(bot: commands.Bot):
    @bot.command(name="mod_purge_user")
    @commands.has_permissions(administrator=True)
    async def _mod_purge_user(ctx: commands.Context, member: discord.Member, amount: int = 50):
        await purge_user_messages(ctx, member, limit=amount)

    @bot.command(name="mod_strip_roles")
    @commands.has_permissions(manage_roles=True)
    async def _mod_strip_roles(ctx: commands.Context, member: discord.Member):
        await role_autoban(ctx, member)

