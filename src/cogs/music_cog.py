import re
from random import randint
import discord
from discord.interactions import Interaction
from discord.ui import View, Button
from discord.ext import commands
import lavalink
from lavalink.filters import LowPass, Tremolo, Vibrato, Rotation, Karaoke, Equalizer

url_rx = re.compile(r'https?://(?:www\.)?.+')


class LavalinkVoiceClient(discord.VoiceClient):
    """
    This is the preferred way to handle external voice sending
    This client will be created via a cls in the connect method of the channel
    see the following documentation:
    https://discordpy.readthedocs.io/en/latest/api.html#voiceprotocol
    """

    def __init__(self, client: discord.Client, channel: discord.abc.Connectable):
        self.client = client
        self.channel = channel
        # ensure a client already exists
        if hasattr(self.client, 'lavalink'):
            self.lavalink = self.client.lavalink
        else:
            self.client.lavalink = lavalink.Client(client.user.id)
            self.client.lavalink.add_node(
                'localhost',
                2333,
                'youshallnotpass',
                'us',
                'default-node'
            )
            self.lavalink = self.client.lavalink

    async def on_voice_server_update(self, data):
        # the data needs to be transformed before being handed down to
        # voice_update_handler
        lavalink_data = {
            't': 'VOICE_SERVER_UPDATE',
            'd': data
        }
        await self.lavalink.voice_update_handler(lavalink_data)

    async def on_voice_state_update(self, data):
        # the data needs to be transformed before being handed down to
        # voice_update_handler
        lavalink_data = {
            't': 'VOICE_STATE_UPDATE',
            'd': data
        }
        await self.lavalink.voice_update_handler(lavalink_data)

    async def connect(self, *, timeout: float, reconnect: bool, self_deaf: bool = False, self_mute: bool = False) -> None:
        """
        Connect the bot to the voice channel and create a player_manager
        if it doesn't exist yet.
        """
        # ensure there is a player_manager when creating a new voice_client
        self.lavalink.player_manager.create(guild_id=self.channel.guild.id)
        await self.channel.guild.change_voice_state(channel=self.channel, self_mute=self_mute, self_deaf=self_deaf)

    async def disconnect(self, *, force: bool = False) -> None:
        """
        Handles the disconnect.
        Cleans up running player and leaves the voice client.
        """
        player = self.lavalink.player_manager.get(self.channel.guild.id)

        # no need to disconnect if we are not connected
        if not force and not player.is_connected:
            return

        # None means disconnect
        await self.channel.guild.change_voice_state(channel=None)

        # update the channel_id of the player to None
        # this must be done because the on_voice_state_update that would set channel_id
        # to None doesn't get dispatched after the disconnect
        player.channel_id = None
        self.cleanup()


class musicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.PINK = discord.Color.from_rgb(255, 200, 255)
        self.rewind_stack = []

        if not hasattr(bot, 'lavalink'):  # This ensures the client isn't overwritten during cog reloads.
            bot.lavalink = lavalink.Client(bot.user.id)
            bot.lavalink.add_node('127.0.0.1', 2333, 'youshallnotpass', 'eu', 'default-node')  # Host, Port, Password, Region, Name

        lavalink.add_event_hook(self.track_hook)

    def cog_unload(self):
        """ Cog unload handler. This removes any event hooks that were registered. """
        self.bot.lavalink._event_hooks.clear()

    async def cog_before_invoke(self, ctx):
        """ Command before-invoke handler. """
        guild_check = ctx.guild is not None
        #  This is essentially the same as `@commands.guild_only()`
        #  except it saves us repeating ourselves (and also a few lines).

        if guild_check:
            await self.ensure_voice(ctx)
            #  Ensure that the bot and command author share a mutual voicechannel.

        return guild_check

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(error.original)
            # The above handles errors thrown in this cog and shows them to the user.
            # This shouldn't be a problem as the only errors thrown in this cog are from `ensure_voice`
            # which contain a reason string, such as "Join a voicechannel" etc. You can modify the above
            # if you want to do things differently.

    async def ensure_voice(self, ctx):
        """ This check ensures that the bot and command author are in the same voicechannel. """
        player = self.bot.lavalink.player_manager.create(ctx.guild.id)
        # Create returns a player if one exists, otherwise creates.
        # This line is important because it ensures that a player always exists for a guild.

        # Most people might consider this a waste of resources for guilds that aren't playing, but this is
        # the easiest and simplest way of ensuring players are created.

        # These are commands that require the bot to join a voicechannel (i.e. initiating playback).
        # Commands such as volume/skip etc don't require the bot to be in a voicechannel so don't need listing here.
        should_connect = ctx.command.name in ('play',)

        if not ctx.author.voice or not ctx.author.voice.channel:
            # Our cog_command_error handler catches this and sends it to the voicechannel.
            # Exceptions allow us to "short-circuit" command invocation via checks so the
            # execution state of the command goes no further.
            raise commands.CommandInvokeError('Join a voicechannel first.')

        v_client = ctx.voice_client
        if not v_client:
            if not should_connect:
                raise commands.CommandInvokeError('Not connected.')

            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:  # Check user limit too?
                raise commands.CommandInvokeError('I need the `CONNECT` and `SPEAK` permissions.')

            player.store('channel', ctx.channel.id)
            await ctx.author.voice.channel.connect(cls=LavalinkVoiceClient)
        else:
            if v_client.channel.id != ctx.author.voice.channel.id:
                raise commands.CommandInvokeError('You need to be in my voicechannel.')

    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            # When this track_hook receives a "QueueEndEvent" from lavalink.py
            # it indicates that there are no tracks left in the player's queue.
            # To save on resources, we can tell the bot to disconnect from the voicechannel.
            guild_id = event.player.guild_id
            guild = self.bot.get_guild(guild_id)
            await guild.voice_client.disconnect(force=True)

    def is_in(self, user_id:int, channel_id:int):
        """Returns True if the user is in the channel"""

        channel = self.bot.get_channel(channel_id)

        for member in channel.members:
            if user_id == member.id:
                return True
        return False

    def format_time(self, time_ms:int):
        ll_format = lavalink.format_time(time_ms)

        if (ll_format[0:2] == '00'):
            return ll_format[3:]
        return ll_format
        
    def generate_scrubber(self, elapsed_ms:int, total_ms:float):
        """ Returns a scrubber in string format, proportional to elapsed time of track. """
        start = '╞'
        end = '╡'
        playhead = '◉'
        scrubber_no_head = '════════════════════'
        denominator = len(scrubber_no_head)
        playhead_position = int(round(elapsed_ms / total_ms * denominator))
        scrubber_str = scrubber_no_head[0:playhead_position] + playhead + scrubber_no_head[playhead_position+1:]

        return start + scrubber_str + end

    @commands.command(aliases=['p'])
    async def play(self, ctx, *, query: str):
        """ Searches and plays a song from a given query. """
        # Get the player for this guild from cache.
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        # Remove leading and trailing <>. <> may be used to suppress embedding links in Discord.
        query = query.strip('<>')

        # Check if the user input might be a URL. If it isn't, we can Lavalink do a YouTube search for it instead.
        # SoundCloud searching is possible by prefixing "scsearch:" instead.
        if not url_rx.match(query):
            query = f'ytsearch:{query}'

        # Get the results for the query from Lavalink.
        results = await player.node.get_tracks(query)

        # Results could be None if Lavalink returns an invalid response (non-JSON/non-200 (OK)).
        # Alternatively, results.tracks could be an empty array if the query yielded no tracks.
        if not results or not results.tracks:
            return await ctx.send('Nothing found!')

        embed = discord.Embed(color=self.PINK)

        # Valid loadTypes are:
        #   TRACK_LOADED    - single video/direct URL)
        #   PLAYLIST_LOADED - direct URL to playlist)
        #   SEARCH_RESULT   - query prefixed with either ytsearch: or scsearch:.
        #   NO_MATCHES      - query yielded no results
        #   LOAD_FAILED     - most likely, the video encountered an exception during loading.
        if results.load_type == 'PLAYLIST_LOADED':
            tracks = results.tracks
            total_duration = 0

            for track in tracks:
                # Add all of the tracks from the playlist to the queue.
                player.add(requester=ctx.author.id, track=track)
                total_duration += track.duration

            embed.title = 'Playlist Queued!'
            embed.description = f'{results.playlist_info.name}'
            embed.set_footer(text=f'{len(tracks)} tracks • Total Length: {self.format_time(total_duration)}', icon_url=self.bot.user.display_avatar.url)
            try:
                embed.set_thumbnail(url=f'https://img.youtube.com/vi/{tracks[0].identifier}/default.jpg')
            except: #discord.HTTPException?
                pass

        elif results.load_type == 'SEARCH_RESULT':
            track = results.tracks[0]
            embed.title = 'Track Queued!'
            embed.description = f'[{track.title}]({track.uri})'
            embed.set_footer(text=f'Length: {self.format_time(track.duration)}', icon_url=self.bot.user.display_avatar.url)
            try:
                embed.set_thumbnail(url=f'https://img.youtube.com/vi/{track.identifier}/default.jpg')
            except: #discord.HTTPException?
                pass

            player.add(requester=ctx.author.id, track=track)

        elif results.load_type == 'NO_MATCHES':
            embed.title = 'No Results.'
            embed.description = 'GG go next ->'

        elif results.load_type == 'LOAD_FAILED':
            embed.title = 'You Done Goofed.'
            embed.description = ''

        await ctx.send(embed=embed)

        # We don't want to call .play() if the player is playing as that will effectively skip
        # the current track.
        if not player.is_playing:
            await player.play()

    @commands.command(aliases=[])
    async def pause(self, ctx):
        """ Pauses current track. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not ctx.voice_client:
            return await ctx.send('Not connected.')
        if player.current == None:
            return await ctx.send('Nothin\' *to* pause...')
        
        if player.paused == False:
            await ctx.send(f'**{player.current.title}** paused!')
            await player.set_pause(True)
        else:
            await ctx.send('What, am I supposed to pause *harder*?')

    @commands.command(aliases=[])
    async def resume(self, ctx):
        """ Resumes current track. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not ctx.voice_client:
            return await ctx.send('Not connected.')
        if player.current == None:
            return await ctx.send('Give me something *to* resume...')
        
        if player.paused == True:
            await ctx.send('Startin\' \'er back up!')
            await player.set_pause(False)
        else:
            await ctx.send('Maybe you\'ve got me muted?')

    @commands.command(aliases=['dc'])
    async def disconnect(self, ctx):
        """ Disconnects the player from the voice channel and clears its queue. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not ctx.voice_client:
            # We can't disconnect, if we're not connected.
            return await ctx.send('Not connected.')

        if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            # Abuse prevention. Users not in voice channels, or not in the same voice channel as the bot
            # may not disconnect the bot.
            return await ctx.send('You\'re not in my voicechannel!')

        # Clear the queue to ensure old tracks don't start playing
        # when someone else queues something.
        player.queue.clear()
        # Stop the current track so Lavalink consumes less resources.
        await player.stop()
        # Disconnect from the voice channel.
        await ctx.voice_client.disconnect(force=True)
        await ctx.send('See you next time!')

    @commands.command(aliases=['encore'])
    async def loop(self, ctx):
        """ Loops current track. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not ctx.voice_client:
            return await ctx.send('Not connected.')
        
        if not player.is_playing:
            return await ctx.send('What, you want me to loop... nothing?')
        
        if player.loop == player.LOOP_NONE:
            # 0: no loop
            # 1: loop current track
            # 2: loop queue
            player.set_loop(1)
            await ctx.send(f'**{player.current.title}** is set to loop.')
        elif player.loop == player.LOOP_SINGLE: # disable loop
            player.set_loop(0)
            await ctx.send(f'Knew you\'d get sick of **{player.current.title}**.')

    @commands.command(aliases=['q'])
    async def queue(self, ctx, page:int=1):
        """ Shows the upcoming eight songs. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        tracks_per_page = 8
        last_page = int(len(player.queue)/tracks_per_page) + 1

        if not ctx.voice_client:
            return await ctx.send('Not connected.')
        
        embed = discord.Embed(color=self.PINK, title='Queue')

        if len(player.queue) == 0:  # empty queue
            embed.description = '\*crickets\* 🦗'
            return await ctx.send(embed=embed)
        elif len(player.queue) <= tracks_per_page*(page-1):   # page number exceeds max, set to last page
            page = last_page

        total_duration = player.current.duration - player.position
        
        for q_position in range(len(player.queue)):
            track = player.queue[q_position]

            # don't add preceding or succeeding queue pages to embed
            if q_position < tracks_per_page*(page-1) or q_position > tracks_per_page*page-1:
                total_duration += track.duration
                continue
            else:
                embed.add_field(name=track.title, 
                                value=f'Requested by `{self.bot.get_user(int(track.requester)).display_name}` • \
                                    Length: `{self.format_time(track.duration)}` • Wait Time: `{self.format_time(total_duration)}` • [[url]]({track.uri})', 
                                inline=False)
                #embed.add_field(name='', value=f'Length: {self.format_time(track.duration)} - T.U.P: {self.format_time(total_duration)}')
                total_duration += track.duration

        embed.set_footer(text=f'Page {page} of {last_page} • Total Length: {self.format_time(total_duration)}', icon_url=self.bot.user.display_avatar.url)

        await ctx.send(embed=embed)

    @commands.command(aliases=['clear','cq'])
    async def clearqueue(self, ctx):
        """ Empties queue and stops playing. """
        # add voting system?

        if not ctx.voice_client:
            return await ctx.send('Not connected.')

        view = View()
        view.add_item(NoButton())
        view.add_item(YesButton())
        await ctx.send('Are you sure you want to clear the queue?', view=view)

    @commands.command(aliases=['rm'])
    async def remove(self, ctx, index:int):
        """ Removes track at queue position. """

    @commands.command(aliases=['np'])
    async def nowplaying(self, ctx):
        """ Shows current track. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not ctx.voice_client:
            return await ctx.send('Not connected.')
        
        if not player.is_playing:
            return await ctx.send('You are now listening to... nothing.')
        
        embed = discord.Embed(color=self.PINK, title='Now Playing:')
        scrubber = self.generate_scrubber(player.position, player.current.duration)
        fmt_elapsed = self.format_time(player.position)
        fmt_duration = self.format_time(player.current.duration)
        requester_name = self.bot.get_user(player.current.requester).display_name
        requester_avatar = self.bot.get_user(player.current.requester).display_avatar.url

        # title, url
        embed.add_field(name='', value=f'[{player.current.title}]({player.current.uri})')
        # scrubber
        embed.add_field(name=f'{fmt_elapsed} {scrubber} {fmt_duration}', value='', inline=False)
        # requester
        embed.set_footer(text=f'Requested by {requester_name}', icon_url=requester_avatar)
        try:
            embed.set_thumbnail(url=f'https://img.youtube.com/vi/{player.current.identifier}/default.jpg')
        except: #discord.HTTPException?
            pass
        
        await ctx.send(embed=embed)

    @commands.command(aliases=['s'])
    async def skip(self, ctx):
        """ Skips current track. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not ctx.voice_client:
            return await ctx.send('Not connected.')
        
        # Abuse protection; only song requester can skip, unless they aren't in the voice channel, in which case anyone can skip
        if (ctx.author.id != player.current.requester) and (self.is_in(user_id=player.current.requester, channel_id=player.channel_id)):
            return await ctx.send('A little rude to skip someone else\'s song, don\'t you think?')
        
        await ctx.send(f'**{player.current.title}** skipped!')
        await player.skip()
        if player.current != None:
            await ctx.send(f'Next up, **{player.current.title}**...')

    #@commands.command(aliases=['rw'])
    async def rewind(self, ctx):
        """ Rewinds one track. """
        '''
        in play fxn add finished track to secondary list
        when rewind is called, pop the last track added to secondary list and add to index 0 of lavalink player
        then skip current track

        NOTE: don't think this is currently implementable
        '''

    @commands.command(aliases=['shakyshaky'])
    async def shuffle(self, ctx):
        """ Shuffles queue. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not ctx.voice_client:
            return await ctx.send('Not connected.')
        
        shuffled_queue = []
        queue_len = len(player.queue)

        if queue_len > 1:
            # based on Fisher-Yates algorithm
            for i in range(queue_len):
                next_track = randint(0,queue_len - i - 1)
                shuffled_queue.append(player.queue[next_track])
            player.queue = shuffled_queue
            await ctx.send('Queue Shuffled!')
    
        else:
            await ctx.send('One song? Really?')

    @commands.command(aliases=['lpf'])
    async def lowpass(self, ctx, strength: float):
        """ Sets the strength of the low pass filter. """
        # Get the player for this guild from cache.
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        # This enforces that strength should be a minimum of 0.
        # There's no upper limit on this filter.
        strength = max(0.0, strength)

        # Even though there's no upper limit, we will enforce one anyway to prevent
        # extreme values from being entered. This will enforce a maximum of 100.
        strength = min(100, strength)

        embed = discord.Embed(color=self.PINK, title='Low Pass Filter')

        # A strength of 0 effectively means this filter won't function, so we can disable it.
        if strength == 0.0:
            await player.remove_filter(LowPass)
            embed.description = 'Disabled **Low Pass Filter**'
            return await ctx.send(embed=embed)

        # Lets create our filter.
        low_pass = LowPass()
        low_pass.update(smoothing=strength)  # Set the filter strength to the user's desired level.

        # This applies our filter. If the filter is already enabled on the player, then this will
        # just overwrite the filter with the new values.
        await player.set_filter(low_pass)

        embed.description = f'Set **Low Pass** strength to {strength}.'
        await ctx.send(embed=embed)

    @commands.command(aliases=['hpf'])
    async def highpass(self, ctx, strength: float):
        """ Sets the strength of the high pass filter. """
        # no highpass filter, maybe use karaoke filter?

    @commands.command(aliases=['tsf'])
    async def timescale(self, ctx, speed:float = 1.0, pitch:float = 1.0, rate:float = 1.0):
        """ Speed up/slow down, change pitch, playback rate (wat difference speed vs. playback rate?). """
        # apparently player.position doesn't work correctly when track is sped up?

    @commands.command(aliases=['tmf'])
    async def tremolo(self, ctx, frequency:float = 4.0, depth:float = 0.5):
        """ Shiver me timbers. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        # Enforces a lower limit
        frequency = max(0.0, frequency)
        depth = max(0.0, depth)

        # Enforces an upper limit
        frequency = min(100.0, frequency)
        depth = min(1.0, depth)

        embed = discord.Embed(color=self.PINK, title='Tremolo')

        # A strength of 0 effectively means this filter won't function, so we can disable it.
        if frequency == 0.0:
            await player.remove_filter(Tremolo)
            embed.description = 'Disabled **Tremolo Filter**'
            return await ctx.send(embed=embed)

        # Lets create our filter.
        tremolo = Tremolo()
        tremolo.update(frequency=frequency, depth=depth)

        # This applies our filter. If the filter is already enabled on the player, then this will
        # just overwrite the filter with the new values.
        await player.set_filter(tremolo)

        embed.description = f'Set **Tremolo Filter** frequency to {frequency} and depth to {depth}.'
        await ctx.send(embed=embed)

    @commands.command(aliases=['vbf'])
    async def vibrato(self, ctx, frequency:float = 8.0, depth:float = 0.5):
        """ Wobbly, bobbly. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        # Enforces a lower limit
        frequency = max(0.0, frequency)
        depth = max(0.0, depth)

        # Enforces an upper limit
        frequency = min(14.0, frequency)
        depth = min(1.0, depth)

        embed = discord.Embed(color=self.PINK, title='Vibrato')

        # A strength of 0 effectively means this filter won't function, so we can disable it.
        if frequency == 0.0:
            await player.remove_filter(Vibrato)
            embed.description = 'Disabled **Vibrato Filter**'
            return await ctx.send(embed=embed)

        # Lets create our filter.
        vibrato = Vibrato()
        vibrato.update(frequency=frequency, depth=depth)

        # This applies our filter. If the filter is already enabled on the player, then this will
        # just overwrite the filter with the new values.
        await player.set_filter(vibrato)

        embed.description = f'Set **Vibrato Filter** frequency to {frequency} and depth to {depth}.'
        await ctx.send(embed=embed)

    @commands.command(aliases=['rtf'])
    async def rotate(self, ctx, frequency:float = 1.0):
        """ 8D audio effect. """

    @commands.command(aliases=['eqf'])
    async def equalizer(self, ctx):
        """ You know what an equalizer is. """
        # not sure about this one, maybe use discord.buttons to control it?

    @commands.command(aliases=['clearf'])
    async def clearfilter(self, ctx):
        """ Removes all filters applied to audio. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        
        if not ctx.voice_client:
            return await ctx.send('Not connected.')
        
        embed = discord.Embed(color=self.PINK, title='No. More. Filters!')
        
        await player.clear_filters()
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(musicCog(bot))

class NoButton(Button):
    """ Clear queue confirmation. """
    def __init__(self):
        super().__init__(label='No', style=discord.ButtonStyle.danger)

    async def callback(self, interaction: Interaction):
        await interaction.response.edit_message(content='Make up your mind!', view=None)

class YesButton(Button):
    """ Clear queue confirmation. """
    def __init__(self):
        super().__init__(label='Yes', style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: Interaction):
        player = interaction.client.lavalink.player_manager.get(interaction.guild_id)
        player.queue.clear()
        await interaction.response.edit_message(content='Queue Cleared!', view=None)

class PreviousButton(Button):
    """ Queue page navigation. """
    def __init__(self):
        super().__init__(label='Previous', style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: Interaction):

        await interaction.response.edit_message()

class NextButton(Button):
    """ Queue page navigation. """
    def __init__(self):
        super().__init__(label='Next', style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: Interaction):

        await interaction.response.edit_message()