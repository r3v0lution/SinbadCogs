import pathlib
import logging

import discord
from discord.ext import commands
from redbot.core.config import Config
from redbot.core import RedContext
from redbot.core.bot import Red
from redbot.core.i18n import CogI18n
from redbot.core.utils.data_converter import DataConverter as dc

from .antispam import AntiSpam

_ = CogI18n('AutoRooms', __file__)
log = logging.getLogger('red.sinbadcogs.autorooms')


class AutoRooms:
    """
    Automatic Rooms
    """

    default_guild = {
        'active': False,
        'channels': [],
        'ownership': True,
        'tempcache': []
    }

    default_channel = {
        'ownership': None,
        'gamedetect': False
    }

    def __init__(self, bot: Red):
        self.bot = bot
        self.antispam = {}
        self.config = Config.get_conf(
            self, identifier=78631113035100160,
            force_registration=True
        )

        self.config.register_channel(**self.default_channel)
        self.config.register_guild(**self.default_guild)
        self.bot.loop.create_task(self.cleanup(check_all=True))

    async def cleanup(self, *, check_all: bool=False,
                      guild: discord.Guild=None):
        """
        guild, or being told to check all
        """

        if check_all:
            for g in self.bot.guilds:
                await self.clean_guild(g)
        elif guild:
            await self.clean_guild(guild)

    async def clean_guild(self, guild: discord.Guild):
        """
        cleans up unused autorooms in a guild
        """
        if not guild.me.guild_permissions.manage_channels:
            await self.config.guild(guild).active.set(False)
            log.debug(
                "Disabling autorooms due to permission error in "
                "guild with ID: {}".format(guild.id)
            )
            return False

        async with self.config.guild(guild).tempcache() as temps:
            for c in guild.voice_channels:
                if c.id in temps and len(c.members) == 0:
                    try:
                        await c.delete()
                    except discord.HTTPException as e:
                        log.exception(e)
                    except discord.Forbidden as e:
                        log.error(
                            "How could this happen to me...." + str(e)
                        )

            # NOTE: I'd love to use the below, but config's async context
            # manager won't let me. When exclusive access outside of context
            # managers are available, I'll modify this to use the below:

            # temps = [
            #     x for x in temps if x in [
            #         c.id for c in guild.voice_channels
            #     ]
            # ]

            [
                temps.remove(x) for x in [
                    i for i in temps if i not in [
                        c.id for c in guild.voice_channels
                    ]
                ]
            ]