import discord
from .utils import checks
from discord.ext import commands
import csv
from pathlib import Path
from datetime import datetime

path = Path('data') / 'membercsv'


class MemberCSV:
    """
    CSV generation of data
    """

    __author__ = "mikeshardmind(Sinbad#0001)"
    __version__ = "1.0.0"

    def __init__(self, bot):
        self.bot = bot

    async def csv_from_guild(self, who: discord.Member) -> Path:
        server = who.server
        fp = path / "{0.server.id}.csv".format(who)
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
            'id': "\u200b {}".format(member.id),
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

        fp = await self.csv_from_guild(ctx.message.author)
        try:
            await self.bot.send_file(ctx.message.author, fp)
        except discord.Forbidden:
            try:
                await self.bot.send_file(ctx.message.channel, fp)
            except Exception:
                await self.bot.say("I can't DM you or upload files here.")

        fp.unlink()


def setup(bot):
    path.mkdir(exist_ok=True, parents=True)
    bot.add_cog(MemberCSV(bot))
