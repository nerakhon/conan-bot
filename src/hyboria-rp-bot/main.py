import configparser
import asyncio
import logging

import discord
import a2s


class MyException(Exception):
    pass


class BotConfig(configparser.ConfigParser):
    def __init__(self, config_file):
        super(BotConfig, self).__init__()
        self.read(config_file)
        self.validate_config()

    def validate_config(self):
        required_values = {
            'discord': {
                'token': None,
                'channel': None,
            },
            'server': {
                'ip': None,
                'port': None,
                'name' : None,
            }
        }

        for section, keys in required_values.items():
            if section not in self:
                raise MyException(
                    'Missing section %s in the config file' % section)

        for key, values in keys.items():
            if key not in self[section] or self[section][key] == '':
                raise MyException((
                                          'Missing value for %s under section %s in ' +
                                          'the config file') % (key, section))

            if values:
                if self[section][key] not in values:
                    raise MyException((
                                              'Invalid value for %s under section %s in ' +
                                              'the config file') % (key, section))


config = {}

try:
    config = BotConfig('conan-bot.ini')
except MyException as e:
    print(e)
else:
    if config['bot'].getboolean('debug', fallback=False):
        logging.basicConfig(level=logging.DEBUG)

TOKEN = config.get('discord', 'token')
address = (config.get('server', 'ip'), config.getint('server', 'port'))
name = config.get('server', 'name')
mychannel = config.getint('discord','channel')


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
        channel = self.get_channel(mychannel)  # TODO channel ID goes here make it configurable
        while not self.is_closed():
            i = await async_a2s_info(address)
            await discord.VoiceChannel.edit(channel,
                                            name="Online Players : " + str(i.player_count) + " / " + str(i.max_players))  # TODO make this a f string
            await asyncio.sleep(60)  # task runs every 60 seconds


if __name__ == "__main__":
    client = MyClient()
    client.run(TOKEN)
