import aiohttp
import discord
import os
from discord import Webhook, AsyncWebhookAdapter
from discord.ext import commands, tasks
from datetime import datetime
from marketplace.axiesold import get_filtered_data


class Sold(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.saved_data = []
        self.send_sales.start()


    async def identifyWebhook(self):

        whooks = await self.sold_channel.webhooks()

        for i in whooks:
            if i.name == "Marketplace Sales":
                self.url = i.url
                return


        async with aiohttp.ClientSession() as cs:
            async with cs.get(str(self.bot.user.avatar_url)) as r:
                image_bytes = await r.read()

        web = await self.sold_channel.create_webhook(name="Marketplace Sales", avatar=image_bytes, reason="Axie Marketplace Bot")
        self.url = web.url


    @tasks.loop(minutes=3)
    async def send_sales(self):

        #Prevent memory overflow
        if len(self.saved_data) >= 1000000:
            self.saved_data = []


        data = await get_filtered_data()

        if len(data) == 0 or not data:
            return

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

                if i in ('id', 'image', 'url', 'numMystic'):
                    continue

                name = " ".join(map(str,[x.capitalize() for x in i.split("_")]))

                if isinstance(sale[i], list):
                    value = "```" + "\n".join(map(str,sale[i])) + "```"

                else:
                    value = f"```{sale[i]}```"


                embed.add_field(name=name, value=value)


            embed.set_image(url=sale['image'])

            async with aiohttp.ClientSession() as session:
                webhook = Webhook.from_url(self.url, adapter=AsyncWebhookAdapter(session))
                await webhook.send(embed=embed)




    @send_sales.before_loop
    async def before_send_sales(self):
        await self.bot.wait_until_ready()

        self.sold_channel = self.bot.get_channel(int(os.environ["SOLD-CHANNEL"]))
        await self.identifyWebhook()






#Setup
def setup(bot):
    bot.add_cog(Sold(bot))