

class CheckShim:

    def __init__(self, bot):
        self.bot = bot
        self.disallowed = ['contact']

    async def __global_check(self, ctx):
        if not await ctx.bot.is_owner(
            ctx.author
        ) and any(
            ctx.command == self.bot.get_command(x)
            for x in self.disallowed
        ):
            return False
        return True
