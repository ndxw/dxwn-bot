import logging

from discord.ext import commands
from YTDLSource import YTDLSource
from asyncio import Queue

logfile = 'dxwn.log'
fmt = '[%(levelname)s] %(asctime)s - %(message)s'

logging.basicConfig(filename = logfile, filemode = 'w', format = fmt, level = logging.DEBUG)

class musicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.q = Queue(maxsize=100)

    @commands.Cog.listener()
    async def on_voice_state_update(member, before, after):
        voice_state = member.guild.voice_client
        # Checking if only the bot is connected to vc
        if voice_state is not None and len(voice_state.channel.members) == 1:
            await voice_state.disconnect()

    @commands.command(aliases=['p'])
    async def play(self, ctx, url:str):
        vc = ctx.voice_client
        if not vc:
            await self.connect(ctx)
        vc = ctx.voice_client

        async with ctx.typing():
            source = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            vc.play(source, after=lambda e: print(f'Player error: {e}') if e else None)

            await ctx.send(f'Now playing {source.title}')

    @commands.command(aliases=['holup'])
    async def pause(self, ctx):
        vc = ctx.voice_client

        if not vc or not vc.is_playing():
            await ctx.send("Can't pause what's not playing!")
            return
        else:
            if not vc.is_paused():
                vc.pause()
                await ctx.send(f'{ctx.author} has paused the song!')

    @commands.command(aliases=['continue','res'])
    async def resume(self, ctx):
        vc = ctx.voice_client

        if not vc:
            await ctx.send("What am I supposed to resume, eh?")
            return
        else:
            if vc.is_paused():
                vc.resume()
                await ctx.send(f'{ctx.author} has resumed the song!')


    @commands.command(aliases=['np']) #now playing
    async def now_playing(self, ctx):
        pass

    @commands.command(aliases=['q']) #queue
    async def queue(self, ctx):
        pass

    @commands.command(aliases=['s']) #skip
    async def skip(self, ctx):
        pass

    @commands.command(aliases=['x','fuckoff','pissoff','dc','leave']) #disconnect
    async def disconnect(self, ctx):
        
        for vclient in self.bot.voice_clients:
            if(vclient.guild == ctx.message.guild):
                return await vclient.disconnect()

        await ctx.send("I'm not in a voice channel!")

    @commands.command(aliases=['come','join'])
    async def connect(self, ctx):
        try:
            vchannel = ctx.author.voice.channel
        except AttributeError:
            await ctx.send('Hop in a voice channel first, please!')
            return
        vc = ctx.voice_client

        if vc:  #bot already connected to a vc
            if vc.channel.id == vchannel.id:    #bot already connected to author channel
                return
            await vc.move_to(vchannel)
        else:
            await vchannel.connect()

async def setup(bot):
    await bot.add_cog(musicCog(bot))




