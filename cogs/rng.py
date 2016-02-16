from discord.ext import commands
import random as rng
import copy


class RNG:
    """Utilities that provide pseudo-RNG."""

    el_fractions=['ходоки', 'лорды', 'некрофаги', 'маги', 'хуители']

    def __init__(self, bot):
        self.bot = bot
        self.el_pull = copy.copy(RNG.el_fractions)

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

    @commands.group(pass_context=True, aliases=['ел'])
    async def el(self, ctx):
        """Выбор фракции в Endless Legend."""
        str_answer = ''
        for fract in self.el_pull:
            str_answer += '{}\n'.format(fract)
        await self.bot.say(str_answer)

    @el.command(pass_context=True, aliases=['репул'])
    async def repull(self, ctx):
        self.el_pull = copy.copy(RNG.el_fractions)
        ctx.invoke(self.el)

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
