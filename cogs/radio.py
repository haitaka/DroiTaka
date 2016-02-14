from .utils import config, checks, formats
import discord
from discord.ext import commands
import discord.utils
from .utils.api.pycopy import Copy
import random, json, asyncio
from urllib.parse import unquote

class Radio:
    """The radio-bot related commands."""

    def __init__(self, bot):
        self.bot = bot
        if not discord.opus.is_loaded():
            discord.opus.load_opus('/usr/local/lib/libopus.so') #FreeBSD path
            
        self.player = None
        self.stopped = True
        self.q = asyncio.Queue()
        self.play_next_song = asyncio.Event()
        self.current_song = None
        copy_creds = self.load_copy_creds()
        self.copycom = Copy(copy_creds['login'], copy_creds['passwd'])
        self.songs = []
        self.update_song_list()

    def load_copy_creds(self):
        with open('copy_creds.json') as f:
            return json.load(f)
            
    @property
    def is_playing(self):
        return self.player is not None and self.player.is_playing() and not self.stopped
        
    def toggle_next_song(self):
        if not self.stopped:
            self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    def update_song_list(self):
        self.songs = self.copycom.list_files('radio/')
    
    
    @commands.command()
    async def join(self, *, channel : discord.Channel = None):
        """Join voice channel.
        """
        if channel is None or channel.type is not discord.ChannelType.voice:
            await self.bot.say('Cannot find a voice channel by that name. {0}'.format(channel.type))
            return
        await self.bot.join_voice_channel(channel)
        
    @commands.command(pass_context=True)
    async def leave(self, ctx):
        """Leave voice channel.
        """
        await ctx.invoke(self.stop)
        await self.bot.voice.disconnect()
        
    @commands.command()
    async def pause(self):
        """Pause.
        """
        if self.player is not None:
            self.player.pause()
            
    @commands.command()
    async def resume(self):
        """Resume playing.
        """
        if self.player is not None and not self.is_playing:
            self.player.resume()
            
    @commands.command()
    async def skip(self):
        """Skip song and play next.
        """
        if self.player is not None and self.is_playing:
            self.player.stop()
            self.toggle_next_song()
            
    @commands.command()
    async def stop(self):
        """Stop playing song.
        """
        if self.is_playing:
            self.stopped = True
            self.player.stop()

    @commands.command(pass_context=True)
    async def play(self, ctx):
        """Start playing song from queue.
        """
        if self.player is not None and not self.stopped:
            if not self.is_playing:
                await ctx.invoke(self.resume)
                return
            else:
                await self.bot.say('Already playing a song')
                return
            
        while True:
            if not self.bot.is_voice_connected():
                await ctx.invoke(self.join, channel=ctx.message.author.voice_channel)
                continue
    
            if self.q.empty():
                await self.q.put(random.choice(self.songs))
            self.play_next_song.clear()
            self.current = await self.q.get()
            self.player = self.bot.voice.create_ffmpeg_player(
                self.copycom.direct_link('radio/' + self.current),
                after=self.toggle_next_song,
                #options="-loglevel debug -report",
                headers = dict(self.copycom.session.headers))
            self.stopped = False
            self.player.start()
            fmt = 'Playing song "{0}"'
            song_name = unquote(self.current.split('/')[-1])
            await self.bot.say(fmt.format(song_name))
            await self.bot.change_status(discord.Game(name=song_name))
            
            await self.play_next_song.wait()
            
def setup(bot):
    bot.add_cog(Radio(bot))
