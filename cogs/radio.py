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
        """Зайти на указанный голосовой канал."""
        if channel is None or channel.type is not discord.ChannelType.voice:
            await self.bot.say('Нет такого голосового канала.')
            return
        await self.bot.join_voice_channel(channel)
        
    @commands.command(pass_context=True)
    async def leave(self, ctx):
        """Покинуть текущий голосовой каналю"""
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
            song_name = unquote(self.current.split('/')[-1])
            await self.bot.change_status(discord.Game(name=song_name))
            
            await self.play_next_song.wait()
            
    @commands.command(aliases=['c'])
    async def current(self):
        """Что там на радио?"""
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
