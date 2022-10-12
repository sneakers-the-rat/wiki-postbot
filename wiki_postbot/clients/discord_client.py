import discord
from discord import Client, Intents
from wiki_postbot.creds import Discord_Creds
from wiki_postbot.patterns.wikilink import Wikilink

from discord.ext import commands
from discord import Emoji

intents = Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

DEBUG = False

@bot.event
async def on_message(message:discord.Message):
    print(message)

    if message.content == 'ping':
        await message.channel.send('pong')

    if 'good bot' in message.content:
        await message.add_reaction("❤️‍🔥")

    wl = Wikilink.parse(message.content)
    if len(wl) > 0:
        if DEBUG:
            await message.channel.send(f"Wikilinks detected: \n" + '\n'.join([str(l) for l in wl]))
        else:
            await message.add_reaction("⏳")

    await bot.process_commands(message)

@bot.command()
async def debug(ctx:discord.ext.commands.Context, arg):
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
# @bot.command


#
# class MyClient(Client):
#
#     def __init__(self, intents=None, **kwargs):
#         if intents is None:
#             intents = Intents.default()
#             intents.message_content = True
#
#         super(MyClient, self).__init__(intents=intents, **kwargs)
#
#
#     async def on_ready(self):
#         print('Logged on as', self.user)
#
#     async def on_message(self, message):
#         print(message)
#         # don't respond to ourselves
#         if message.author == self.user:
#             return
#
#         if message.content == 'ping':
#             await message.channel.send('pong')
#
#         wl = Wikilink.parse(message.content)
#         if len(wl)>0:
#             await message.channel.send(f"Wikilinks detected: \n" + '\n'.join([str(l) for l in wl]))



if __name__ == "__main__":
    creds = Discord_Creds.from_json('discord_creds.json')
    # client = MyClient()
    # client.run(creds.token)


    bot.run(creds.token)
