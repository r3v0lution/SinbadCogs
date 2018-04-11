from .checkshim import CheckShim


def setup(bot):
    bot.add_cog(CheckShim(bot))
