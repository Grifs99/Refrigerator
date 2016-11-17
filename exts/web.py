import aiohttp
from discord.ext import commands


class Web:
    def __init__(self, client):
        self.client = client

    @commands.command(name='u',
                      help='Returns search term from urbandictionary.com')
    async def urban(self, *, search_term):
        search_term = aiohttp.helpers.requote_uri(search_term)
        session = aiohttp.ClientSession()
        async with session.get('http://api.urbandictionary.com/v0/define?term={}'.format(search_term)) as resp:
            assert resp.status == 200
            resp_parsed = await resp.json()
            resp_msg = resp_parsed['list'][0]['definition'][:1900] if resp_parsed['list'] else 'Something went wrong \U0001F641'
            await self.client.reply('{}'.format(resp_msg))


def setup(client):
    client.add_cog(Web(client))
