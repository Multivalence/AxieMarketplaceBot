import aiohttp
import discord
import json
from discord.ext import commands
from ext.errors import NoSubcommandFound, ChannelNotFound, ChannelAlreadyFiltered
from ext.checks import is_file_valid
from sqlite3 import IntegrityError


class CommandsListing(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.filters = ('classes', 'health', 'breedCount', 'speed', 'skill', 'morale', 'parts', 'abilities', 'price', 'pureness', 'numMystic')



    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.group(invoke_without_command=True)
    async def listing(self, ctx):
        raise NoSubcommandFound


    @listing.command(name='add', description='Add a listing')
    @commands.check(is_file_valid)
    async def add(self, ctx, channel : discord.TextChannel):
        url = ctx.message.attachments[0].url

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                x = await resp.json()

        for i in self.filters:
            if i in x.keys():
                continue

            else:
                return await ctx.send("Invalid data in JSON File!")

        try:
            json_data = json.dumps(x)

        except json.decoder.JSONDecodeError:
            return await ctx.send("Invalid data in JSON File!")

        sql = 'INSERT INTO listings(channel) VALUES (?)'
        sql2 = 'UPDATE listings set data = ? where channel = ?'

        try:
            await self.bot.db.execute(sql, (channel.id,))
            await self.bot.db.execute(sql2, (json_data, channel.id))
            await self.bot.db.commit()

        except IntegrityError:
            raise ChannelAlreadyFiltered

        else:

            embed = discord.Embed(
                title="Action Successful",
                description=f"Listing added at {channel.mention}",
                colour=discord.Colour.green()
            )

            return await ctx.send(embed=embed)






    @listing.command(name='remove', description="Remove a listing")
    async def remove(self, ctx, channel : discord.TextChannel):

        async with self.bot.db.execute('SELECT channel from listings') as cursor:
            channels = await cursor.fetchall()

            if channel.id not in [i[0] for i in channels]:
                raise ChannelNotFound


        sql = 'DELETE FROM listings WHERE channel=?'

        async with self.bot.db.execute(sql, (channel.id,)) as cursor:
            await self.bot.db.commit()


        embed = discord.Embed(
            title="Action Successful",
            description=f"Listing Channel Removed: {channel.mention}",
            colour=discord.Colour.red()
        )

        return await ctx.send(embed=embed)






#Setup
def setup(bot):
    bot.add_cog(CommandsListing(bot))