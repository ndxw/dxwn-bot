import logging

from discord.ext import commands
from discord import Embed, Colour

logfile = 'dxwn.log'
fmt = '[%(levelname)s] %(asctime)s - %(message)s'

logging.basicConfig(filename = logfile, filemode = 'w', format = fmt, level = logging.DEBUG)

class mainCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener() #on_ready
    async def on_ready(self):
        logging.info(f'{self.bot.user} is connected to:')
        for guild in self.bot.guilds:
            logging.info(f'name={guild.name} -- id={guild.id}')

    @commands.Cog.listener() #member join
    async def on_member_join(self, member):
        logging.info(f'{member.name} has joined {member.guild}')
        await member.guild.text_channels[0].send(
            f'Greetings, {member.mention}! Welcome to {member.guild}! <:menothinks:893589143303643147>'
        )

    @commands.Cog.listener() #member leave
    async def on_member_remove(self, member):
        logging.info(f'{member.name} has left {member.guild}')
        await member.guild.text_channels[0].send(
            f'R.I.P. {member.mention}, you will be remembered...'
        )

    @commands.Cog.listener() #yeah
    async def on_message(self, ctx):
        pass

    @commands.command() #help
    async def help(self, ctx):
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

async def setup(bot):
    await bot.add_cog(mainCog(bot))


