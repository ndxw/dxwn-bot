import os
import asyncio

import discord
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN', default=None)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class dxwnBot(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix=';', case_insensitive=True, intents=intents)

        self.PINK = discord.Color.from_rgb(255, 200, 255)


dxwnBot = dxwnBot()
dxwnBot.remove_command('help')

async def load_cogs():
    print('Loading cogs...')
    os.chdir("./")

    for filename in os.listdir("src/cogs"):
        if filename.endswith(".py"):
            # cut off the .py from the file name
            await dxwnBot.load_extension(f'cogs.{filename[:-3]}')
            print(f'{filename[:-7]} cog loaded')

@dxwnBot.event
async def on_ready():
    await load_cogs()

dxwnBot.run(TOKEN)

