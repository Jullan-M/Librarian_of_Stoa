import asyncio
import os

import discord
from discord.ext import bridge, commands
from dotenv import load_dotenv

from cogs.Help import Help
from cogs.Librarian import Librarian

load_dotenv(dotenv_path=".env")
TOKEN = os.getenv("DISCORD_TOKEN")

# Configure intents
intents = discord.Intents.default()
intents.message_content = True

bot = bridge.Bot(command_prefix=".", intents=intents)
bot.add_cog(Librarian(bot))
bot.add_cog(Help(bot))


def is_guild_owner():
    def predicate(ctx):
        return ctx.guild is not None and ctx.guild.owner_id == ctx.author.id

    return commands.check(predicate)


@bot.bridge_command(name="add_cog", hidden=True)
@commands.check_any(commands.is_owner(), is_guild_owner())
async def add_cog(ctx, cog_name: str):
    try:
        cog_dc = bot.load_extension(f"cogs.{cog_name}", store=False)
    except discord.ExtensionNotFound:
        await ctx.respond(f"No cog found with the name: `{cog_name}`")
        return
    except discord.ExtensionAlreadyLoaded:
        await ctx.respond(f"`{cog_name}` is already loaded.")
        return
    print(f"Loaded cog: {cog_name}")
    await ctx.respond(f"Added cog `{cog_name}`.")


@bot.bridge_command(name="remove_cog", hidden=True)
@commands.check_any(commands.is_owner(), is_guild_owner())
async def remove_cog(ctx, cog_name: str):
    cog = bot.remove_cog(cog_name)
    if not cog:
        await ctx.respond(f"No cog loaded with the name: `{cog_name}`")
        return
    print(f"Removed cog: {cog.qualified_name}")
    await ctx.respond(f"Removed cog `{cog.qualified_name}`.")


@bot.event
async def on_ready():
    print(f"--- {bot.user.name} ready ---")


bot.run(TOKEN)
