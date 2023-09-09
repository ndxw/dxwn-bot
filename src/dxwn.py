import os
import asyncio

from dotenv import load_dotenv
from discord.ext import commands
from discord import Intents

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN', default=None)

intents = Intents.default()
intents.members = True
intents.message_content = True

dxwnBot = commands.Bot(command_prefix = ';', case_insensitive = True, intents=intents)
dxwnBot.remove_command('help')

async def load_cogs():
    print('Loading cogs...')
    os.chdir("C:/Users/XxPan/Documents/fold/dxwn-bot-backup")

    for filename in os.listdir("src/cogs"):
        if filename.endswith(".py"):
            # cut off the .py from the file name
            await dxwnBot.load_extension(f'cogs.{filename[:-3]}')
            print(f'{filename[:-7]} cog loaded')

@dxwnBot.event
async def on_ready():
    await load_cogs()

dxwnBot.run(TOKEN)

