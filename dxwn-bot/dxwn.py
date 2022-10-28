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

bot = commands.Bot(command_prefix = ';', intents = intents)
bot.remove_command('help')

async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            # cut off the .py from the file name
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    await load_extensions()
    await bot.start(TOKEN)

asyncio.run(main())