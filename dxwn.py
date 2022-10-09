import os
import math
import random
import requests
import json
import html
import logging

from dotenv import load_dotenv
#from discord.ext import commands
from discord.ui import Button, View
from discord import Client, Intents, ButtonStyle

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN', default=None)
GUILD = os.getenv('DISCORD_GUILD', default=None)
TENOR_KEY = os.getenv('TENOR_API_KEY', default=None)

intents = Intents.default()
intents.members = True
intents.message_content = True
client = Client(intents=intents)

logfile = 'dxwn.log'
fmt = '[%(levelname)s] %(asctime)s - %(message)s'

logging.basicConfig(filename = logfile, filemode = 'w', format = fmt, level = logging.DEBUG)

prefix = ';'

class MCView(View):

    q = None
    author = None

    def __init__(self, q, author):
        super().__init__()

        self.q = q
        self.author = author
        answers = q['results'][0]['incorrect_answers']
        answers.append(q['results'][0]['correct_answer'])
        random.shuffle(answers)
        for i, answer in enumerate(answers):
            self.add_item(MCButton(label=answer, style=ButtonStyle.gray, row=math.floor(i/2)))

class MCButton(Button):

    async def callback(self, interaction):
        if interaction.user == self.view.author:
            if self.view.q['results'][0]['correct_answer'] == self.label:
                self.style = ButtonStyle.green
                await interaction.response.edit_message(content=f"{self.view.q['results'][0]['question']}\n\nCorrect!", view=self.view)
                self.view.stop()
            else:
                self.style = ButtonStyle.red
                for item in self.view.children:
                    if item.label == self.view.q['results'][0]['correct_answer']:
                        item.style = ButtonStyle.green

                await interaction.response.edit_message(content=f"{self.view.q['results'][0]['question']}\n\nIncorrect...", view=self.view)
                self.view.stop()

class TFView(View):

    q = None
    author = None

    def __init__(self, q, author):
        super().__init__()

        self.q = q
        self.author = author
        self.add_item(TFButton(label='True', style=ButtonStyle.green))
        self.add_item(TFButton(label='False', style=ButtonStyle.red))

class TFButton(Button):

    async def callback(self, interaction):
        if interaction.user == self.view.author:
            if self.view.q['results'][0]['correct_answer'] == self.label:
                await interaction.response.edit_message(content=f"{self.view.q['results'][0]['question']}\n\nCorrect!", view=None)
            else:
                await interaction.response.edit_message(content=f"{self.view.q['results'][0]['question']}\n\nIncorrect...the correct answer is {self.view.q['results'][0]['correct_answer']}", view=None)
     
@client.event
async def on_ready():
    logging.info(f'{client.user} is connected to:\n')
    for guild in client.guilds:
        logging.info(f'name={guild.name} -- id={guild.id}')

@client.event
async def on_member_join(member):
    logging.info(f'{member.name} has joined {member.guild}')
    await member.guild.text_channels[0].send(
        f'Kachow, {member.name}! Welcome to {member.guild}! :skull:'
    )

@client.event
async def on_member_remove(member):
    logging.info(f'{member.name} has left {member.guild}')
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
            top_gifs = json.loads(gifs.content)
            await message.channel.send(top_gifs["results"][random.randint(0,limit-1)]["url"])
        else:
            top_gifs = None
            logging.warning(f'Tenor request status {gifs.status_code}')

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
            top_gifs = json.loads(gifs.content)
            await message.channel.send(top_gifs["results"][random.randint(0,limit-1)]["url"])
        else:
            top_gifs = None
            logging.warning(f'Tenor request status {gifs.status_code}')

    elif message.content.startswith(f'{prefix}trivia'): #;trivia command

        q = requests.get("https://opentdb.com/api.php?amount=1")
        
        if q.status_code == 200:
            q = json.loads(q.content)
        else:
            q = None
            logging.warning(f'OpenTDB request status {q.status_code}')
            del_msg = await message.channel.send('Bad request')
            await del_msg.delete(delay=5)
            return
        
        if q['response_code'] != 0:
            logging.warning(f'OpenTDB bad result code {q["response_code"]}')
            del_msg = await message.channel.send('No results')
            await del_msg.delete(delay=5)
            return

        q['results'][0]['question'] = html.unescape(q['results'][0]['question']) #fix bad decoding
        q['results'][0]['correct_answer'] = html.unescape(q['results'][0]['correct_answer'])
        for i, answer in enumerate(q['results'][0]['incorrect_answers']):
            q['results'][0]['incorrect_answers'][i] = html.unescape(answer)

        if q['results'][0]['type'] == 'boolean': #True or False

            view = TFView(q, message.author)
            await message.channel.send(f'{q["results"][0]["question"]}', view=view)
        
        elif q['results'][0]['type'] == 'multiple': # Multiple Choice

            view = MCView(q, message.author)
            await message.channel.send(f'{q["results"][0]["question"]}', view=view)

client.run(TOKEN)

