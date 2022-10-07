import os
import discord
import random
import requests
import json
import html

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
    guilds = []

    for guild in client.guilds:
        guilds.append(guild)
        
    #members = '\n - '.join([member.name for member in guild.members])
    
    print(f'{client.user} is connected to:\n')
    for guild in guilds:
        print(
            f'name={guild.name} -- id={guild.id}'
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
            del_msg = await message.channel.send(f'Bad request')
            await del_msg.delete(delay=5)

    elif message.content.startswith(f'{prefix}gif'):

        limit = 10
        query = message.content.replace(f'{prefix}gif', '')

        if (query != ''):
            gifs = requests.get(
                "https://tenor.googleapis.com/v2/search?q=%s&key=%s&client_key=%s&limit=%s" % (query, TENOR_KEY, TOKEN, limit))
        else:
            del_msg = await message.channel.send('Please enter a valid search term')
            await del_msg.delete(delay=5)
            return

        if gifs.status_code == 200:
            top_gifs = json.loads(gifs.content) #dict
            await message.channel.send(top_gifs["results"][random.randint(0,limit-1)]["url"])
        else:
            top_gifs = None
            del_msg = await message.channel.send('Bad request')
            await del_msg.delete(delay=5)

    elif message.content.startswith(f'{prefix}trivia'): #;trivia command
        b_True = Button(label='True', style=discord.ButtonStyle.green)
        b_False = Button(label='False', style=discord.ButtonStyle.red)
        view = View()
        view.add_item(b_True)
        view.add_item(b_False)

        #scuffed i know, need fix
        async def t_callback(interaction):
            if q['results'][0]['correct_answer'] == 'True':
                await interaction.response.edit_message(content=f"{question}\n\nCorrect!", view=None)
            else:
                await interaction.response.edit_message(content=f"{question}\n\nIncorrect...the correct answer is false", view=None)

        async def f_callback(interaction):
            if q['results'][0]['correct_answer'] == 'False':
                await interaction.response.edit_message(content=f"{question}\n\nCorrect!", view=None)
            else:
                await interaction.response.edit_message(content=f"{question}\n\nIncorrect...the correct answer is true", view=None)

        q = requests.get("https://opentdb.com/api.php?amount=1&type=boolean")
        
        if q.status_code == 200:
            q = json.loads(q.content)
            question = html.unescape(q['results'][0]['question']) #fix bad decoding
            #print(q)

            if q['response_code'] == 0:
                await message.channel.send(question, view=view)
                b_True.callback = t_callback
                b_False.callback = f_callback
                
            else:
                del_msg = await message.channel.send(f'Response code: {q["response_code"]}')
                await del_msg.delete(delay=5)
        else:
            q = None
            del_msg = await message.channel.send('Bad request')
            await del_msg.delete(delay=5)







client.run(TOKEN)

