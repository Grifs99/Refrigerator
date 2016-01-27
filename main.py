import logging
import asyncio
import random
import psutil
import discord
import sys
from discord.ext import commands
import os
import json
import aiohttp
import time
import re

starttime = int(time.time())
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Lods settings from JSON file
try:
    with open(os.path.abspath('settings.json'), 'r') as data:
        settings = json.load(data)
except:
    print('Couldn\'t load settings from file')
    raise

client = commands.Bot(command_prefix=settings['prefix'], description=settings['description'])


def status():
    process_id = os.getpid()
    process_mem = psutil.Process(process_id)
    mem = process_mem.memory_info()[0] / float(2 ** 20)
    status_msg = 'Memory usage: {0:.2f}MB\n'.format(mem)
    status_msg += 'Servers: {}\n'.format(len(client.servers))
    members = sum(map(lambda _: 1, client.get_all_members()))
    status_msg += 'Members: {}\n'.format(members)
    channels = sum(map(lambda _: 1, client.get_all_channels()))
    status_msg += 'Channels: {}\n'.format(channels)
    status_msg += 'Private Channels: {}\n'.format(len(client.private_channels))
    status_msg += 'Messages: {}\n'.format(len(client.messages))
    return status_msg

@client.event
async def on_ready():
    await asyncio.sleep(5)
    print(status())

@client.command(name='status',
                aliases=['usage'],
                help='Returns information about status of bot')
async def command_status():
    await client.say('```{}```'.format(status()))

@client.command(name='u',
                aliases=['urban', 'urbandic'],
                help='Returns search term from urbandictionary.com')
async def command_urbandictionary(*term):
    search_term = '+'.join(term)
    async with aiohttp.get('http://api.urbandictionary.com/v0/define?term={}'.format(search_term)) as resp:
        assert resp.status == 200
        resp_parsed = await resp.json()
        resp_msg = resp_parsed['list'][0]['definition'][:1900] if resp_parsed['list'] else 'Sorry I didn\'t find this term'
        #hard limit on msg length, could be done with fancy math. 2000 - (user_mention_string_length+ comma + one_white_space)
        await client.reply('{}'.format(resp_msg))

@client.command(name='whois',
                aliases=['user'],
                help='Returns information about user',
                pass_context=True)
async def command_whois(ctx, username: str):
    userinfo = discord.utils.get(ctx.message.server.members, name=username)
    userinfo_msg = 'Username: {}\n'.format(userinfo.name)
    userinfo_msg += 'Users ID: {}\n'.format(userinfo.id)
    userinfo_msg += 'Avatar hash: {}\n'.format(userinfo.avatar)
    await client.say('```{}```'.format(userinfo_msg))

@client.command(name='uptime',
                help='Returns uptime for bot')
async def command_uptime():
    timenow = int(time.time())
    deltatime = timenow-starttime
    days = divmod(deltatime,86400)
    hours = divmod(days[1],3600)
    minutes = divmod(hours[1],60)
    seconds = minutes[1]
    await client.say('I have been up for {[0]} days, {[0]} hours, {[0]} minutes and {} seconds'.format(days, hours, minutes, seconds))

@client.command(name='choose',
                help='Chooses between multiple choices',
                aliases=['random','rnd','rand'],
                description='For when you wanna settle the score some other way')
async def command_choose(*choices : str):
    await client.reply(random.choice(choices))

@client.command(name='setgame',
                help='Sets or updates game status for Bot',
                aliases=['playing'],
                description='When Bot is bored!')
@commands.has_permissions(manage_server=True)
async def command_setgame(*gamename: str):
    _gamename = ' '.join(gamename)
    await client.change_status(game=discord.Game(name=_gamename))

async def process_always(message):
    _twitch_re = re.compile(r'(.*:)//(twitch.tv|www.twitch.tv)(:[0-9]+)?(.*)', re.I)
    _twitch_match = _twitch_re.match(message.content)
    if _twitch_match:
        channel = _twitch_match.group(4).split('#')[0].split(' ')[0].split('/')[1]
        async with aiohttp.get('https://api.twitch.tv/kraken/streams/{}'.format(channel)) as resp:
            assert resp.status == 200
            resp_parsed = await resp.json()
            if resp_parsed['stream'] or not resp_parsed['error']:
                resp_msg = '**{}** - **{}** is playing **{}** and **{}** are watching it!'.format(
                    resp_parsed['stream']['channel']['display_name'],
                    resp_parsed['stream']['channel']['status'],
                    resp_parsed['stream']['channel']['game'],
                    resp_parsed['stream']['viewers']
                )
                await client.send_message(message.channel, '{}'.format(resp_msg))

@client.event
async def on_message(message):
    await client.process_commands(message)
    await process_always(message)

client.run(settings['email'], settings['password'])