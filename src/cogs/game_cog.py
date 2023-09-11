import random
import aiohttp
import html
import logging
import os

from discord.ext import commands
from true_false import TFView
from multiple_choice import MCView
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN', default=None)
TENOR_KEY = os.getenv('TENOR_API_KEY', default=None)

logfile = 'C:/Users/XxPan/Documents/fold/dxwn-bot/log/dxwn.log'
fmt = '[%(levelname)s] %(asctime)s - %(message)s'

logging.basicConfig(filename = logfile, filemode = 'w', format = fmt, level = logging.DEBUG)

class game_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command() #gif
    async def gif(self, ctx, *args):

        limit = 10
        query = " ".join(args)

        if query != '':

            async with aiohttp.ClientSession() as session:
                async with session.get("https://tenor.googleapis.com/v2/search?q=%s&key=%s&client_key=%s&limit=%s" % (query, TENOR_KEY, TOKEN, limit)) as gifs:

                    if gifs.status == 200:
                        top_gifs = await gifs.json()
                        await ctx.send(top_gifs["results"][random.randint(0,limit-1)]["url"])
                    else:
                        top_gifs = None
                        #logging.warning(f'Tenor request status {gifs.status}')
        else:
            del_msg = await ctx.send('Please enter a valid search term')
            await del_msg.delete(delay=5)

    @commands.command() #trivia
    async def trivia(self, ctx, category=''):

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

        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://opentdb.com/api.php?amount=1{cat}") as q:
        
                if q.status == 200:
                    q = await q.json()
                    print(q)
                else:
                    q = None
                    #logging.warning(f'OpenTDB request status {q.status}')
                    del_msg = await ctx.send('Bad request')
                    await del_msg.delete(delay=5)
                    return
        
                if q['response_code'] != 0:
                    #logging.warning(f'OpenTDB bad result code {q["response_code"]}')
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

async def setup(bot):
    await bot.add_cog(game_cog(bot))


