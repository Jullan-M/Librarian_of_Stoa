import asyncio
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

        self.med = load_json("books/meditations.json") # Meditations
        self.ench = load_json("books/enchiridion.json") # Enchiridion
        self.let = load_json("books/letters.json") # Letters
        self.hap = load_json("books/happylife.json") # Happy Life
        self.short = load_json("books/shortness.json") # Shortness of life
        self.disc = load_json("books/discourses.json") # The Discourses
        self.ang = load_json("books/anger.json") # Of Anger
        self.media = load_json("books/media.json")
        self.toc = load_json("books/toc.json")

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
                
                if str(reaction.emoji) == "▶️":
                    # Next page
                    if cur_page == pages - 1: # If current page is the last page, wrap around to the first page
                        cur_page = 0
                    else: # Else just flip to the next
                        cur_page += 1
                    await message.edit(embed=embeds[cur_page])
                    await message.remove_reaction(reaction, user)

                elif str(reaction.emoji) == "◀️":
                    # Previous page
                    if cur_page == 0: # If current page is the first page, wrap around to the last page
                        cur_page = pages - 1
                    else: # Else just flip back to the previous
                        cur_page -= 1
                    await message.edit(embed=embeds[cur_page])
                    await message.remove_reaction(reaction, user)
                
                elif str(reaction.emoji) == "🗑️":
                    # Bot messages can be deleted by reacting with the waste basket emoji
                    await message.delete()
                    break
                
            except (asyncio.TimeoutError, discord.errors.Forbidden):
                # End the loop if user doesn't react after MULTIPAGE_TIMEOUT seconds
                for r in valid_emoji:
                    # Remove bot's reactions first in case there are missing perms
                    await message.remove_reaction(r, self.bot.user)
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

    @commands.command(name='meditations', help=f"[*The Meditations*](https://en.wikisource.org/wiki/The_Meditations_of_the_Emperor_Marcus_Antoninus) by Marcus Aurelius (Farquharson's translation). Example: .mediations 5:23")
    async def meditations(self, ctx, bk_ch: str = ""):
        bk, cha = None, None
        try:
            if not bk_ch:
                bk, cha = uniform_random_choice_from_dict(self.med)
            else:
                bk, cha = re.split("[:\.]", bk_ch, maxsplit=1)
        except ValueError:
            return await ctx.send(f"{ctx.author.mention}, invalid formatting. The correct syntax is `<BOOK>:<CHAPTER>`, e.g., `5:23` for Book 5, Chapter 23.")
            
        if not (bk in self.med):
            return await ctx.send(f"{ctx.author.mention}, there is no Book `{bk}` of Meditations.")
            
        if not (cha in self.med[bk]):
            return await ctx.send(f"{ctx.author.mention}, there is no chapter `{cha}` in Book `{bk}` of Meditations.")
        
        title = f"Meditations {bk}:{cha}"
        passage = self.med[bk][cha].rstrip()
        aurelius = self.media["aurelius"] # author data
        passage_url = f"{aurelius['meditations']}/Book_{bk}"
        color = 0xFF0000 # Red

        to_send = split_within(passage, MAX_EMBED_LENGTH, ["\n", ". "], keep_delim=True)
        
        embed = self.generate_embed(title, to_send[0], aurelius, passage_url, color)
        embed.set_thumbnail(url=aurelius["thumbnail"])        
        
        embeds = []     
        embeds.append(embed)
        if len(to_send) > 1:
            # Mediations doesn't have any passages over 2 embeds long
            embeds.append(discord.Embed(description=to_send[1], color=color))
        await self.deletables(ctx, embeds)

    @commands.command(name='enchiridion', help="[*Enchiridion*](https://en.wikisource.org/wiki/Epictetus,_the_Discourses_as_reported_by_Arrian,_the_Manual,_and_Fragments/Manual) by Epictetus (Oldfather's translation). Example: .enchiridion 34")
    async def enchiridion(self, ctx, chapter: str = ""):
        if not chapter:
            chapter = str(random.randrange(1,54)) # Choose a random chapter of the 53 chapters
        elif not (chapter in self.ench):
            return await ctx.send(f"{ctx.author.mention}, there is no chapter `{chapter}` in The Enchiridion.")
        
        title = f"Enchiridion {chapter}"
        passage = self.ench[chapter].rstrip()
        epictetus = self.media["epictetus"]
        passage_url = epictetus["enchiridion"]
        color = 0x00FF00 # Green

        to_send = split_within(passage, MAX_EMBED_LENGTH, ["\n", ". "], keep_delim=True)
        
        embed = self.generate_embed(title, to_send[0], epictetus, passage_url, color)
        embed.set_thumbnail(url=epictetus["thumbnail"])
        
        embeds = []     
        embeds.append(embed)
        if len(to_send) > 1:
            # Enchiridion doesn't have any passages over 2 embeds long
            embeds.append(discord.Embed(description=to_send[1], color=color))
        await self.deletables(ctx, embeds)

    @commands.command(name='letters', aliases=["letter"], help="[*Moral letters to Lucilius*](https://en.wikisource.org/wiki/Moral_letters_to_Lucilius) by Seneca (Gummere's translation). Example: `.letters 99:3-6` gives §3-6 from Letter 99. `.letters 19 all` spews out all pages of letter 19 at once.")
    async def letters(self, ctx, bk_ch: str = "", post_all: str = ""):
        bk, cha = None, None
        if any([s in bk_ch for s in [":", "."]]):
            bk, cha = re.split("[:\.]", bk_ch, maxsplit=1)
        elif bk_ch == "toc": # Shows table of contents
            return await self.table_of_contents(ctx, "letters")
        else:
            bk = bk_ch
        
        if not bk:
            bk = str(random.randrange(1,125)) # Choose a random letter of the 124 letters
        elif not (bk in self.let):
            return await ctx.send(f"{ctx.author.mention}, there is no letter `{bk}` of the Moral letters.")
        
        passage = None
        seneca = self.media["seneca"]
        if cha:
            if "-" in cha:
                cha1, cha2 = cha.split("-", maxsplit=1)
                if not 0 < int(cha1) < int(cha2) or not (cha1 in self.let[bk] and cha2 in self.let[bk]):
                    return await ctx.send(f"{ctx.author.mention}, `{cha1}-{cha2}` is not a valid range.")
                passage = " ".join([self.let[bk][str(ch)] for ch in range(int(cha1), int(cha2) + 1)]).rstrip()
            else:
                if not (int(cha) > 0 and cha in self.let[bk]):
                    return await ctx.send(f"{ctx.author.mention}, there is no paragraph `{cha}` in letter `{bk}` of the Moral letters.")
                passage = self.let[bk][cha].rstrip()
        else:
            letter_passages = list(self.let[bk].values())[1:]
            passage = "".join(letter_passages)
        title = f"Moral letters to Lucilius: Letter {bk}"
        
        if cha:
            title += f", §{cha}"
        else:
            title += f"\n{self.let[bk]['0']}"

        passage_url = f"{seneca['letters']}/Letter_{bk}"
        color = 0x0000FF # Red
        if len(passage) > MAX_EMBED_LENGTH and not cha:
            to_send = split_within(passage, MAX_EMBED_LENGTH, ["\n", ". "], keep_delim=True)
            
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

    @commands.command(name='happylife', help="[*Of a Happy Life*](https://en.wikisource.org/wiki/Of_a_Happy_Life) by Seneca (Stewart's translation). Example: .happylife 12")
    async def happylife(self, ctx, chapter: str = ""):
        if not chapter:
            chapter = str(random.randrange(1,29)) # Choose a random chapter of the 28 chapters
        elif not (chapter in self.hap):
            return await ctx.send(f"{ctx.author.mention}, there is no chapter `{chapter}` in `Of a Happy Life`.")
        
        roman_num = int2roman(int(chapter))
        title = f"Of a Happy Life: Book {roman_num}"
        passage = self.hap[chapter]
        seneca = self.media["seneca"]
        passage_url = f"{seneca['happylife']}/Book_{roman_num}"
        
        color = 0x00FFFF # Red
        to_send = split_within(passage, MAX_EMBED_LENGTH, [". "], keep_delim=True)

        embed = self.generate_embed(title, to_send[0], seneca, passage_url, color)

        embeds = []     
        embeds.append(embed)
        if len(to_send) > 1:
            # Happy Life doesn't have any passages over 2 embeds long
            embeds.append(discord.Embed(description=to_send[1], color=color))
        await self.deletables(ctx, embeds)

    @commands.command(name='shortness', help="[*On the shortness of life*](https://en.wikisource.org/wiki/On_the_shortness_of_life) \
        by Seneca (Basore's translation). Example: .shortness 13")
    async def shortness(self, ctx, chapter: str = ""):
        if not chapter:
            chapter = str(random.randrange(1,21)) # Choose a random chapter of the 21 chapters
        elif not (chapter in self.short):
            return await ctx.send(f"{ctx.author.mention}, there is no chapter `{chapter}` in `On the shortness of life`.")
        
        roman_num = int2roman(int(chapter))
        title = f"On the shortness of life: Chapter {roman_num}"
        passage = self.short[chapter]
        seneca = self.media["seneca"]
        passage_url = f"{seneca['shortness']}/Chapter_{roman_num}"

        color = 0x00FFFF # Red
        to_send = split_within(passage, MAX_EMBED_LENGTH, [". "], keep_delim=True)

        embed = self.generate_embed(title, to_send[0], seneca, passage_url, color)
        
        embeds = []     
        embeds.append(embed)
        if len(to_send) > 1:
            # Shortness of life doesn't have any passages over 2 embeds long
            embeds.append(discord.Embed(description=to_send[1], color=color))
        await self.deletables(ctx, embeds)

    @commands.command(name='discourses', help="[*The Discourses*](https://en.wikisource.org/wiki/Epictetus,_the_Discourses_as_reported_by_Arrian,_the_Manual,_and_Fragments) by Epictetus (Oldfather's translation). Example: .discourses 1:21")
    async def discourses(self, ctx, bk_ch: str = ""):
        bk, cha = None, None
        try:
            if not bk_ch:
                bk, cha = uniform_random_choice_from_dict(self.disc)
            elif bk_ch == "toc": # Shows table of contents
                return await self.table_of_contents(ctx, "discourses")
            else:
                bk, cha = re.split("[:\.]", bk_ch, maxsplit=1)
        except ValueError:
            return await ctx.send(f"{ctx.author.mention}, invalid formatting. The correct syntax is `<BOOK>:<CHAPTER>`, e.g., `1:21` for Book 1, Chapter 21.")
            
        if not (bk in self.disc):
            return await ctx.send(f"{ctx.author.mention}, there is no Book `{bk}` in *The Discourses* (or it may have been lost to time 😢).")
            
        if not (cha in self.disc[bk]):
            return await ctx.send(f"{ctx.author.mention}, there is no chapter `{cha}` in Book `{bk}` of *The Discourses*.")
        
        title, passage = self.disc[bk][cha].split("\n", maxsplit=1)
        title = f"The Discourses – Book {int2roman(int(bk))}, Chapter {cha}\n{title}"
        passage = passage.lstrip()
        epictetus = self.media["epictetus"] # author data
        passage_url = f"{epictetus['discourses']}/Book_{bk}/Chapter_{cha}"
        color = 0x00FF00 # Green

        if len(passage) > MAX_EMBED_LENGTH:
            to_send = split_within(passage, MAX_EMBED_LENGTH, ["\n", ". "], keep_delim=True)
            embeds = [self.generate_embed(title, t, epictetus, passage_url, color) for t in to_send]
            await self.multi_page(ctx, embeds)
            return
        
        embed = self.generate_embed(title, passage, epictetus, passage_url, color)
        embed.set_thumbnail(url=epictetus["thumbnail"])        
        await self.deletables(ctx, [embed])

    @commands.command(name='anger', aliases=["ofanger", "onanger"], help="[*Of Anger*](https://en.wikisource.org/wiki/Of_Anger) by Seneca (Stewart's translation). Example: .anger 2:10")
    async def anger(self, ctx, bk_ch: str = ""):
        bk, cha = None, None
        try:
            if not bk_ch:
                bk, cha = uniform_random_choice_from_dict(self.disc)
            else:
                bk, cha = re.split("[:\.]", bk_ch, maxsplit=1)
        except ValueError:
            return await ctx.send(f"{ctx.author.mention}, invalid formatting. The correct syntax is `<BOOK>:<CHAPTER>`, e.g., `1:21` for Book 1, Chapter 21.")
            
        if not (bk in self.disc):
            return await ctx.send(f"{ctx.author.mention}, there is no Book `{bk}` in *Of Anger*.")
            
        if not (cha in self.disc[bk]):
            return await ctx.send(f"{ctx.author.mention}, there is no chapter `{cha}` in Book `{bk}` in *Of Anger*.")

        roman_num = int2roman(int(bk))
        title = f"Of Anger: Book {roman_num} Chapter {cha}"
        passage = self.ang[bk][cha]
        seneca = self.media["seneca"]
        passage_url = f"{seneca['anger']}/Book_{roman_num}#{int2roman(int(cha))}."

        color = 0x00FFFF
        to_send = split_within(passage, MAX_EMBED_LENGTH, ["\n", ". "], keep_delim=True)

        embed = self.generate_embed(title, to_send[0], seneca, passage_url, color)
        
        embeds = []     
        embeds.append(embed)
        if len(to_send) > 1:
            # Of Anger doesn't have any passages over 2 embeds long
            embeds.append(discord.Embed(description=to_send[1], color=color))
        await self.deletables(ctx, embeds)
        

    @commands.command(name='random', help="Posts a random passage or chapter from any of the available books.")
    async def random(self, ctx):
        # Put every function in the library in to a list
        functions = [self.enchiridion, self.discourses, self.meditations, self.shortness, self.happylife, self.letters, self.anger]
        func = random.choice(functions)
        print(f"Choosing a random chapter/passage from {func.name}")
        await func(ctx)

    @commands.command(name='toc', aliases=["tableofcontents"], help="Shows table of contents (if any) of a given book. Example: .toc letters")
    async def table_of_contents(self, ctx, title: str):
        try:
            book_data = self.toc[title]
        except KeyError:
            await ctx.send(f"No table of contents was found for `{title}`")
            return
        author = book_data["author"]
        author_media = self.media[author]
        color = discord.Color.orange()
        heading = f"Table of Contents - {book_data['name']}"
        description = book_data["description"]

        embeds = []
        for vol, chaps in book_data["contents"].items():
            chapters = '\n'.join(chaps)
            toc_text = f"\n\n__**{vol}**__\n{chapters}"
            embed = discord.Embed(title = heading, description = description + toc_text, color = color, url = author_media[title])
            embeds.append(embed)
        await self.multi_page(ctx, embeds)
        

def setup(bot):
    bot.add_cog(Librarian(bot))
    print("Librarian cog up and ready!")