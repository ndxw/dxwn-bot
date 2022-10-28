import logging

from discord.ext import commands

logfile = 'dxwn.log'
fmt = '[%(levelname)s] %(asctime)s - %(message)s'

logging.basicConfig(filename = logfile, filemode = 'w', format = fmt, level = logging.DEBUG)

class musicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def p(self, ctx):
        pass

    @commands.command()
    async def np(self, ctx):
        pass

    @commands.command()
    async def q(self, ctx):
        pass

    @commands.command()
    async def s(self, ctx):
        pass

async def setup(bot):
    await bot.add_cog(musicCog(bot))




