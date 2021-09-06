import discord
from discord.ext import commands
import sys
import traceback
import ext.errors



class ChannelNotFound(commands.CommandError):
    pass

class ChannelAlreadyFiltered(commands.CommandError):
    pass

class NoSubcommandFound(commands.CommandError):
    pass

class FilterNotFound(commands.CommandError):
    pass




class Errors(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        # Gets original attribute of error
        error = getattr(error, "original", error)


        if isinstance(error, commands.errors.BadArgument):
            await ctx.send("Bad argument.",delete_after=10)
            return

        elif isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send("You are missing a required argument",delete_after=10)


        elif isinstance(error, discord.ext.commands.errors.NoPrivateMessage):
            return

        elif isinstance(error, discord.ext.commands.errors.MissingPermissions):
            await ctx.send("You require Administrator privileges to do this command!")


        elif isinstance(error, ext.errors.ChannelNotFound):
            await ctx.send("That channel is not being filtered")

        elif isinstance(error, ext.errors.ChannelAlreadyFiltered):
            await ctx.send("Channel already being filtered. Please remove the current filter to add a new one!")

        elif isinstance(error, ext.errors.NoSubcommandFound):
            await ctx.send("Please provide a sub-command!")

        elif isinstance(error, ext.errors.FilterNotFound):
            await ctx.send("Please provide a filter in JSON format!")

        else:

            # Prints original traceback if it isnt handled
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)



#Setup
def setup(bot):
    bot.add_cog(Errors(bot))