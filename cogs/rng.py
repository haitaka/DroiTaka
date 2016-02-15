from discord.ext import commands
import random as rng


class RNG:
    """Utilities that provide pseudo-RNG."""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True)
    async def random(self, ctx):
        """Генератор случайностей."""
        if ctx.invoked_subcommand is None:
            await self.bot.say('Incorrect random subcommand passed.')
        
    @random.command()
    async def number(self, minimum=0, maximum=100):
        """Выбрать случайное число в заданном диапазоне.

        Минимум должен быть меньше максимума, а максимум — меньше 1000.
        """

        maximum = min(maximum, 1000)
        if minimum >= maximum:
            await self.bot.say('Максимум меньше минимума.')
            return

        await self.bot.say(rng.randint(minimum, maximum))

    @random.command()
    async def lenny(self):
        """Displays a random lenny face."""
        lenny = rng.choice([
            "( ͡° ͜ʖ ͡°)", "( ͠° ͟ʖ ͡°)", "ᕦ( ͡° ͜ʖ ͡°)ᕤ", "( ͡~ ͜ʖ ͡°)",
            "( ͡o ͜ʖ ͡o)", "͡(° ͜ʖ ͡ -)", "( ͡͡ ° ͜ ʖ ͡ °)﻿", "(ง ͠° ͟ل͜ ͡°)ง",
            "ヽ༼ຈل͜ຈ༽ﾉ"
        ])
        await self.bot.say(lenny)

    @commands.command(aliases=['выбери', 'вибери'])
    async def choose(self, choices : str):
        """Есть два стула...

        Варианты должны быть разделены с помощью `or` или `или`
        """
        choices_list = list()
        for choice in choices.split('or'):
            choices_list += choice.split('или')
            
        print(choices_list)
        if len(choices_list) < 2:
            await self.bot.say('Шо то хуйня, шо это хуйня.')
        else:
            await self.bot.say(rng.choice(choices_list))

def setup(bot):
    bot.add_cog(RNG(bot))
