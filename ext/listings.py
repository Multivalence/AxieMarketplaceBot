import aiohttp
import discord
import os
from discord.ext import commands, tasks
from discord import Webhook, AsyncWebhookAdapter
from datetime import datetime
from marketplace.axielatest import get_filtered_data


class Listings(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.saved_data = []
        self.send_listing.start()



    async def identifyWebhook(self):

        whooks = await self.listing_channel.webhooks()

        for i in whooks:
            if i.name == "Marketplace Listings":
                self.url = i.url
                return


        async with aiohttp.ClientSession() as cs:
            async with cs.get(str(self.bot.user.avatar_url)) as r:
                image_bytes = await r.read()

        web = await self.listing_channel.create_webhook(name="Marketplace Listings", avatar=image_bytes, reason="Axie Marketplace Bot")
        self.url = web.url


    @tasks.loop(seconds=60)
    async def send_listing(self):

        #Prevent memory overflow
        if len(self.saved_data) >= 1000000:
            self.saved_data = []

        data = await get_filtered_data()


        if len(data) == 0 or not data:
            return

        for listing in data:

            if listing in self.saved_data:
                continue


            embed = discord.Embed(
                title="New Listing",
                description=f"[{listing['id']}]({listing['url']})",
                colour=discord.Colour.blue(),
                timestamp=datetime.utcnow()
            )

            for i in listing:

                if i in ('id', 'image', 'url', 'numMystic'):
                    continue

                name = " ".join(map(str,[x.capitalize() for x in i.split("_")]))

                if isinstance(listing[i], list):
                    value = "```" + "\n".join(map(str,listing[i])) + "```"

                else:
                    value = f"```{listing[i]}```"

                embed.add_field(name=name, value=value)


            embed.set_image(url=listing['image'])

            async with aiohttp.ClientSession() as session:
                webhook = Webhook.from_url(self.url, adapter=AsyncWebhookAdapter(session))
                await webhook.send(embed=embed)





    @send_listing.before_loop
    async def before_send_listing(self):
        await self.bot.wait_until_ready()

        self.listing_channel = self.bot.get_channel(int(os.environ["LISTING-CHANNEL"]))

        await self.identifyWebhook()






#Setup
def setup(bot):
    bot.add_cog(Listings(bot))