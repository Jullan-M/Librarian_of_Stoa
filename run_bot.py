import asyncio
import os
from dotenv import load_dotenv
from discord.ext import commands
from Librarian import Librarian

load_dotenv(dotenv_path='.env')
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix=".")
bot.add_cog(Librarian(bot))

def is_guild_owner():
    def predicate(ctx):
        return ctx.guild is not None and ctx.guild.owner_id == ctx.author.id
    return commands.check(predicate)

@bot.command(name='add_cog')
@commands.check_any(commands.is_owner(), is_guild_owner())
async def add_cog(ctx, cog_name: str):
    bot.load_extension(cog_name)

@bot.command(name='remove_cog')
@commands.check_any(commands.is_owner(), is_guild_owner())
async def remove_cog(ctx, cog_name: str):
    bot.remove_cog(cog_name)

bot.run(TOKEN)
