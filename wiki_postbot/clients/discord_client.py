from pathlib import Path
from typing import List, Optional
import argparse

import discord
from discord import Client, Intents, Embed, Message
from wiki_postbot.creds import Discord_Creds, Mediawiki_Creds
from wiki_postbot.patterns.wikilink import Wikilink
from wiki_postbot.interfaces.mediawiki import Wiki
from wiki_postbot.logger import init_logger

from discord.ext import commands
from discord import Emoji
import pdb

class DiscordClient(Client):

    def __init__(
        self,
        wiki:Wiki,
        intents=None,
        debug:bool=False,
        reply_channel:str="wikibot",
        log_dir:Path=Path('/var/log/wikibot'),
        **kwargs
    ):
        if intents is None:
            intents = Intents.default()
            intents.message_content = True

        self.wiki = wiki
        if self.wiki.sess is None:
            raise RuntimeError("Wiki client is not logged in! Login before passing to discord client")

        self.debug = debug
        self.reply_channel_name = reply_channel
        self.reply_channel = None # type: Optional[discord.TextChannel]

        self.log_dir = Path(log_dir)
        # Try and make log directory, if we cant, it should fail.
        self.log_dir.mkdir(exist_ok=True)

        self.logger = init_logger(name="discord_bot", basedir=self.log_dir)

        super(DiscordClient, self).__init__(intents=intents, **kwargs)

    async def get_channel(self, channel_name:str) -> discord.TextChannel:
        channel = discord.utils.get(self.get_all_channels(), name=channel_name)
        self.logger.debug(f"Got channel {channel}")
        return channel

    async def on_ready(self):
        self.logger.info(f'Logged on as {self.user}')
        self.reply_channel = await self.get_channel(self.reply_channel_name)

    async def on_disconnect(self):
        self.logger.debug(f"wikibot disconnected!")
        await self.reply_channel.send("Wikibot disconnected!")


    async def on_message(self, message:discord.message.Message):
        self.logger.debug(f"Received message: {message.content}\nFrom:{message.author}")

        if message.author == self.user:
            self.logger.debug("Not responding to self")
            return


        if 'good bot' in message.content:
            await message.add_reaction("❤️‍🔥")

        try:
            wl = Wikilink.parse(message.content)
            self.logger.debug(f"Parsed wikilinks: {wl}")
            if len(wl)>0:
                await self.handle_wikilink(message, wl)
        except Exception as e:
            self.logger.exception(f"Error parsing wikilink! got exception: ")


    async def handle_wikilink(self, message:discord.message.Message, wl:List[Wikilink]):
        log_msg = f"Wikilinks detected: \n" + '\n'.join([str(l) for l in wl])
        self.logger.info(log_msg)
        if self.debug:
            await message.channel.send(f"Wikilinks detected: \n" + '\n'.join([str(l) for l in wl]))

        await message.add_reaction("⏳")
        try:
            result = self.wiki.handle_discord(message)
            ok = result.ok
        except Exception as e:
            # TODO: Log here!
            self.logger.exception(f"Exception handling discord message")
            result = None
            ok = False

        if ok:
            await message.remove_reaction("⏳", self.user)
            await message.add_reaction("✅")
        else:
            await message.remove_reaction("⏳", self.user)
            await message.add_reaction("❌")

        if result and result.reply:
            if self.reply_channel is None:
                self.logger.exception(f"Do not have channel to reply to!")
            else:
                await self.reply_channel.send(embed=Embed().add_field(name="WikiLinks", value=result.reply))
                self.logger.debug('replied!')

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

def argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="discord_bot",
        description="A discord bot for posting messages with wikilinks to an associated mediawiki wiki"
    )
    parser.add_argument('-d', '--directory', default='/etc/wikibot/', type=Path,
                        help="Directory that stores credential files and logs")
    parser.add_argument('-w', '--wiki', help="URL of wiki", type=str)
    return parser

def main():
    parser = argparser()
    args = parser.parse_args()
    directory = Path(args.directory)
    log_dir = directory / "logs"

    discord_creds = Discord_Creds.from_json(directory / 'discord_creds.json')
    wiki_creds = Mediawiki_Creds.from_json(directory / 'mediawiki_creds.json')

    wiki = Wiki(url=args.wiki, log_dir=log_dir, creds=wiki_creds)
    wiki.login(wiki_creds)

    client = DiscordClient(wiki=wiki, log_dir=log_dir)
    client.run(discord_creds.token)


