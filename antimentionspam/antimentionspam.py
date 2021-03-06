import discord
from discord.ext import commands
import pathlib
from cogs.utils.dataIO import dataIO
from .utils import checks

path = 'data/antimentionspam'


class AntiMentionSpam:
    """removes mass mention spam"""

    __author__ = "mikeshardmind (Sinbad#0001)"
    __version__ = "2.1.0"

    def __init__(self, bot):
        self.bot = bot
        try:
            self.settings = dataIO.load_json(path + '/settings.json')
        except Exception:
            self.settings = {}

    def save_json(self):
        dataIO.save_json(path + '/settings.json', self.settings)

    @commands.group(name="antimentionspam",
                    pass_context=True, no_pm=True)
    async def antimentionspam(self, ctx):
        """configuration settings for anti mention spam"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @checks.admin_or_permissions(Manage_server=True)
    @antimentionspam.command(name="max", pass_context=True, no_pm=True)
    async def set_max_mentions(self, ctx, m):
        """sets the maximum number of mentions allowed in a message
        a setting of 0 disables this check"""
        server = ctx.message.server
        if m is not None:
            if server.id not in self.settings:
                self.settings[server.id] = {'max': 0, 'autoban': False}
            self.settings[server.id]["max"] = int(m)
            self.save_json()
            await self.bot.say("Maximum mentions set to {}".format(m))

    @checks.admin_or_permissions(Manage_server=True)
    @antimentionspam.command(
        name="autobantoggle", pass_context=True, no_pm=True)
    async def autobantoggle(self, ctx):
        """
        Toggle automatic ban for spam (default off)
        """
        server = ctx.message.server
        if server.id not in self.settings:
            self.settings[server.id] = {'max': 0, 'autoban': False}
        is_auto = not self.settings[server.id].get('autoban', False)
        self.settings[server.id]['autoban'] = is_auto
        self.save_json()
        await self.bot.say("Autoban: {}".format(is_auto))

    def immune(self, message):
        """Taken from mod.py"""
        user = message.author
        server = message.server
        admin_role = self.bot.settings.get_server_admin(server)
        mod_role = self.bot.settings.get_server_mod(server)

        if user.id == self.bot.settings.owner:
            return True
        elif discord.utils.get(user.roles, name=admin_role):
            return True
        elif discord.utils.get(user.roles, name=mod_role):
            return True
        else:
            return False

    async def check_msg_for_spam(self, message):
        if message.channel.is_private or self.bot.user == message.author \
         or not isinstance(message.author, discord.Member):
            pass
        else:
            server = message.server
            can_delete = \
                message.channel.permissions_for(server.me).manage_messages
            can_ban = \
                message.channel.permissions_for(server.me).ban_members

            if server.id in self.settings:
                autoban = self.settings[server.id].get('autoban', False)
                if self.settings[server.id]['max'] > 0:
                    if len(message.mentions) > self.settings[server.id]['max']:
                        if can_ban and autoban:
                            # catch especially fast spam/leave bots
                            await self.bot.http.ban(
                                message.author.id, server.id, 0)
                        if can_delete:
                            await self.bot.delete_message(message)


def setup(bot):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    n = AntiMentionSpam(bot)
    bot.add_listener(n.check_msg_for_spam, "on_message")
    bot.add_cog(n)
