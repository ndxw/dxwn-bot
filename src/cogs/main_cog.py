import logging
import json
import aiohttp
from random import randint
from dotenv import load_dotenv
from os import getenv

import discord
from discord.ext import commands

load_dotenv()
TOKEN = getenv('DISCORD_TOKEN', default=None)
TENOR_KEY = getenv('TENOR_API_KEY', default=None)

logfile = './log/dxwn.log'
fmt = '[%(levelname)s] %(asctime)s - %(message)s'

logging.basicConfig(filename = logfile, filemode = 'w', format = fmt, level = logging.DEBUG)

class main_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.PINK = discord.Color.from_rgb(255, 200, 255)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        logging.info(f'{member.name} has joined {member.guild}')
        await member.guild.text_channels[0].send(
            f'Greetings, {member.mention}! Welcome to {member.guild}! <:menothinks:893589143303643147>'
        )

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        logging.info(f'{member.name} has left {member.guild}')
        await member.guild.text_channels[0].send(
            f'R.I.P. {member.mention}, you will be remembered...'
        )

    @commands.command()
    async def ping(self, ctx):
        await ctx.send('pong')

    @commands.command()
    async def help(self, ctx, category:str='general', page:int=1):
        '''
        Custom help command, with explanations and usage of each command
        '''
        embed = discord.Embed(title = 'Help', colour = self.PINK)
        embed.description = category.capitalize()

        f = open('resources/help.json', 'r')
        try:
            category_pages = json.load(f)['help'][category]
        except KeyError:
            return await ctx.send('Gimme a valid category!')
        f.close()

        if page < 1:
            page = 1
        elif page > len(category_pages)-1:
            page = len(category_pages)-1
        cmd_dict = category_pages[page]

        for cmd_name in list(cmd_dict.keys()):
            cmd = cmd_dict[cmd_name]
            cmd_info = '' # contains all information regarding a given command

            for info_name in list(cmd.keys()):
                '''
                Unlike "usage","aliases", etc. info types, the title corresponding
                to "description" info is the command name itself.
                '''
                # first add info title
                if info_name != 'description':
                    cmd_info += f'__{info_name.capitalize()}__:\n'
                # then info itself
                cmd_info += f'{cmd[info_name]}\n\n'

            # each command gets one field
            embed.add_field(name=cmd_name, value=cmd_info)

        embed.set_footer(text = f'Page {page} of {len(category_pages)-1}', icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed = embed)

    @commands.command() #gif
    async def gif(self, ctx, *args):

        limit = 10
        query = " ".join(args)

        if query != '':

            async with aiohttp.ClientSession() as session:
                async with session.get("https://tenor.googleapis.com/v2/search?q=%s&key=%s&client_key=%s&limit=%s" % (query, TENOR_KEY, TOKEN, limit)) as gifs:

                    if gifs.status == 200:
                        top_gifs = await gifs.json()
                        await ctx.send(top_gifs["results"][randint(0,limit-1)]["url"])
                    else:
                        top_gifs = None
                        #logging.warning(f'Tenor request status {gifs.status}')
        else:
            del_msg = await ctx.send('Egad! Gimme somethin\' to search for.')
            await del_msg.delete(delay=5)

async def setup(bot):
    await bot.add_cog(main_cog(bot))


