from .utils import config, checks, formats
import discord
from discord.ext import commands
import discord.utils
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
        self.break_loop = asyncio.Event()
        #self.break_loop.clear()
        self.q = asyncio.Queue()
        self.play_next_song = asyncio.Event()
        self.current_song = None
        self.songs_dir = 'radio/'
        self.songs = []
        self.update_song_list()
            
    @property
    def is_playing(self):
        return self.player is not None and self.player.is_playing() and not self.stopped
        
    def toggle_next_song(self):
        if not self.stopped:
            self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    def update_song_list(self):
        self.songs = self.bot.pycopy.list_files(self.songs_dir)
    
    
    @commands.command(pass_context=True)
    async def join(self, ctx, *, channel_name : str):
        """Зайти на указанный голосовой канал."""
        if self.bot.is_voice_connected():
            await ctx.invoke(self.leave)
            
        check = lambda c: c.name == channel_name and c.type == discord.ChannelType.voice
        channel = discord.utils.find(check, ctx.message.server.channels)
        if channel is None:
            await self.bot.say('Нет такого голосового канала.')
        await self.bot.join_voice_channel(channel)
        
    @commands.command(pass_context=True)
    async def leave(self, ctx):
        """Покинуть текущий голосовой канал."""
        await ctx.invoke(self.stop)
        await self.bot.voice.disconnect()
        
    @commands.command()
    async def pause(self):
        """Приостановить воспроизведение."""
        if self.player is not None:
            self.player.pause()
            
    @commands.command()
    async def resume(self):
        """Продолжить воспроизведение."""
        if self.player is not None and not self.is_playing:
            self.player.resume()
            
    @commands.command()
    async def skip(self):
        """Перейти к следующей песне в очереди."""
        if self.player is not None and self.is_playing:
            self.player.stop()
            self.toggle_next_song()
            
    @commands.command()
    async def stop(self):
        """Остановить воспроизведение."""
        if self.is_playing:
            self.break_loop.set()
            self.play_next_song.set()
            self.stopped = True
            self.player.stop()

    @commands.command(pass_context=True)
    async def play(self, ctx):
        """Начать воспроизведение песен из очереди."""
        if self.player is not None and not self.stopped:
            if not self.is_playing:
                await ctx.invoke(self.resume)
                return
            else:
                await self.bot.say('Уже играю песенку.')
                return
            
        while True:
            if not self.bot.is_voice_connected():
                author_channel = ctx.message.author.voice_channel
                if author_channel is not None:
                    await self.bot.say('Залетаю на {}.'.format(author_channel.name))
                    await ctx.invoke(self.join, channel_name=author_channel.name)
                else:
                    await self.bot.say('Не выбран голосовой канал.')
                    return
    
            if self.q.empty():
                await self.q.put(random.choice(self.songs))
            self.play_next_song.clear()
            self.current = await self.q.get()
            self.player = self.bot.voice.create_ffmpeg_player(
                self.bot.pycopy.direct_link(self.songs_dir + self.current),
                after=self.toggle_next_song,
                options="-loglevel debug -report",
                headers = dict(self.bot.pycopy.session.headers))
            self.stopped = False
            self.player.start()
            song_name = unquote(self.current.split('/')[-1])
            await self.bot.change_status(discord.Game(name=song_name))
            
            await self.play_next_song.wait()
            if self.break_loop.is_set():
                self.break_loop.clear()
                return
        await self.bot.say('Leaving play loop')
            
    @commands.command(aliases=['c'])
    async def current(self):
        """Что там играет?"""
        if self.is_playing:
            song_name = unquote(self.current.split('/')[-1])
            await self.bot.say(song_name)
        
    @commands.command()
    async def update(self):
        """Обновить список песен."""
        self.update_song_list()
        await self.bot.say("Найдено {} песенок".format(len(self.songs)))
    
    @commands.command()
    async def list(self):
        """Вывести список всех доступных песен."""
        song_list = ""
        id = 1
        for song in self.songs:
            song_list += "{}. {}\n".format(id, song)
            id += 1
            if len(song_list) > 1800:
                await self.bot.say(song_list)
                song_list = ''
        await self.bot.say(song_list)
        
    @commands.command()
    async def add(self, song_num : int):
        """Добавить в конец очереди песню с данным номером."""
        await self.q.put(self.songs[song_num-1])
        await self.bot.say("{} будет следующей песенкой".format(self.songs[song_num-1]))
            
def setup(bot):
    bot.add_cog(Radio(bot))
