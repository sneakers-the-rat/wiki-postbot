import discord
from discord import Client, Intents, Embed, Message
from wiki_postbot.creds import Discord_Creds, Mediawiki_Creds
from wiki_postbot.patterns.wikilink import Wikilink
from wiki_postbot.interfaces.mediawiki import Wiki

from discord.ext import commands
from discord import Emoji
import pdb
#
# intents = Intents.default()
# intents.message_content = True
#
# bot = commands.Bot(command_prefix='/', intents=intents)
#
# DEBUG = False
#
# @bot.event
# async def on_message(message:discord.Message):
#     print(message)
#
#     if message.content == 'ping':
#         await message.channel.send('pong')
#
#     if 'good bot' in message.content:
#         await message.add_reaction("❤️‍🔥")
#
#     wl = Wikilink.parse(message.content)
#     if len(wl) > 0:
#         if DEBUG:
#             await message.channel.send(f"Wikilinks detected: \n" + '\n'.join([str(l) for l in wl]))
#         else:
#             await message.add_reaction("⏳")
#
#     await bot.process_commands(message)
#
# @bot.command()

# @bot.command



class DiscordClient(Client):

    def __init__(self, wiki:Wiki, intents=None, debug:bool=False, **kwargs):
        if intents is None:
            intents = Intents.default()
            intents.message_content = True

        self.wiki = wiki
        if self.wiki.sess is None:
            raise RuntimeError("Wiki client is not logged in! Login before passing to discord client")

        self.debug = debug

        super(DiscordClient, self).__init__(intents=intents, **kwargs)


    async def on_ready(self):
        print('Logged on as', self.user)


    async def on_message(self, message:discord.message.Message):
        print(message)
        # don't respond to ourselves
        if message.author == self.user:
            return


        if 'good bot' in message.content:
            await message.add_reaction("❤️‍🔥")

        wl = Wikilink.parse(message.content)
        if len(wl)>0:
            if self.debug:
                await message.channel.send(f"Wikilinks detected: \n" + '\n'.join([str(l) for l in wl]))

            await message.add_reaction("⏳")
            try:
                result = self.wiki.handle_discord(message)
                ok = result.ok
            except:
                # TODO: Log here!
                result = None
                ok = False

            if ok:
                await message.remove_reaction("⏳", self.user)
                await message.add_reaction("✅")
            else:
                await message.remove_reaction("⏳", self.user)
                await message.add_reaction("❌")

            if result and result.reply:
                await message.channel.send(embed=Embed().add_field(name="WikiLinks", value=result.reply))


            # TODO: Logging!

    # def add_links(self, links:Wikilink, msg:discord.message.Message):
    #     if 'testing links' in message.content:
    #         await message.channel.send(embed=Embed().add_field(name="Links", value="there are [links](https://example.com)"))
    #         #await message.edit(content=message.content, embed=Embed().add_field(name="Links", value="There are [links](https://example.com) in here"))
    #         #await message.channel.send("Bot is testing if it can [make links](https://example.com)")



    async def debug(ctx: discord.ext.commands.Context, arg):
        print('debug command')
        global DEBUG
        if arg == "on":
            DEBUG = True
            await ctx.message.add_reaction("🧪")
        elif arg == "off":
            DEBUG = False
            await ctx.message.add_reaction("🤐")
        else:
            await ctx.message.reply("usage: /debug off or /debug on")


if __name__ == "__main__":
    discord_creds = Discord_Creds.from_json('discord_creds.json')
    wiki_creds = Mediawiki_Creds.from_json('mediawiki_creds.json')
    wiki = Wiki(url="https://cscw.sciop.net")
    wiki.login(wiki_creds)

    client = DiscordClient(wiki=wiki)
    client.run(discord_creds.token)


    # bot.run(creds.token)
