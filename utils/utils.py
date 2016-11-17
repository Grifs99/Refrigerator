import re
import aiohttp
import time

import datetime
import discord
from isodate import parse_duration

async def process_always( message, settings, client):
    _twitch_re = re.compile(r'(.*:)//(twitch.tv|www.twitch.tv)(:[0-9]+)?(.*)', re.I)
    _youtube_re = re.compile(r'(?:youtube.*?(?:v=|/v/)|youtu\.be/|yooouuutuuube.*?id=)([-_a-zA-Z0-9]+)', re.I)
    _youtube_match = _youtube_re.search(message.content)
    _twitch_match = _twitch_re.match(message.content)
    if _twitch_match:
        channel = _twitch_match.group(4).split('#')[0].split(' ')[0].split('/')[1]
        async with aiohttp.get('https://api.twitch.tv/kraken/streams/{}'.format(channel)) as resp:
            assert resp.status == 200
            resp_parsed = await resp.json()
            if resp_parsed['stream']:
                resp_msg = '**{}** - **{}** is playing **{}** and **{}** are watching it!'.format(
                    resp_parsed['stream']['channel']['display_name'],
                    resp_parsed['stream']['channel']['status'],
                    resp_parsed['stream']['channel']['game'],
                    resp_parsed['stream']['viewers']
                )
                await client.send_message(message.channel, str(resp_msg))
            elif not resp_parsed['stream']:
                await client.send_message(message.channel,
                                               '**{}** channel at the moment is offline'.format(channel))
    elif _youtube_match:
        _id = _youtube_match.group(1)
        session = aiohttp.ClientSession()
        async with session.get(
                'https://www.googleapis.com/youtube/v3/videos?part=contentDetails%2C+snippet%2C+statistics&id={}&key={}'.format(
                        _id, settings['youtube_api_key'])) as resp:
            assert resp.status == 200
            resp_parsed = await resp.json()
            if resp_parsed.get('error'):
                if resp_parsed['error']['code'] == 403:
                    await client.send_message(message.channel, 'Failed to fetch content from youtube :(')
                else:
                    pass
            items = resp_parsed['items'][0]
            snippet = items['snippet']
            statistics = items['statistics']
            content_details = items['contentDetails']
            title = snippet['title']
            length = parse_duration(content_details['duration'])
            intervals = (
                ('w', 604800),  # 60 * 60 * 24 * 7
                ('d', 86400),  # 60 * 60 * 24
                ('h', 3600),  # 60 * 60
                ('m', 60),
                ('s', 1),
            )
            def display_time(seconds, granularity=2):
                result = []
                for name, count in intervals:
                    value = seconds // count
                    if value:
                        seconds -= value * count
                        result.append("{:.0f} {}".format(value, name))
                return ' '.join(result[:granularity])
            likes = float(statistics['likeCount'])
            dislikes = float(statistics['dislikeCount'])
            total_votes = likes + dislikes
            total_percent = 100 * (likes / total_votes)
            views = statistics['viewCount']
            author = snippet['channelTitle']
            upload_time = time.strptime(snippet['publishedAt'], "%Y-%m-%dT%H:%M:%S.000Z")
            await client.send_message(message.channel,
                                           '**{}** – length **{}** – likes **{}**, dislikes **{}** (**{:.1f}%**) – **{}** views – **{}** on **{}**'.format(
                                               title,
                                               display_time(length.total_seconds(), 4),
                                               likes,
                                               dislikes,
                                               total_percent,
                                               views,
                                               author,
                                               time.strftime("%Y.%m.%d", upload_time)
                                           ))
            channel = discord.utils.get(client.get_all_channels(), name='youtubestuff')
            if message.channel.id != channel.id:
                await client.send_message(channel, 'https://{}'.format(_youtube_match.group(0)))
