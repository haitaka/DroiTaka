from .utils import config, checks, formats
import discord
from discord.ext import commands
import discord.utils
from .utils.api.pycopy import Copy
import random, json

class Radio:
    """The radio-bot related commands."""

    def __init__(self, bot):
        self.bot = bot
        self.player = None
        self.stopped = True
        self.q = asyncio.Queue()
        self.play_next_song = asyncio.Event()
        self.current_song = None
        copy_creds = self.load_copy_creds()
        self.copycom = Copy(copy_creds['login'], copy_creds['passwd'])
        self.songs = []
        self.update_song_list()
        if not discord.opus.is_loaded():
            discord.opus.load_opus('/usr/local/lib/libopus.so') #FreeBSD path

    def load_copy_creds():
        with open('../copy_creds.json') as f:
            return json.load(f)
            
    @property
    def is_playing(self):
        return self.player is not None and self.player.is_playing() and not self.stopped
        
    def toggle_next_song(self):
        if not self.stopped:
            self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    def update_song_list(self):
        self.files = self.copycom.list_files(settings.copy_radio_path)
    
    
    @commands.command()
    async def join(self, *, channel : discord.Channel = None):
        """Join voice channel.
        """
        if channel is None or channel != discord.ChannelType.voice:
            await self.bot.say('Cannot find a voice channel by that name.')
        await self.bot.join_voice_channel(channel)
        
    @commands.command()
    async def leave(self):
        """Leave voice channel.
        """
        await self.stop().invoke(ctx)
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
        if self.player is not None and not self.is_playing():
            self.player.resume()
            
    @commands.command()
    async def skip(self):
        """Skip song and play next.
        """
        if self.player is not None and self.is_playing():
            self.player.stop()
            self.toggle_next_song()
            
    @commands.command()
    async def stop():
        """Stop playing song.
        """
        if self.is_playing():
            self.stopped = True
            self.player.stop()

    @commands.command(pass_context=True)
    async def play(self, ctx):
        """Start playing song from queue.
        """
        if self.player is not None:
            if not self.is_playing():
                await self.resume().invoke(ctx)
                return
            else:
                await self.bot.say('Already playing a song')
                return
            
        while True:
            if not selfbot.is_voice_connected():
                await self.join(channel=ctx.message.author.voice_channel).invoke(ctx)
                continue
    
            if self.q.empty():
                await self.q.put(random.choice(self.songs))
            self.play_next_song.clear()
            self.current = await self.q.get()
            self.player = self.bot.voice.create_ffmpeg_player(
                self.copycom.direct_link(settings.copy_radio_path + self.current),
                after=self.toggle_next_song,
                #options="-loglevel debug -report",
                headers = dict(self.copycom.session.headers))
            self.stopped = False
            self.player.start()
            fmt = 'Playing song "{0}"'
            song_name = unquote(self.current.split('/')[-1])
            await bot.say(fmt.format(song_name))
            self.bot.change_status(discord.Game(name=song_name))
            
            await self.play_next_song.wait()
            
def setup(bot):
    bot.add_cog(Radio(bot))
