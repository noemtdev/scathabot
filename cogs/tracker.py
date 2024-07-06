import discord
from discord.ext import commands

from discord import SlashCommandGroup, option
from util.db import add_tracker_uuid, get_stats, get_best, get_discord_id
from util.requests import Web

from constants import SCATHA_EMOJI, WORM_EMOJI, NOSCATHAS_EMOJI, user_role

class Tracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    tracker = SlashCommandGroup(name="tracker", description="Commands for tracking")

    @tracker.command(
        name="add",
        description="Starts tracking your user.",
    )
    @option(
        name="username",
        description="Your Minecraft Username",
        type=str,
        required=True,
    )
    @commands.check_any(commands.has_role(user_role), commands.is_owner())
    async def add_tracker(self, ctx: discord.ApplicationContext, username: str):
        await ctx.defer(ephemeral=True)

        web = Web()
        
        uuid, username = await web.get_uuid(username)
        if not uuid:
            await ctx.send("User not found.")
            return

        add_tracker_uuid(uuid, ctx.author.id)

        embed = discord.Embed(
            title=f"{SCATHA_EMOJI} Tracker Added",
            description=f"I am now tracking Scatha Kills for `{username}`",
            color=discord.Color.blue()
        )

        await ctx.respond(embed=embed)


    @tracker.command(
        name="stats",
        description="Shows your tracked stats.",
    )
    @commands.check_any(commands.has_role(user_role), commands.is_owner())
    async def tracker_stats(self, ctx: discord.ApplicationContext):
        await ctx.defer(ephemeral=True)

        stats = get_stats(ctx.author.id)
        if not stats:
            return await ctx.respond("You are not being tracked.")
        
        embed = discord.Embed(
            title=f"Your Scatha Stats",
            color=discord.Color.blue(),
            description=f"""
{SCATHA_EMOJI} **Scatha Kills:** {stats["scatha_kills"]}
{WORM_EMOJI} **Worm Kills:** {stats["worm_kills"]}

{NOSCATHAS_EMOJI} **Streaks**
**Dry Streak:** {stats["dry_streak"]}
**Highest Dry Streak:** {stats["max_dry_streak"]}"""
        )
        embed.set_footer(text='"Dry Streak" is the number of Worm Kills since your last Scatha Kill.')

        await ctx.respond(embed=embed)

    @tracker.command(
        name="leaderboard",
        description="Shows the leaderboard of tracked stats.",
    )
    @option(
        name="stat",
        description="The stat to sort by.",
        type=str,
        required=True,
        choices=["Scatha Kills", "Worm Kills", "Current Dry Streak", "Highest Dry Steak"],
    )
    async def tracker_leaderboard(self, ctx: discord.ApplicationContext, stat: str):
        await ctx.defer(ephemeral=True)

        stats_map = {
            "Scatha Kills": "scatha_kills",
            "Worm Kills": "worm_kills",
            "Current Dry Streak": "dry_streak",
            "Highest Dry Steak": "max_dry_streak",
        }

        best = get_best(stats_map[stat])

        embed = discord.Embed(
            title=f"Leaderboard for {stat}",
            color=discord.Color.blue(),
            description=""
        )

        rank_emojis = {
            0: "🥇",
            1: "🥈",
            2: "🥉",
        }

        subtract_index_by = 0
        for i, (uuid, value) in enumerate(best):

            discord_id = get_discord_id(uuid)
            if not discord_id:
                subtract_index_by += 1
                continue

            embed.description += f"{rank_emojis.get(i-subtract_index_by, '')} #{i+1-subtract_index_by} <@{discord_id}>: {value:,}\n"

        await ctx.respond(embed=embed)


    @add_tracker.error
    @tracker_stats.error
    async def add_tracker_error(self, ctx, error):
        await ctx.respond("You do not have the required role to use this command.", ephemeral=True)


def setup(bot):
    bot.add_cog(Tracker(bot))