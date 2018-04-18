

class CheckShim:

    def __init__(self, bot):
        self.bot = bot
        self.disallowed = []
        self.restricted = ['Audio']
        self.my_guilds = [355902355868483584, 78634202018357248]

    async def __global_check(self, ctx):
        if await ctx.bot.is_owner(
            ctx.author
        ):
            return True
        if any(
            ctx.command == self.bot.get_command(x)
            for x in self.disallowed
        ):
            return False
        if ctx.cog.__name__ in self.restricted:
            return ctx.guild.id in self.my_guilds if ctx.guild else False
        return True
