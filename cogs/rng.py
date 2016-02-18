from discord.ext import commands
import random as rng
import copy

class RNG:
    """Utilities that provide pseudo-RNG."""

    el_fractions=['ходоки', 'лорды', 'некрофаги', 'маги', 'хранители', 'драккны', 'забитые', 'кланы']

    def __init__(self, bot):
        self.bot = bot
        self.el_pull = copy.copy(RNG.el_fractions)
        self.ban.aliases += RNG.el_fractions
        self.ban.aliases.append('test')
    @commands.command()
    async def random(self, minimum=0, maximum=100):
        """Выбрать случайное число в заданном диапазоне.
        Минимум должен быть меньше максимума, а максимум — меньше 1000.
        """

        maximum = min(maximum, 1000)
        if minimum >= maximum:
            await self.bot.say('Максимум меньше минимума.')
            return

        await self.bot.say(rng.randint(minimum, maximum))

    #@random.command()
    #async def lenny(self):
    #    """Displays a random lenny face."""
    #    lenny = rng.choice([
    #        "( ͡° ͜ʖ ͡°)", "( ͠° ͟ʖ ͡°)", "ᕦ( ͡° ͜ʖ ͡°)ᕤ", "( ͡~ ͜ʖ ͡°)",
    #        "( ͡o ͜ʖ ͡o)", "͡(° ͜ʖ ͡ -)", "( ͡͡ ° ͜ ʖ ͡ °)﻿", "(ง ͠° ͟ل͜ ͡°)ง",
    #        "ヽ༼ຈل͜ຈ༽ﾉ"
    #    ])
    #    await self.bot.say(lenny)

    async def print_pull(self, pull):
        str_answer = ''
        for idx, fract in enumerate(pull, 1):
            str_answer += '{}. {}\n'.format(idx, fract)
        await self.bot.say(str_answer)
        
    @commands.group(pass_context=True, aliases=['ел'])
    async def el(self, ctx):
        """Выбор фракции в Endless Legend.
        
        Здесь был Vinyl.
        """
        if ctx.invoked_subcommand is None:
            await self.print_pull(self.el_pull)

    @el.command(pass_context=True, aliases=['репул', 'репулл'])
    async def repull(self, ctx):
        """Восстановить список."""
        self.el_pull = copy.copy(RNG.el_fractions)
        await self.print_pull(self.el_pull)

    @el.command(pass_context=True, aliases=copy.copy(el_fractions), hidden=True)
    async def ban(self, ctx, *fractions):
        """Исключить фракцию из списка."""
        for fract in fractions:
            if fract in self.el_pull:
                await self.bot.say(fract)
                self.el_pull.remove(fract)
        await self.bot.say(ctx.invoked_with)
        if ctx.invoked_with in self.el_pull:
            self.el_pull.remove(ctx.invoked_with)
            await self.print_pull(self.el_pull)
        else:
            await self.bot.say('Нет такой фракции.')
    
    @el.command(pass_context=True, aliases=['ролл', 'выбор'])
    async def roll(self, ctx, *, count : int = 0):
        """Выбрать *count* случайных фракций."""
        choice = rng.sample(self.el_pull, count)
        await self.print_pull(choice)
        
    @commands.command(aliases=['выбери', 'вибери'])
    async def choose(self, *, choices : str):
        """Есть два стула...
        Варианты должны быть разделены с помощью `or` или `или`
        """
        choices_list = list()
        for choice in choices.split('or'):
            choices_list += choice.split('или')
            
        if len(choices_list) < 2:
            await self.bot.say('Шо то хуйня, шо это хуйня.')
        else:
            await self.bot.say(rng.choice(choices_list).lstrip())

def setup(bot):
    bot.add_cog(RNG(bot))
