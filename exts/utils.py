import datetime
import random
from discord import Game
from discord.ext import commands
import os
import psutil


class Utils:
    def __init__(self, client):
        self.client = client

    def get_uptime(self):
        now = datetime.datetime.utcnow()
        delta = now - self.client.uptime
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        if days:
            fmt = '{d} days, {h} hours, {m} minutes, and {s} seconds'
        else:
            fmt = '{h} hours, {m} minutes, and {s} seconds'

        return fmt.format(d=days, h=hours, m=minutes, s=seconds)

    @commands.command()
    async def status(self):
        process_id = os.getpid()
        process_mem = psutil.Process(process_id)
        mem = process_mem.memory_info()[0] / float(2 ** 20)
        status_msg = 'Servers: {}\n'.format(len(self.client.servers))
        status_msg += 'Memory usage: {0:.2f}MB\n'.format(mem)
        members = sum(map(lambda _: 1, self.client.get_all_members()))
        status_msg += 'Members: {}\n'.format(members)
        channels = sum(map(lambda _: 1, self.client.get_all_channels()))
        status_msg += 'Channels: {}\n'.format(channels)
        status_msg += 'Private Channels: {}\n'.format(len(self.client.private_channels))
        status_msg += 'Messages: {}\n'.format(len(self.client.messages))
        status_msg += 'Uptime: {}\n'.format(self.get_uptime())
        await self.client.say('```{}```'.format(status_msg))

    @commands.command()
    async def uptime(self):
        await self.client.say('```{}```'.format(self.get_uptime()))

    @commands.command(help='Sets or updates game status for Bot',
                        description='When Bot is bored!')
    @commands.has_permissions(manage_server=True)
    async def setgame(self, *, gamename: str):
        await self.client.change_presence(game=Game(name=gamename))

    @commands.command(help='Chooses between multiple choices',
                    description='For when you wanna settle the score some other way')
    async def choose(self, *choices: str):
        await self.client.reply(random.choice(choices))


def setup(client):
    client.add_cog(Utils(client))