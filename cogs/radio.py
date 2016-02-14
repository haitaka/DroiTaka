from .utils import config, checks, formats
import discord
from discord.ext import commands
import discord.utils

class Radio:
    """The radio-bot related commands."""

    def __init__(self, bot):
        self.bot = bot
        self.player = None
        if not discord.opus.is_loaded():
            discord.opus.load_opus('/usr/local/lib/libopus.so') #FreeBSD path

    @property
    def is_playing(self):
        return self.player is not None and self.player.is_playing()
    
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
        await self.stop()
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

def setup(bot):
    bot.add_cog(Radio(bot))
