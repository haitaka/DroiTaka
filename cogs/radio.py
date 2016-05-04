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
        self.playlists = {}
        self.update_song_list()
            
    @property
    def is_playing(self):
        return self.player is not None and self.player.is_playing() and not self.stopped
        
    def toggle_next_song(self):
        if not self.stopped:
            self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    def update_song_list(self):
        self.songs = self.bot.yadisk.list_files(self.songs_dir)
        self.update_playlists()
        
    def update_playlists(self):
        pl_files = self.bot.yadisk.list_files(self.songs_dir + 'playlists/')
        for pl in pl_files:
            pl_url = self.bot.yadisk.direct_link(self.songs_dir + 'playlists/' + pl)
            pl_data = self.bot.yadisk._get(pl_url).json()['songs']
            self.playlists[pl.split('.json')[0]] = []
            for song in pl_data:
                if song in self.songs:
                    self.playlists[pl.split('.json')[0]].append(song)
    
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
        
    @commands.command(pass_context=True, aliases=['у', 'уёбывай', 'уходи'])
    async def leave(self, ctx):
        """Покинуть текущий голосовой канал."""
        await ctx.invoke(self.stop)
        await self.bot.voice.disconnect()
        await self.bot.change_status(None)
        
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
                    print('Joining {}.'.format(author_channel.name))
                    await ctx.invoke(self.join, channel_name=author_channel.name)
                else:
                    await self.bot.say('Не выбран голосовой канал.')
                    return
    
            if self.q.empty():
                await self.q.put(random.choice(self.songs))
            self.play_next_song.clear()
            self.current = await self.q.get()
            self.player = self.bot.voice.create_ffmpeg_player(
                self.bot.yadisk.direct_link(self.songs_dir + self.current),
                after=self.toggle_next_song)
                #options="-loglevel debug -report",
                #headers = dict(self.bot.pycopy.session.headers)
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
        
    @commands.command(aliases=['ss'])
    async def searchsong(self, search_word : str):
        """Искать песню по названию."""
        search_result = ""
        id = 1
        found = False
        for song in self.songs:
            if search_word.lower() in song.lower():
                found = True
                search_result += "{}. {}\n".format(id, song)
                if len(search_result) > 1800:
                    await self.bot.say(search_result)
                    search_result = ''
            id += 1
        if not found:
            search_result = "Нет такой песни."
        await self.bot.say(search_result)
        
    @commands.command()
    async def add(self, value : str):
        """Добавить в конец очереди песню или плейлист."""
        if value.strip().isdigit():
            await self.q.put(self.songs[int(value.strip())-1])
            await self.bot.say("{} добавлена в конец очереди".format(self.songs[int(value.strip())-1]))
        elif value in self.playlists:
            for song in self.playlists[value]:
                await self.q.put(song)
            await self.bot.say("Плейлист добавлен в конец очереди.")
        else:
            await self.bot.say("Нет такой песенки.")
            
    @commands.group(pass_context=True, aliases=['pl'])
    async def playlist(self, ctx):
        """Показать плейлисты."""
        if ctx.invoked_subcommand is None and len(self.playlists) > 0:
            to_print = ""
            id = 1
            for playlist in self.playlists:
                to_print += "{}. {}\n".format(id, playlist)
                id += 1
                if len(to_print) > 1800:
                    await self.bot.say(to_print)
                    to_print = ''
            await self.bot.say(to_print)
                
    
    @playlist.command(pass_context=True, name='add')
    async def pl_add(self, ctx, *args):
        """Добавить песенки в плейлист.
        
        !playlist add {song} {song} ... {playlist}
        """
        to_add = []
        for arg in args:
            if arg.strip().isdigit():
                if int(arg) in range(1, len(self.songs) + 1):
                    song_name = self.songs[int(arg)-1]
                    to_add.append(song_name)
            elif arg in self.playlists:
                self.playlists[arg] += to_add
                pl_json = {'name': arg, 'songs': self.playlists[arg]}
                self.bot.yadisk.upload(self.songs_dir + 'playlists/' + arg + '.json', json.dumps(pl_json))
                await self.bot.say('Плейлист {} обновлён.'.format(arg))
                to_add = []
                
    @playlist.command(name = 'new')
    async def pl_new(self, name : str):
        """Создать новый плейлист. 
        (Имя не должно содержать пробелов. Имя не может быть числом.)
        """
        name = name.strip().split(' ')[0]
        self.playlists[name] = []
        await self.bot.say('Плейлист {} создан.'.format(name))
        
    @playlist.command(name = 'show')
    async def pl_show(self, name : str):
        """Показать плейлист."""
        name = name.strip().split(' ')[0]
        if name in self.playlists:
            song_list = ""
            for song in self.playlists[name]:
                try:
                    id = self.songs.index(song) + 1
                except:
                    await self.bot.say('Плейлист {} повреждён.'.format(name))
                song_list += "{}. {}\n".format(id, song)
                if len(song_list) > 1800:
                    await self.bot.say(song_list)
                    song_list = ''
            await self.bot.say(song_list)
        else:
            await self.bot.say('Нет такого плейлиста.')
           
            
    @commands.command(pass_context=True)
    async def playvk(self, ctx, url : str):
        """Начать воспроизведение аудио со страницы группы 
        или пользователя vk.com."""
        if self.player is not None and not self.stopped:
            await self.bot.say('Уже играю песенку.')
            return
            
        queue = self.bot.vkaudio.get_by_url(url)
        for song in queue:
            if not self.bot.is_voice_connected():
                author_channel = ctx.message.author.voice_channel
                if author_channel is not None:
                    print('Joining {}.'.format(author_channel.name))
                    await ctx.invoke(self.join, channel_name=author_channel.name)
                else:
                    await self.bot.say('Не выбран голосовой канал.')
                    return
                
            print(song)
            self.play_next_song.clear()
            self.player = self.bot.voice.create_ffmpeg_player(song['url'], after=self.toggle_next_song)
            self.stopped = False
            self.player.start()
            song_name = song["artist"] + " " + song["title"]
            await self.bot.change_status(discord.Game(name=song_name))
            
            await self.play_next_song.wait()
            if self.break_loop.is_set():
                self.break_loop.clear()
                return
        await self.bot.say('Leaving play loop')
        
def setup(bot):
    bot.add_cog(Radio(bot))
