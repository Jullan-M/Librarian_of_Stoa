import asyncio
import discord
import json
from discord.ext import commands

class Librarian(commands.Cog, name='Librarian'):
    def __init__(self, bot):
        self.bot = bot
        with open("books/meditations.json", "r", encoding="utf-8") as f:
            self.meditations = json.load(f)
        
        with open("books/enchiridion.json", "r", encoding="utf-8") as f:
            self.enchiridion = json.load(f)

        with open("books/letters.json", "r", encoding="utf-8") as f:
            self.letters = json.load(f)

        with open("media.json", "r", encoding="utf-8") as f:
            self.media = json.load(f)

    @commands.command(name='meditations', help="meditations.")
    async def meditations(self, ctx, psg_num: str):
        try:
            bk, cha = psg_num.split(":", maxsplit=1)
        except ValueError:
            return await ctx.send(f"{ctx.author.mention}, invalid formatting. The correct syntax is `<BOOK>:<CHAPTER>`, e.g., `5:23` for Book 5, Chapter 23.")
            
        if not (bk in self.meditations):
            return await ctx.send(f"{ctx.author.mention}, there is no Book `{bk}` of Meditations.")
            
        if not (cha in self.meditations[bk]):
            return await ctx.send(f"{ctx.author.mention}, there is no chapter `{cha}` in Book `{bk}` of Meditations.")
        
        passage = self.meditations[bk][cha].rstrip()
        aurelius = self.media["aurelius"]

        color = 0xFF0000 # Red
        if len(passage) > 4096:
            passage = passage[:4090] + " [...]"
        
        embed = discord.Embed(title=f"Meditations {bk}:{cha}", url=f"{aurelius['meditations']}{bk}", description=passage, color=color)
        embed.set_author(name="Marcus Aurelius", url=aurelius["url"], icon_url=aurelius["icon"])
        embed.set_thumbnail(url=aurelius["thumbnail"])        
        await ctx.send(embed=embed)

    @commands.command(name='enchiridion', help="enchiridion.")
    async def enchiridion(self, ctx, chapter: str):
        if not (chapter in self.enchiridion):
            return await ctx.send(f"{ctx.author.mention}, there is no chapter `{chapter}` in The Enchiridion.")
            
        passage = self.enchiridion[chapter].rstrip()
        epictetus = self.media["epictetus"]

        color = 0x00FF00 # Green
        if len(passage) > 4096:
            passage = passage[:4090] + " [...]"
        
        embed = discord.Embed(title=f"Enchiridion {chapter}", url=epictetus["enchiridion"], description=passage, color=color)
        embed.set_author(name="Epictetus", url=epictetus["url"], icon_url=epictetus["icon"])
        embed.set_thumbnail(url=epictetus["thumbnail"])        
        await ctx.send(embed=embed)

    @commands.command(name='letters', help="letters.")
    async def letters(self, ctx, psg_num: str):
        try:
            bk, cha = psg_num.split(":", maxsplit=1)
        except ValueError:
            return await ctx.send(f"{ctx.author.mention}, invalid formatting. The correct syntax is `<LETTER>:<PARAGRAPH>`, e.g., `99:4` for Letter 99, §4.")
            
        if not (bk in self.letters):
            return await ctx.send(f"{ctx.author.mention}, there is no letter `{bk}` of the Moral letters.")
            
        passage = None
        seneca = self.media["seneca"]
        if "-" in cha:
            cha1, cha2 = cha.split("-", maxsplit=1)
            if int(cha2) <= int(cha1) or not (cha1 in self.letters[bk] and cha2 in self.letters[bk]):
                return await ctx.send(f"{ctx.author.mention}, `{cha1}-{cha2}` is not a valid range.")
            passage = " ".join([self.letters[bk][str(ch)] for ch in range(int(cha1), int(cha2) + 1)]).rstrip()
        else:
            if not (cha in self.letters[bk]):
                return await ctx.send(f"{ctx.author.mention}, there is no paragraph `{cha}` in letter `{bk}` of the Moral letters.")
            passage = self.letters[bk][cha].rstrip()
        
        
        color = 0x0000FF # Red
        if len(passage) > 4096:
            passage = passage[:4090] + " [...]"
        
        embed = discord.Embed(title=f"Moral letters to Lucilius: Letter {bk}, §{cha}", url=f"{seneca['letters']}{bk}", description=passage, color=color)
        embed.set_author(name="Seneca the Younger", url=seneca["url"], icon_url=seneca["icon"])
        embed.set_thumbnail(url=seneca["thumbnail"])        
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Librarian(bot))