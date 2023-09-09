import logging
import discord
from discord.ext import commands

logfile = 'C:/Users/XxPan/Documents/fold/dxwn-bot-backup/log/dxwn.log'
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
    async def help(self, ctx, page:int=1):
        '''
        Custom help command, with explanations and usage of each command
        '''
        embed = discord.Embed(title = 'Help', colour = self.PINK)
        embed.set_footer(text = f'Page {page} of 4', icon_url=self.bot.user.display_avatar.url)

        if page == 1:
            embed.add_field(name = 'help', value = 'Displays valid commands. \
                            \n\n__Usage__:\n;help <page number>')
            embed.add_field(name = 'ping', value = 'Pong.')
            embed.add_field(name = 'gif', value = 'Gives GIF.\n\n__Usage__:\n;gif <query>')
            embed.add_field(name = 'trivia', value = 'Gives one trivia question,\neither multiple choice or T/F. \
                            \n\n__Usage__:\n;trivia <category> \
                            \n\n__Possible categories__:\ngeneral, books, film, music, theatre,\ntv, video_games, board_games, nature,\ncomputers, \
                            math, myths, sports,\ngeography, history, politics, art,\ncelebrities, animals, vehicles,\ncomics, tech, anime, cartoons')
        elif page == 2:
            embed.add_field(name = 'play', value = 'Searches Youtube. \
                            \n\n__Usage__:\n;play <query or url> \
                            \n\n__Aliases__: p')
            embed.add_field(name = 'pause', value = 'Pauses current track.')
            embed.add_field(name = 'resume', value = 'Resumes current track.')
            embed.add_field(name = 'disconnect', value = 'Disconnects bot from voice channel. \
                            \n\n__Aliases__: dc')
            embed.add_field(name = 'queue', value = 'Displays upcoming tracks. \
                            \n\n__Usage__:\n;queue <page number> \
                            \n\n__Aliases__: q')
            embed.add_field(name = 'clearqueue', value = 'Clears queue. \
                            \n\n__Aliases__: clear, cq')
        elif page == 3:
            pass
        elif page == 4:
            pass

        await ctx.send(embed = embed)

async def setup(bot):
    await bot.add_cog(main_cog(bot))


