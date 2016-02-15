from discord.ext import commands
import copy
import requests

class Pic:
    """Мемасики и просто картинки."""

    def __init__(self, bot):
        self.bot = bot
        self.pic_dir = 'pictures/'
        self.pic_list = []
        self.update_pics()
        
    def update_pics(self):
        file_list = self.bot.pycopy.list_files(self.pic_dir)
        for file_name in file_list:
            self.pic_list[file_name.split('.')[0]] = file_name
        self.pic.aliases = list(self.pic_list.values())
    
    @commands.group(pass_context=True, aliases=[])
    async def pic(self, ctx):
        """База картинок, мемесов etc."""
        if ctx.invoked_with in self.pic_list:
            url = self.bot.pycopy.direct_link(self.pic_path + self.pic_list[ctx.invoked_with])
            r = requests.get(url, stream=True)
            if r.status_code == 200:
                r.raw.decode_content = True
                await self.bot.upload(r.raw, self.pic_list[ctx.invoked_with])
        elif ctx.invoked_subcommand is None:
            msg = copy.copy(ctx.message)
            msg.content = ctx.prefix + 'help pic'
            await self.bot.process_commands(msg)
        
    @pic.command()
    async def update(self):
        """Обновить список картиночек."""
        self.update_pics()
        await self.bot.say("Найдено {} картиночек.".format(len(self.pic_list)))
        
    @pic.command()
    async def list(self):
        """Вывести список картиночек."""
        pic_list = ''
        id = 1
        for pic in self.pic_list:
            pic_list += "{}. {}\n".format(id, pic)
            id += 1
            if len(pic_list) > 1800:
                await self.bot.say(pic_list)
                pic_list = ''
        await self.bot.say(pic_list)
        
        
def setup(bot):
    bot.add_cog(Pic(bot))
