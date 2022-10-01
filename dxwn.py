import os
import discord
import random

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN', default=None)
GUILD = os.getenv('DISCORD_GUILD', default=None)

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name==GUILD:
            break

    members = '\n - '.join([member.name for member in guild.members])
    
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name} (id: {guild.id})\n'
        f'Server Members: \n - {members}'
    )

@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Kachow, {member.name}! Welcome to hhhhhh! :skull:'
    )

@client.event
async def on_member_leave(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'R.I.P. {member.name}, you will be remembered...'
    )

client.run(TOKEN)
