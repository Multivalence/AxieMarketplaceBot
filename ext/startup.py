import aiosqlite
from discord.ext import commands

class Startup(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.initializeDB())



    async def initializeDB(self):

        self.bot.db = await aiosqlite.connect('data.db')

        sql = """CREATE TABLE IF NOT EXISTS listings (
            channel BIGINT PRIMARY KEY UNIQUE,
            data TEXT)
        """

        sql2 = """CREATE TABLE IF NOT EXISTS sales (
            channel BIGINT PRIMARY KEY UNIQUE,
            data TEXT)
        """


        await self.bot.db.execute(sql)
        await self.bot.db.execute(sql2)
        await self.bot.db.commit()



    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Logged in as {self.bot.user.name} | {self.bot.user.id}')




#Setup
def setup(bot):
    bot.add_cog(Startup(bot))