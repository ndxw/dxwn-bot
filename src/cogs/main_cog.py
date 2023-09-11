import logging
import json
import discord
from discord.ext import commands

logfile = 'C:/Users/XxPan/Documents/fold/dxwn-bot/log/dxwn.log'
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

async def setup(bot):
    await bot.add_cog(main_cog(bot))


