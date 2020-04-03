import asyncio
import logging

import discord
import a2s

from .config import MyException, BotConfig

config = {}

try:
    config = BotConfig('conan-bot.ini')
except MyException as e:
    print(e)
    exit(1)
else:
    if config['bot'].getboolean('debug', fallback=False):
        logging.basicConfig(level=logging.DEBUG)

TOKEN = config.get('discord', 'token')
address = (config.get('server', 'ip'), config.getint('server', 'port'))
name = config.get('server', 'name')
mychannel = config.getint('discord', 'channel')


async def async_a2s_info(addr):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, a2s.info, addr)


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.my_background_task())

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        activity = discord.Activity(name=name, type=discord.ActivityType.watching)
        await client.change_presence(activity=activity)

    async def my_background_task(self):
        await self.wait_until_ready()
        channel = self.get_channel(mychannel)
        while not self.is_closed():
            i = await async_a2s_info(address)
            await discord.VoiceChannel.edit(channel, name=f"Online Players : {i.player_count} / {i.max_players}")
            await asyncio.sleep(60)  # task runs every 60 seconds


if __name__ == "__main__":
    client = MyClient()
    client.run(TOKEN)
