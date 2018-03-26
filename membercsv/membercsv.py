import discord
from .utils import checks
from discord.ext import commands
import csv
from pathlib import Path
from datetime import datetime
import os

path = Path('data') / 'membercsv'


class MemberCSV:
    """
    CSV generation of data
    """

    __author__ = "mikeshardmind(Sinbad#0001)"
    __version__ = "0.0.2a"

    def __init__(self, bot):
        self.bot = bot
        self.user_cache = []

    async def csv_from_guild(self, who: discord.Member) -> Path:
        server = who.server
        fp = path / "{0}-{1.id}.csv".format(
            str(datetime.utcnow())[:10], who)
        with fp.open(mode='w', encoding='utf-8') as csvfile:
            fieldnames = [
                'id',
                'name',
                'highestrole',
                'membersince',
                'discordmembersince',
                'memberage',
                'currentstatus',
                'currentactivity'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for member in sorted(server.members, key=lambda m: m.joined_at):
                writer.writerow(await self.get_member_row(member))
        return fp

    async def get_member_row(self, member: discord.Member) -> dict:
        ret = {
            'id': member.id,
            'name': str(member),
            'highestrole': "{0.name} ({0.id})".format(member.top_role),
            'membersince': member.joined_at.strftime("%d %b %Y %H:%M"),
            'discordmembersince': member.created_at.strftime("%d %b %Y %H:%M"),
            'memberage': "{} days.".format(
                (datetime.utcnow() - member.joined_at).days),
            'currentstatus': str(member.status)
        }
        if member.game is None:
            g = ""
        elif member.game.type == 0:
            g = "Playing: {}".format(member.game)
        elif member.game.type == 1:
            g = "Streaming: {}  || Streamurl: {}".format(
                member.game, member.game.url)
        elif member.game.type == 2:
            g = "Listening to: {}".format(member.game)
        elif member.game.type == 3:
            g = "Watching: {}".format(member.game)
        ret['currentactivity'] = g

        return ret

    @commands.command(name='getmembercsv', pass_context=True, no_pm=True)
    @checks.serverowner_or_permissions(manage_server=True)
    async def getmembercsv(self, ctx):
        """
        get a csv with member data
        """
        if ctx.message.author in self.user_cache:
            return await self.bot.say(
                "wait a moment, still finishing your previous request.")
        self.user_cache.append(ctx.message.author)
        try:
            await self.bot.whisper(
                "This might take a few minutes depending on server size")
        except Exception:
            await self.bot.say(
                "I can't do that. I need to be able to message you.")
        else:
            fp = await self.csv_from_guild(ctx.message.author)
            await self.bot.send_file(ctx.message.author, fp)
            os.remove(fp.resolve())

        self.user_cache.remove(ctx.message.author)


def setup(bot):
    if path.exists:
        path.rmdir()
    path.mkdir(exist_ok=True, parents=True)
    bot.add_cog(MemberCSV(bot))
