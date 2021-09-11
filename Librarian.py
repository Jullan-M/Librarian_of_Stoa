import asyncio
import discord
import json
import random
from discord.ext import commands
from utilities import int2roman, split_within

MAX_EMBED_LENGTH = 4096
MULTIPAGE_TIMEOUT = 600

class Librarian(commands.Cog, name='Librarian'):
    def __init__(self, bot):
        self.bot = bot

        def load_json(filename: str):
            with open(filename, "r", encoding="utf-8") as f:
                js = json.load(f)
            return js

        self.meditations = load_json("books/meditations.json")
        self.enchiridion = load_json("books/enchiridion.json")
        self.letters = load_json("books/letters.json")
        self.happylife = load_json("books/happylife.json")
        self.shortness = load_json("books/shortness.json")
        self.media = load_json("media.json")

    @staticmethod
    def generate_embed(title, passage, author_data, passage_url, color):
        embed = discord.Embed(title=title, description=passage, url=passage_url, color=color)
        embed.set_author(name=author_data["name"], url=author_data["url"], icon_url=author_data["icon"])
        # embed.set_thumbnail(url=author_data["thumbnail"])   
        return embed

    async def multi_page(self, ctx, embeds):
        pages = len(embeds)
        cur_page = 0
        for i, em in enumerate(embeds):
            pg = i + 1
            em.set_footer(text=f"Page {pg} of {pages}")

        message = await ctx.send(embed=embeds[0])
        # getting the message object for editing and reacting

        await message.add_reaction("◀️")
        await message.add_reaction("▶️")

        def check(reaction, user):
            nonlocal message
            return user == ctx.author and reaction.message.id==message.id and str(reaction.emoji) in ["◀️", "▶️"]
            # This makes sure nobody except the command sender can interact with the "menu"
            # The user can't flip pages in multiple messages at once

        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=MULTIPAGE_TIMEOUT, check=check)
                # waiting for a reaction to be added - times out after x seconds, 60 in this
                # example

                if str(reaction.emoji) == "▶️" and cur_page != pages-1:
                    cur_page += 1
                    await message.edit(embed=embeds[cur_page])
                    await message.remove_reaction(reaction, user)

                elif str(reaction.emoji) == "◀️" and cur_page > 0:
                    cur_page -= 1
                    await message.edit(embed=embeds[cur_page])
                    await message.remove_reaction(reaction, user)
                else:
                    await message.remove_reaction(reaction, user)
                    # removes reactions if the user tries to go forward on the last page or
                    # backwards on the first page
            except asyncio.TimeoutError:
                await message.clear_reactions()
                break
                # ending the loop if user doesn't react after x seconds

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
        
        title = f"Meditations {bk}:{cha}"
        passage = self.meditations[bk][cha].rstrip()
        aurelius = self.media["aurelius"] # author data
        passage_url = f"{aurelius['meditations']}/Book_{bk}"
        color = 0xFF0000 # Red

        to_send = split_within(passage, MAX_EMBED_LENGTH, "\n", keep_delim=True)
        
        embed = self.generate_embed(title, to_send[0], aurelius, passage_url, color)
        embed.set_thumbnail(url=aurelius["thumbnail"])        
        await ctx.send(embed=embed)
        if len(to_send) > 1:
            # Mediations doesn't have any passages over 2 embeds long
            embed = discord.Embed(description=to_send[1], color=color)
            await ctx.send(embed=embed)

    @commands.command(name='enchiridion', help="Enchiridion by Epictetus (Oldfather's translation). Example: .enchiridion 34")
    async def enchiridion(self, ctx, chapter: str = ""):
        if not chapter:
            chapter = str(random.randrange(1,54)) # Choose a random chapter of the 53 chapters
        elif not (chapter in self.enchiridion):
            return await ctx.send(f"{ctx.author.mention}, there is no chapter `{chapter}` in The Enchiridion.")
        
        title = f"Enchiridion {chapter}"
        passage = self.enchiridion[chapter].rstrip()
        epictetus = self.media["epictetus"]
        passage_url = epictetus["enchiridion"]
        color = 0x00FF00 # Green

        to_send = split_within(passage, MAX_EMBED_LENGTH, "\n", keep_delim=True)
        
        embed = self.generate_embed(title, to_send[0], epictetus, passage_url, color)
        embed.set_thumbnail(url=epictetus["thumbnail"])        
        await ctx.send(embed=embed)
        if len(to_send) > 1:
            # Enchiridion doesn't have any passages over 2 embeds long
            embed = discord.Embed(description=to_send[1], color=color)
            await ctx.send(embed=embed)

    @commands.command(name='letters', aliases=["letter"], help="Moral letters to Lucilius by Seneca (Gummere's translation). Example: .letters 99:3-6 gives §3-6 from Letter 99")
    async def letters(self, ctx, psg_num: str):
        bk, cha = None, None
        if ":" in psg_num:
            bk, cha = psg_num.split(":", maxsplit=1)
        else:
            bk = psg_num

        if not (bk in self.letters):
            return await ctx.send(f"{ctx.author.mention}, there is no letter `{bk}` of the Moral letters.")
            
        passage = None
        seneca = self.media["seneca"]
        if cha:
            if "-" in cha:
                cha1, cha2 = cha.split("-", maxsplit=1)
                if int(cha2) <= int(cha1) or not (cha1 in self.letters[bk] and cha2 in self.letters[bk]):
                    return await ctx.send(f"{ctx.author.mention}, `{cha1}-{cha2}` is not a valid range.")
                passage = " ".join([self.letters[bk][str(ch)] for ch in range(int(cha1), int(cha2) + 1)]).rstrip()
            else:
                if not (cha in self.letters[bk]):
                    return await ctx.send(f"{ctx.author.mention}, there is no paragraph `{cha}` in letter `{bk}` of the Moral letters.")
                passage = self.letters[bk][cha].rstrip()
        else:
            passage = "\n".join(self.letters[bk].values())
        title = f"Moral letters to Lucilius: Letter {bk}"
        if cha:
            title += f", §{cha}"
        passage_url = f"{seneca['letters']}/Letter_{bk}"
        color = 0x0000FF # Red
        if len(passage) > MAX_EMBED_LENGTH and not cha:
            to_send = split_within(passage, MAX_EMBED_LENGTH, "\n", keep_delim=True)
            embeds = [self.generate_embed(title, t, seneca, passage_url, color) for t in to_send]
            await self.multi_page(ctx, embeds)
            return
        
        embed = self.generate_embed(title, passage, seneca, passage_url, color)
        embed.set_thumbnail(url=seneca["thumbnail"])        
        await ctx.send(embed=embed)

    @commands.command(name='happylife', help="Of a Happy Life by Seneca (Stewart's translation). Example: .happylife 12")
    async def happylife(self, ctx, chapter: str):
        if not (chapter in self.happylife):
            return await ctx.send(f"{ctx.author.mention}, there is no chapter `{chapter}` in `Of a Happy Life`.")
        
        roman_num = int2roman(int(chapter))
        title = f"Of a Happy Life: Book {roman_num}"
        passage = self.happylife[chapter]
        seneca = self.media["seneca"]
        passage_url = f"{seneca['happylife']}/Book_{roman_num}"
        
        color = 0x00FFFF # Red
        to_send = split_within(passage, MAX_EMBED_LENGTH, ". ", keep_delim=True)

        embed = self.generate_embed(title, to_send[0], seneca, passage_url, color)
        await ctx.send(embed=embed)
        if len(to_send) > 1:
            # Of a Happy Life doesn't have any passages over 2 embeds long
            embed = discord.Embed(description=to_send[1], color=color)
            await ctx.send(embed=embed)

    @commands.command(name='shortness', help="On the shortness of life by Seneca (Basore's translation). Example: .shortness 13")
    async def shortness(self, ctx, chapter: str):
        if not (chapter in self.shortness):
            return await ctx.send(f"{ctx.author.mention}, there is no chapter `{chapter}` in `On the shortness of life`.")
        
        roman_num = int2roman(int(chapter))
        title = f"On the shortness of life: Chapter {roman_num}"
        passage = self.shortness[chapter]
        seneca = self.media["seneca"]
        passage_url = f"{seneca['shortness']}/Chapter_{roman_num}"

        color = 0x00FFFF # Red
        to_send = split_within(passage, MAX_EMBED_LENGTH, ". ", keep_delim=True)

        embed = self.generate_embed(title, to_send[0], seneca, passage_url, color)
        await ctx.send(embed=embed)
        if len(to_send) > 1:
            # On the shortness of life doesn't have any passages over 2 embeds long
            embed = discord.Embed(description=to_send[1], color=color)
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Librarian(bot))