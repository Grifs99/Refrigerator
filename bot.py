import datetime
import discord
from discord.ext import commands
import os
import json
import sys
import logging
import asyncio
import psutil
from utils.utils import process_always

description = 'Dank bot!'

client = commands.Bot(command_prefix='.', description=description)

discord_logger = logging.getLogger('discord')
discord_logger.setLevel(logging.CRITICAL)
log = logging.getLogger()
log.setLevel(logging.INFO)
handler = logging.FileHandler(filename='bot.log', encoding='utf-8', mode='w')
log.addHandler(handler)

'''
Extensions that will be loaded on start
'''
exts = [
    'exts.utils',
    'exts.web'
]


def load_settings():
    with open(os.path.abspath('settings.json'), 'r') as data:
        return json.load(data)


@client.event
async def on_ready():
    await asyncio.sleep(1)
    if not hasattr(client, 'uptime'):
        client.uptime = datetime.datetime.utcnow()
    process_id = os.getpid()
    process_mem = psutil.Process(process_id)
    mem = process_mem.memory_info()[0] / float(2 ** 20)
    status_msg = 'Servers: {}\n'.format(len(client.servers))
    status_msg += 'Memory usage: {0:.2f}MB\n'.format(mem)
    members = sum(map(lambda _: 1, client.get_all_members()))
    status_msg += 'Members: {}\n'.format(members)
    channels = sum(map(lambda _: 1, client.get_all_channels()))
    status_msg += 'Channels: {}\n'.format(channels)
    status_msg += 'Private Channels: {}\n'.format(len(client.private_channels))
    status_msg += 'Messages: {}\n'.format(len(client.messages))
    print(status_msg)


@client.event
async def on_message(message):
    await client.process_commands(message)
    await process_always(message, settings, client)


if __name__ == '__main__':
    if any('debug' in arg.lower() for arg in sys.argv):
        client.command_prefix = '!'
    settings = load_settings()


    for extension in exts:
        try:
            client.load_extension(extension)
            print('Loaded {}'.format(extension))
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))

    client.run(settings['token'])
