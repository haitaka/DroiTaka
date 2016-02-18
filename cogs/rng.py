from discord.ext import commands
from difflib import SequenceMatcher
import random as rng
import copy

class RNG:
    """Utilities that provide pseudo-RNG."""

    el_fractions = [['Дикие Ходоки', 'ходоки', 'ходукены', 'Wild Walkers'],
                    ['Владыки праха', 'Сломленные Лорды', 'Broken Lords'],
                    ['Хранители', 'Vaulters'],
                    ['Некрофаги', 'Necrophages'],
                    ['Неистовые маги', 'Ярые Маги', 'они слабы', 'Ardent Mages'],
                    ['Кочующие Кланы', 'кочевники', 'Roving Clans'],
                    ['Драккены', 'Drakken'],
                    ['Культисты', 'Cultists'],
                    ['Забытые', 'Тени', 'Forgotten']]

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

    def sample(self, seq, length, uniq=True):
        if uniq:
            return rng.sample(seq, length)
        else:
            result = []
            for i in range(length):
                result.append(rng.choice(seq))
            return result
            
    def similar(self, a, b):
        return SequenceMatcher(None, a, b).ratio()
        
    async def print_pull(self, pull):
        str_answer = ''
        for idx, fract in enumerate(pull, 1):
            str_answer += '{}. {}\n'.format(idx, fract[0])
        await self.bot.say(str_answer)
        
    @commands.group(pass_context=True, aliases=['ел'])
    async def el(self, ctx, *args):
        """Выбор фракции в Endless Legend.
        
        !el вывести список фракций
        !el {n} выбрать *n* случайных фракций
        !el uniq {n} выбрать *n* случайных фракций без повторений
        !el {fract} исключить *fract* из списка
        """
        
        uniq = False
        isroll = False
            
        for arg in args:
            if arg.strip().isdigit():
                if int(arg) in range(1, 9):
                    choice = self.sample(self.el_pull, int(arg), uniq)
                    await self.print_pull(choice)
                uniq = False
                isroll = True
            elif arg in ['uniq', 'uni', 'уни', 'уникал', 'уник']:
                uniq = True
            elif arg in ['repull', 'репул', 'репулл', 'ресет']:
                self.el_pull = copy.copy(RNG.el_fractions)
            else:
                match = None
                maxratio = 0
                for fract in RNG.el_fractions:
                    for alias in fract:
                        ratio = self.similar(arg, alias)
                        if ratio > maxratio:
                            match = fract
                            maxratio = ratio
                if match in self.el_pull:
                    await self.bot.say('{} удалены из списка.'.format(match[0]))
                    self.el_pull.remove(match)
                    
        if not isroll:
            await self.print_pull(self.el_pull)
        
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
