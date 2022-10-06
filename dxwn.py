import os
import discord
import random
import requests
import json

from dotenv import load_dotenv
#from discord.ext import commands
from discord.ui import Button, View

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN', default=None)
GUILD = os.getenv('DISCORD_GUILD', default=None)
TENOR_KEY = os.getenv('TENOR_API_KEY', default=None)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = discord.Client(intents=intents)

prefix = ';'

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name==GUILD:
            break
        
    #members = '\n - '.join([member.name for member in guild.members])
    
    print(
        f'{client.user} is connected to {guild.name}\n'
        f'Guild ID: {guild.id}\n'
        #f'Guild Members: \n - {members}'
    )

@client.event
async def on_member_join(member):
    await member.guild.text_channels[0].send(
        f'Kachow, {member.name}! Welcome to {member.guild}! :skull:'
    )

@client.event
async def on_member_remove(member):
    await member.guild.text_channels[0].send(
        f'R.I.P. {member.name}, you will be remembered...'
    )

@client.event
async def on_message(message):
    if message.author == client.user:
        return
 
    elif message.content.startswith(f'{prefix}bql'):    #;bql command

        limit = 10  #number of search results
        query = 'bing chilling'
        
        gifs = requests.get(
            "https://tenor.googleapis.com/v2/search?q=%s&key=%s&client_key=%s&limit=%s" % (query, TENOR_KEY, TOKEN, limit))

        if gifs.status_code == 200:
            top_gifs = json.loads(gifs.content) #dict
            await message.channel.send(top_gifs["results"][random.randint(0,limit-1)]["url"])
        else:
            top_gifs = None
            await message.channel.send(f'Could not find GIF for "{query}"')
            print('Could not find GIF for "{query}"')

        #print(top_gifs)
     
    elif message.content.startswith(f'{prefix}poll'): #;poll command
        b_True = Button(label='True', style=discord.ButtonStyle.green)
        b_False = Button(label='False', style=discord.ButtonStyle.red)
        b_Youtube = Button(label='Youtube', url='https://youtube.com')
        view = View()
        view.add_item(b_True)
        view.add_item(b_False)
        view.add_item(b_Youtube)
        await message.channel.send(f'True or False?', view=view)


client.run(TOKEN)
