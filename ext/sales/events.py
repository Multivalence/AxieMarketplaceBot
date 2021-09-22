import aiohttp
import discord
import json
from discord import Webhook, AsyncWebhookAdapter
from discord.ext import commands, tasks
from datetime import datetime
from marketplace.axiesold import get_filtered_data
from marketplace.axiefloorprice import get_floor_price


class SoldEvent(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.saved_data = []
        self.send_sales.start()


    async def fetch_db_data(self):

        sql = 'SELECT channel, data FROM sales'

        async with self.bot.db.execute(sql) as cursor:
            acc = await cursor.fetchall()

            return acc


    async def identifyWebhook(self, channel_id):

        channel = self.bot.get_channel(channel_id)

        whooks = await channel.webhooks()

        for i in whooks:
            if i.name == "Marketplace Sales":
                return i.url



        async with aiohttp.ClientSession() as cs:
            async with cs.get(str(self.bot.user.avatar_url)) as r:
                image_bytes = await r.read()

        web = await channel.create_webhook(name="Marketplace Sales", avatar=image_bytes, reason="Axie Marketplace Bot")
        return web.url


    @tasks.loop(minutes=3)
    async def send_sales(self):

        #Prevent memory overflow
        if len(self.saved_data) >= 1000000:
            self.saved_data = []


        db_data = await self.fetch_db_data()

        for channel_id, data_str in db_data:

            webhook_url = await self.identifyWebhook(channel_id)
            data_json = json.loads(data_str)

            data = await get_filtered_data(data_json)



            if not data or len(data) == 0:
                continue

            for sale in data:

                if sale in self.saved_data:
                    continue


                embed = discord.Embed(
                    title="New Sale",
                    description=f"[{sale['id']}]({sale['url']})",
                    colour=discord.Colour.red(),
                    timestamp=datetime.utcnow()
                )

                for i in sale:

                    if i in ('id', 'image', 'url', 'body_parts_id'):
                        continue

                    name = " ".join(map(str,[x.capitalize() for x in i.split("_")]))

                    if isinstance(sale[i], list):
                        value = "```" + "\n".join(map(str,sale[i])) + "```"

                    else:
                        value = f"```{sale[i]}```"


                    embed.add_field(name=name, value=value)


                embed.add_field(name="Floor Price", value=f"```{await get_floor_price(data_json)}```")


                embed.set_image(url=sale['image'])

                async with aiohttp.ClientSession() as session:
                    webhook = Webhook.from_url(webhook_url, adapter=AsyncWebhookAdapter(session))
                    await webhook.send(embed=embed)




    @send_sales.before_loop
    async def before_send_sales(self):
        await self.bot.wait_until_ready()






#Setup
def setup(bot):
    bot.add_cog(SoldEvent(bot))