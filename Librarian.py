import asyncio
import discord
import json
import random
from discord.ext import commands
from utilities import int2roman, split_within

class Librarian(commands.Cog, name='Librarian'):
    def __init__(self, bot):
        self.bot = bot
        with open("books/meditations.json", "r", encoding="utf-8") as f:
            self.meditations = json.load(f)
        
        with open("books/enchiridion.json", "r", encoding="utf-8") as f:
            self.enchiridion = json.load(f)

        with open("books/letters.json", "r", encoding="utf-8") as f:
            self.letters = json.load(f)

        with open("books/happylife.json", "r", encoding="utf-8") as f:
            self.happylife = json.load(f)

        with open("books/shortness.json", "r", encoding="utf-8") as f:
            self.shortness = json.load(f)

        with open("media.json", "r", encoding="utf-8") as f:
            self.media = json.load(f)

    @commands.command(name='meditations', help="The Meditations by Marcus Aurelius (Farquharson's translation). Example: .mediations 5:23")
    async def meditations(self, ctx, psg_num: str = ""):
        bk, cha = None, None
        try:
            if not psg_num:
                bk = random.choices( list(self.meditations.keys()), weights=[len(v.keys()) for v in self.meditations.values()])[0]
                chapters = list(self.meditations[bk].keys())
                cha = str(random.choice(chapters) )
            else:
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
        
        embed = discord.Embed(title=f"Meditations {bk}:{cha}", url=f"{aurelius['meditations']}/Book_{bk}", description=passage, color=color)
        embed.set_author(name="Marcus Aurelius", url=aurelius["url"], icon_url=aurelius["icon"])
        embed.set_thumbnail(url=aurelius["thumbnail"])        
        await ctx.send(embed=embed)

    @commands.command(name='enchiridion', help="Enchiridion by Epictetus (Oldfather's translation). Example: .enchiridion 34")
    async def enchiridion(self, ctx, chapter: str = ""):
        if not chapter:
            chapter = str(random.randrange(1,54)) # Choose a random chapter of the 53 chapters
        elif not (chapter in self.enchiridion):
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

    @commands.command(name='letters', aliases=["letter"], help="Moral letters to Lucilius by Seneca (Gummere's translation). Example: .letters 99:3-6 gives §3-6 from Letter 99")
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
        
        embed = discord.Embed(title=f"Moral letters to Lucilius: Letter {bk}, §{cha}", url=f"{seneca['letters']}/Letter_{bk}", description=passage, color=color)
        embed.set_author(name="Seneca the Younger", url=seneca["url"], icon_url=seneca["icon"])
        embed.set_thumbnail(url=seneca["thumbnail"])        
        await ctx.send(embed=embed)

    @commands.command(name='happylife', help="Of a Happy Life by Seneca (Stewart's translation). Example: .happylife 12")
    async def happylife(self, ctx, chapter: str):
        if not (chapter in self.happylife):
            return await ctx.send(f"{ctx.author.mention}, there is no chapter `{chapter}` in `Of a Happy Life`.")
            
        passage = self.happylife[chapter]
        seneca = self.media["seneca"]

        color = 0x00FFFF # Red
        to_send = []
        if len(passage) > 4096:
            # If passage is longer than max character limit then split it into two parts by last sentence.
            to_send.extend(passage.rsplit(". ", maxsplit=1))
        else:
            to_send.append(passage)

        roman_num = int2roman(int(chapter))
        embed = discord.Embed(title=f"Of a Happy Life: Book {roman_num}", url=f"{seneca['happylife']}/Book_{roman_num}", description=to_send[0] + ".", color=color)
        embed.set_author(name="Seneca the Younger", url=seneca["url"], icon_url=seneca["icon"])
        #embed.set_thumbnail(url=seneca["thumbnail"])        
        await ctx.send(embed=embed)
        if len(to_send) > 1:
            embed = discord.Embed(description=to_send[1], color=color)
            await ctx.send(embed=embed)

    @commands.command(name='shortness', help="On the shortness of life by Seneca (Basore's translation). Example: .shortness 13")
    async def shortness(self, ctx, chapter: str):
        if not (chapter in self.shortness):
            return await ctx.send(f"{ctx.author.mention}, there is no chapter `{chapter}` in `On the shortness of life`.")
            
        passage = self.shortness[chapter]
        seneca = self.media["seneca"]

        color = 0x00FFFF # Red
        to_send = []
        if len(passage) > 4096:
            # If passage is longer than max character limit then split it into two parts by last sentence.
            to_send.extend(split_within(passage, 4096, ". "))
        else:
            to_send.append(passage)

        roman_num = int2roman(int(chapter))
        embed = discord.Embed(title=f"On the shortness of life: Chapter {roman_num}", url=f"{seneca['shortness']}/Chapter_{roman_num}", description=to_send[0] + ".", color=color)
        embed.set_author(name="Seneca the Younger", url=seneca["url"], icon_url=seneca["icon"])
        #embed.set_thumbnail(url=seneca["thumbnail"])        
        await ctx.send(embed=embed)
        if len(to_send) > 1:
            embed = discord.Embed(description=to_send[1], color=color)
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Librarian(bot))