import discord
from discord.ext import commands

class Help(commands.Cog):
    """ Sends this help message """

    def __init__(self, bot):
        self.bot = bot
        self.cmds = {}
        for cmd in self.bot.walk_commands():
            self.cmds[cmd.name] = cmd
        self.prefix = self.bot.command_prefix

    @commands.command(name="help", help="Displays help about Librarian of Stoa commands and functions.")
    async def help(self, ctx, *input):
        """Shows all commands of the bot"""

        owner_name = "Jullan#5868"

        title = "Help Message"
        description = f"""
        Librarian of Stoa is a bot that finds and quotes passages of some classical era philosophers, in particular the Stoics. The bot then sends them in a beautiful embedded format on Discord. Take a look below for the list of public domain books that are currently supported.
        """

        about = f"""
        The bot is developed and maintained by {owner_name}, and is based on py-cord. If you have any suggestions you can always @ me on servers the bot is in.\nSource code can be found on [GitHub](https://github.com/Jullan-M/Librarian_of_Stoa).\nIf you're feeling generous you can donate to me on [PayPal](https://www.paypal.com/donate/?hosted_button_id=GE7JNW89XDQJN). Never necessary, but always appreciated.
        """

        if not input:
            # Starting to build embed
            emb = discord.Embed(title=title, color=discord.Color.blue(), description=description)
            
            emb.add_field(name="List of Commands", value=f"Use `{self.prefix}help <module/command>` to see information about a particular module/command. Using a command without giving it a number will send a random passage or chapter from that book.")
            # List all unhidden commands
            for cmd_name, cmd in self.cmds.items():
                if not cmd.hidden:
                    value = f"{cmd.help}"
                    # If command has aliases, add those in a new line
                    if cmd.aliases:
                        value = value + "\nAliases: " + ', '.join([f"`{a}`" for a in cmd.aliases])
                    emb.add_field(name=f"`{self.prefix}{cmd_name} {' '.join('<' + a[0] + '>' for a in cmd.clean_params.items())}`", value=value, inline=False)                

            # setting information about author
            emb.add_field(name="About & Support", value=about)
            emb.set_footer(text=f"Developed by {owner_name}")

        # Block called when one command-name is given
        # trying to find matching cog and it's commands
        elif len(input) == 1:
            
            # Iterating trough cogs
            if input[0] in self.cmds.keys():
                cmd = self.cmds[input[0]]
                title = f"`{self.prefix}{cmd.name} {' '.join('<' + a[0] + '>' for a in cmd.clean_params.items())}`"
                description = f"{cmd.help}"
                emb = discord.Embed(title=title, description=description, color=discord.Color.green())
                if cmd.aliases:
                    aliases = "\nAliases: " + ', '.join(cmd.aliases)
                    emb.set_footer(text=aliases)

            # If input not found
            # yes, for-loops have an else statement, it's called when no 'break' was issued
            else:
                emb = discord.Embed(title="What's that?!",
                                    description=f"I've never heard from a module called `{input[0]}` before.",
                                    color=discord.Color.orange())

        # Sending reply embed using our own function defined above
        await ctx.send(embed=emb)


def setup(bot):
    bot.add_cog(Help(bot))