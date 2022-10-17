import os
import math
import random
import requests
import asyncio
import aiohttp
import json
import html
import logging

from dotenv import load_dotenv
from discord.ext import commands
from discord.ui import Button, View
from discord import Intents, ButtonStyle, Embed, Colour


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN', default=None)
TENOR_KEY = os.getenv('TENOR_API_KEY', default=None)

intents = Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix = ';', intents = intents)
bot.remove_command('help')

logfile = 'dxwn.log'
fmt = '[%(levelname)s] %(asctime)s - %(message)s'

logging.basicConfig(filename = logfile, filemode = 'w', format = fmt, level = logging.DEBUG)

class MCView(View):

    q = None
    author = None

    def __init__(self, q, author):
        super().__init__()

        self.q = q
        self.author = author

        #randomize answers
        answers = q['results'][0]['incorrect_answers']
        answers.append(q['results'][0]['correct_answer'])
        random.shuffle(answers)

        #create button objects
        for i, answer in enumerate(answers):                            
            self.add_item(MCButton(label=answer, style=ButtonStyle.gray, row=math.floor(i/2)))  #buttons in two columns (2x2)

class MCButton(Button):

    async def callback(self, interaction):

        #only command invoker can interact with MC questions
        if interaction.user == self.view.author: 

            if self.view.q['results'][0]['correct_answer'] == self.label:
                self.style = ButtonStyle.green
                await interaction.response.edit_message(content=f"{self.view.q['results'][0]['question']}\n\n**Correct!**", view=self.view)
                self.view.stop()

            else:
                self.style = ButtonStyle.red
                for item in self.view.children:
                    if item.label == self.view.q['results'][0]['correct_answer']:
                        item.style = ButtonStyle.green

                await interaction.response.edit_message(content=f"{self.view.q['results'][0]['question']}\n\n**Incorrect...**", view=self.view)
                self.view.stop()

class TFView(View):

    q = None
    author = None

    def __init__(self, q, author):
        super().__init__()

        self.q = q
        self.author = author

        #create button objects
        self.add_item(TFButton(label='True', style=ButtonStyle.green))
        self.add_item(TFButton(label='False', style=ButtonStyle.red))

class TFButton(Button):

    async def callback(self, interaction):

        #only command invoker can interact with TF questions
        if interaction.user == self.view.author:

            if self.view.q['results'][0]['correct_answer'] == self.label:
                await interaction.response.edit_message(
                    content=f"{self.view.q['results'][0]['question']}\n\n**Correct!**", view=None)

            else:
                await interaction.response.edit_message(
                    content=f"{self.view.q['results'][0]['question']}\n\n**Incorrect...the correct answer is {self.view.q['results'][0]['correct_answer']}**", view=None)
     
@bot.event #on ready
async def on_ready():
    logging.info(f'{bot.user} is connected to:\n')
    for guild in bot.guilds:
        logging.info(f'name={guild.name} -- id={guild.id}')

@bot.event #member join
async def on_member_join(member):
    logging.info(f'{member.name} has joined {member.guild}')
    await member.guild.text_channels[0].send(
        f'Greetings, {member.mention}! Welcome to {member.guild}! <:menothinks:893589143303643147>'
    )

@bot.event #member leave
async def on_member_remove(member):
    logging.info(f'{member.name} has left {member.guild}')
    await member.guild.text_channels[0].send(
        f'R.I.P. {member.mention}, you will be remembered...'
    )

@bot.event #yeah
async def on_message(ctx):
    message_lower = ctx.content.lower()

    if message_lower.find('penis') != -1 or message_lower.find('cock') != -1 or message_lower.find('dick') != -1:
        await ctx.add_reaction('🍆')
        if message_lower.find('sucker') != -1:
            await ctx.add_reaction('💦')

    await bot.process_commands(ctx)

@bot.command() #help
async def help(ctx):
    embed = Embed(
        title = 'Commands',
        #description = 'what it do',
        colour = Colour.gold()
    )

    embed.set_footer(text = 'schlump#3499 | @ndx.w')
    embed.add_field(name = 'bql', value = 'Gives GIF of "bing chilling"!')
    embed.add_field(name = 'gif', value = 'Gives GIF, takes one search term (multi-word terms should go in "quotes")')
    embed.add_field(name = 'trivia', value = 'Gives one trivia question, either multiple choice or true or false\n\n**Possible categories:**\ngeneral\nbooks\nfilm\nmusic\ntheatre\ntv\nvideo_games\nboard_games\nnature\ncomputers\nmath\nmyths\nsports\ngeography\nhistory\npolitics\nart\ncelebrities\nanimals\nvehicles\ncomics\ntech\nanime\ncartoons\n')

    await ctx.send(embed = embed)

@bot.command() #bql
async def bql(ctx):

    limit = 10  #number of search results
    query = 'bing chilling'
        
    async with aiohttp.ClientSession() as session: #non-blocking http request
        async with session.get("https://tenor.googleapis.com/v2/search?q=%s&key=%s&client_key=%s&limit=%s" % (query, TENOR_KEY, TOKEN, limit)) as gifs:

            if gifs.status == 200:
                top_gifs = await gifs.json()
                await ctx.send(top_gifs["results"][random.randint(0,limit-1)]["url"])
            else:
                top_gifs = None
                logging.warning(f'Tenor request status {gifs.status}')

@bot.command() #gif
async def gif(ctx, query=''):

    limit = 10

    if query != '':

        async with aiohttp.ClientSession() as session: #non-blocking http request
            async with session.get("https://tenor.googleapis.com/v2/search?q=%s&key=%s&client_key=%s&limit=%s" % (query, TENOR_KEY, TOKEN, limit)) as gifs:

                if gifs.status == 200:
                    top_gifs = await gifs.json()
                    await ctx.send(top_gifs["results"][random.randint(0,limit-1)]["url"])
                else:
                    top_gifs = None
                    logging.warning(f'Tenor request status {gifs.status}')
    else:
        del_msg = await ctx.send('Please enter a valid search term')
        await del_msg.delete(delay=5)

@bot.command() #trivia
async def trivia(ctx, category=''):

    categories = {
        'general':'&category=9',
        'books':'&category=10',
        'film':'&category=11',
        'music':'&category=12',
        'theatre':'&category=13',
        'tv':'&category=14',
        'video_games':'&category=15',
        'board_games':'&category=16',
        'nature':'&category=17',
        'computers':'&category=18',
        'math':'&category=19',
        'myths':'&category=20',
        'sports':'&category=21',
        'geography':'&category=22',
        'history':'&category=23',
        'politics':'&category=24',
        'art':'&category=25',
        'celebrities':'&category=26',
        'animals':'&category=27',
        'vehicles':'&category=28',
        'comics':'&category=29',
        'tech':'&category=30',
        'anime':'&category=31',
        'cartoons':'&category=32',
        }
    
    if category == '':
        cat = ''
    else:
        cat = categories[category]

    async with aiohttp.ClientSession() as session: #non-blocking http request
        async with session.get(f"https://opentdb.com/api.php?amount=1{cat}") as q:
        
            if q.status == 200:
                q = await q.json()
                print(q)
            else:
                q = None
                logging.warning(f'OpenTDB request status {q.status}')
                del_msg = await ctx.send('Bad request')
                await del_msg.delete(delay=5)
                return
        
            if q['response_code'] != 0:
                logging.warning(f'OpenTDB bad result code {q["response_code"]}')
                del_msg = await ctx.send('No results')
                await del_msg.delete(delay=5)
                return

            q['results'][0]['question'] = html.unescape(q['results'][0]['question']) #fix bad decoding
            q['results'][0]['correct_answer'] = html.unescape(q['results'][0]['correct_answer'])
            for i, answer in enumerate(q['results'][0]['incorrect_answers']):
                q['results'][0]['incorrect_answers'][i] = html.unescape(answer)

            if q['results'][0]['type'] == 'boolean': #True or False

                view = TFView(q, ctx.author)
                await ctx.send(f'{q["results"][0]["question"]}', view=view)
        
            elif q['results'][0]['type'] == 'multiple': #Multiple Choice

                view = MCView(q, ctx.author)
                await ctx.send(f'{q["results"][0]["question"]}', view=view)



bot.run(TOKEN)

