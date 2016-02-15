from discord.ext import commands

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
            self.pic_list.append(file_name.split('.')[0])
        self.pic.aliases = ['test']
    
    @commands.group(pass_context=True, aliases=[])
    async def pic(self, ctx):
        """База картинок, мемесов etc."""
        if ctx.invoked_with in self.pic_list:
            await self.bot.say(ctx.invoked_with)
        elif ctx.invoked_subcommand is None:
            await ctx.invoke(commands.help.pic)
        
    @pic.command()
    async def update(self):
        """Обновить список картиночек."""
        self.update_pics()
        await self.bot.say("Найдено {} картиночек.".format(len(self.pic_list)))
        
    @pic.command()
    async def list(self):
        """ВЫвести список картиночек."""
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
