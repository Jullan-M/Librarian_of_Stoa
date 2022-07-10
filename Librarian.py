import asyncio
from tkinter import E
import discord
import json
import random
import re
from discord.ext import commands
from utilities import int2roman, split_within, uniform_random_choice_from_dict

MAX_EMBED_LENGTH = 4096
MULTIPAGE_TIMEOUT = 900 # Timeout period for page flipping with reacts

class Librarian(commands.Cog, name='Librarian'):
    """"Sends quotes and transcripts of public domain texts"""
    def __init__(self, bot):
        self.bot = bot
        self.multipage_timeout = MULTIPAGE_TIMEOUT

        def load_json(filename: str):
            with open(filename, "r", encoding="utf-8") as f:
                js = json.load(f)
            return js

        self.meditations = load_json("books/meditations.json")
        self.enchiridion = load_json("books/enchiridion.json")
        self.letters = load_json("books/letters.json")
        self.happylife = load_json("books/happylife.json")
        self.shortness = load_json("books/shortness.json")
        self.discourses= load_json("books/discourses.json")
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
        
        await message.add_reaction("◀️")
        await message.add_reaction("▶️")

        valid_emoji = ["◀️", "▶️", "🗑️"]
        def check(reaction, user):
            # Make sure nobody except the command sender can interact with the "menu"
            # The user can't flip pages in multiple messages at once either
            nonlocal message
            return user == ctx.author and reaction.message.id==message.id and str(reaction.emoji) in valid_emoji
            

        while True:
            try:
                # wait for a reaction to be added
                # times out after MULTIPAGE_TIMEOUT seconds
                reaction, user = await self.bot.wait_for("reaction_add", timeout=self.multipage_timeout, check=check)
                
                if str(reaction.emoji) == "▶️" and cur_page != pages-1:
                    cur_page += 1
                    await message.edit(embed=embeds[cur_page])
                    await message.remove_reaction(reaction, user)

                elif str(reaction.emoji) == "◀️" and cur_page > 0:
                    cur_page -= 1
                    await message.edit(embed=embeds[cur_page])
                    await message.remove_reaction(reaction, user)
                elif str(reaction.emoji) == "🗑️":
                    # Bot messages can be deleted by reacting with the waste basket emoji
                    await message.delete()
                    break
                else:
                    # remove reactions if the user tries to go forward on the last page or
                    # backwards on the first page
                    await message.remove_reaction(reaction, user)
            except (asyncio.TimeoutError, discord.errors.Forbidden):
                # end the loop if user doesn't react after MULTIPAGE_TIMEOUT seconds
                for r in valid_emoji: await message.remove_reaction(r, self.bot.user)
                await message.clear_reactions()
                break

    async def deletables(self, ctx, embeds):
        # Makes messages deletable by reacting wastebasket on them
        # Check mark reacts make reactions go away (but one may still delete them!)
        messages = []
        for e in embeds:
            messages.append(await ctx.send(embed=e)) 
        last_message = messages[-1]

        await last_message.add_reaction("✅")
        await last_message.add_reaction("🗑️")

        valid_emoji = ["✅", "🗑️"]
        def check(reaction, user):
            # Make sure nobody except the command sender can interact with the "menu"
            # The user can't flip pages in multiple messages at once either
            nonlocal last_message
            return user == ctx.author and reaction.message.id==last_message.id and str(reaction.emoji) in valid_emoji

        while True:
            try:
                # wait for a reaction to be added
                # times out after MULTIPAGE_TIMEOUT seconds
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)
                
                if str(reaction.emoji) == "✅":
                    await last_message.clear_reactions()
                elif str(reaction.emoji) == "🗑️":
                    for m in messages: await m.delete()
                    break
                else:
                    # remove reactions if the user tries to go forward on the last page or
                    # backwards on the first page
                    await last_message.remove_reaction(reaction, user)
            except (asyncio.TimeoutError, discord.errors.Forbidden):
                # end the loop if user doesn't react after MULTIPAGE_TIMEOUT seconds
                for r in valid_emoji: await last_message.remove_reaction(r, self.bot.user)
                await last_message.clear_reactions()
                break

    @commands.command(name='meditations', help=f"[*The Meditations*](https://en.wikisource.org/wiki/The_Meditations_of_the_Emperor_Marcus_Antoninus) \
        by Marcus Aurelius (Farquharson's translation). Example: .mediations 5:23")
    async def meditations(self, ctx, psg_num: str = ""):
        bk, cha = None, None
        try:
            if not psg_num:
                bk, cha = uniform_random_choice_from_dict(self.meditations)
            else:
                bk, cha = re.split("[:\.]", psg_num, maxsplit=1)
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
        
        embeds = []     
        embeds.append(embed)
        if len(to_send) > 1:
            # Mediations doesn't have any passages over 2 embeds long
            embeds.append(discord.Embed(description=to_send[1], color=color))
        await self.deletables(ctx, embeds)

    @commands.command(name='enchiridion', help="[*Enchiridion*](https://en.wikisource.org/wiki/Epictetus,_the_Discourses_as_reported_by_Arrian,_the_Manual,_and_Fragments/Manual) \
        by Epictetus (Oldfather's translation). Example: .enchiridion 34")
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
        
        embeds = []     
        embeds.append(embed)
        if len(to_send) > 1:
            # Enchiridion doesn't have any passages over 2 embeds long
            embeds.append(discord.Embed(description=to_send[1], color=color))
        await self.deletables(ctx, embeds)

    @commands.command(name='letters', aliases=["letter"], help="[*Moral letters to Lucilius*](https://en.wikisource.org/wiki/Moral_letters_to_Lucilius) \
         by Seneca (Gummere's translation). Example: .letters 99:3-6 gives §3-6 from Letter 99")
    async def letters(self, ctx, psg_num: str = "", post_all: str = ""):
        bk, cha = None, None
        if any([s in psg_num for s in [":", "."]]):
            bk, cha = re.split("[:\.]", psg_num, maxsplit=1)
        else:
            bk = psg_num
        
        if not bk:
            bk = str(random.randrange(1,125)) # Choose a random letter of the 124 letters
        elif not (bk in self.letters):
            return await ctx.send(f"{ctx.author.mention}, there is no letter `{bk}` of the Moral letters.")
        
        passage = None
        seneca = self.media["seneca"]
        if cha:
            if "-" in cha:
                cha1, cha2 = cha.split("-", maxsplit=1)
                if not 0 < int(cha1) < int(cha2) or not (cha1 in self.letters[bk] and cha2 in self.letters[bk]):
                    return await ctx.send(f"{ctx.author.mention}, `{cha1}-{cha2}` is not a valid range.")
                passage = " ".join([self.letters[bk][str(ch)] for ch in range(int(cha1), int(cha2) + 1)]).rstrip()
            else:
                if not (int(cha) > 0 and cha in self.letters[bk]):
                    return await ctx.send(f"{ctx.author.mention}, there is no paragraph `{cha}` in letter `{bk}` of the Moral letters.")
                passage = self.letters[bk][cha].rstrip()
        else:
            letter_passages = list(self.letters[bk].values())[1:]
            passage = "".join(letter_passages)
        title = f"Moral letters to Lucilius: Letter {bk}"
        
        if cha:
            title += f", §{cha}"
        else:
            title += f"\n{self.letters[bk]['0']}"

        passage_url = f"{seneca['letters']}/Letter_{bk}"
        color = 0x0000FF # Red
        if len(passage) > MAX_EMBED_LENGTH and not cha:
            to_send = split_within(passage, MAX_EMBED_LENGTH, "\n", keep_delim=True)
            
            # Post every embed if "all" parameter is passed, else do flippable embed pages
            if post_all == "all":
                embeds = [self.generate_embed(title, to_send[0], seneca, passage_url, color)]
                for t in to_send[1:]:
                    embeds.append(discord.Embed(description=t, color=color))
                await self.deletables(ctx, embeds)
            else:
                embeds = [self.generate_embed(title, t, seneca, passage_url, color) for t in to_send]
                await self.multi_page(ctx, embeds)
            return
        
        embed = self.generate_embed(title, passage, seneca, passage_url, color)
        embed.set_thumbnail(url=seneca["thumbnail"])
        embeds = [embed]     
        await self.deletables(ctx, embeds)

    @commands.command(name='happylife', help="[*Of a Happy Life*](https://en.wikisource.org/wiki/Of_a_Happy_Life) \
        by Seneca (Stewart's translation). Example: .happylife 12")
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

        embeds = []     
        embeds.append(embed)
        if len(to_send) > 1:
            # Happy Life doesn't have any passages over 2 embeds long
            embeds.append(discord.Embed(description=to_send[1], color=color))
        await self.deletables(ctx, embeds)

    @commands.command(name='shortness', help="[*On the shortness of life*](https://en.wikisource.org/wiki/On_the_shortness_of_life) \
        by Seneca (Basore's translation). Example: .shortness 13")
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
        
        embeds = []     
        embeds.append(embed)
        if len(to_send) > 1:
            # Enchiridion doesn't have any passages over 2 embeds long
            embeds.append(discord.Embed(description=to_send[1], color=color))
        await self.deletables(ctx, embeds)

    @commands.command(name='discourses', help="[*The Discourses*](https://en.wikisource.org/wiki/Epictetus,_the_Discourses_as_reported_by_Arrian,_the_Manual,_and_Fragments) \
        by Epictetus (Oldfather's translation). Example: .discourses 1:21")
    async def discourses(self, ctx, psg_num: str = ""):
        bk, cha = None, None
        try:
            if not psg_num:
                bk, cha = uniform_random_choice_from_dict(self.discourses)
            else:
                bk, cha = re.split("[:\.]", psg_num, maxsplit=1)
        except ValueError:
            return await ctx.send(f"{ctx.author.mention}, invalid formatting. The correct syntax is `<BOOK>:<CHAPTER>`, e.g., `1:21` for Book 1, Chapter 21.")
            
        if not (bk in self.discourses):
            return await ctx.send(f"{ctx.author.mention}, there is no Book `{bk}` in The Discourses (or it may have been lost to time 😢).")
            
        if not (cha in self.discourses[bk]):
            return await ctx.send(f"{ctx.author.mention}, there is no chapter `{cha}` in Book `{bk}` of The Discourses.")
        
        title, passage = self.discourses[bk][cha].split("\n", maxsplit=1)
        title = f"The Discourses – Book {int2roman(int(bk))}, Chapter {cha}\n{title}"
        passage = passage.lstrip()
        epictetus = self.media["epictetus"] # author data
        passage_url = f"{epictetus['discourses']}/Book_{bk}/Chapter_{cha}"
        color = 0x00FF00 # Green

        if len(passage) > MAX_EMBED_LENGTH:
            to_send = split_within(passage, MAX_EMBED_LENGTH, "\n", keep_delim=True)
            embeds = [self.generate_embed(title, t, epictetus, passage_url, color) for t in to_send]
            await self.multi_page(ctx, embeds)
            return
        
        embed = self.generate_embed(title, passage, epictetus, passage_url, color)
        embed.set_thumbnail(url=epictetus["thumbnail"])        
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Librarian(bot))
    print("Librarian cog up and ready!")