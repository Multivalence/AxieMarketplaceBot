import discord
import os
from dotenv import load_dotenv, find_dotenv
from discord.ext import commands

load_dotenv(find_dotenv())


bot = commands.Bot(command_prefix=commands.when_mentioned_or("!$@&^%@#()"),
                   status=discord.Status.online,
                   intents=discord.Intents.all(),
                   help_command=None)


extensions = [
    'ext.startup',
    'ext.listings',
    'ext.sold'
]


for ext in extensions:
    bot.load_extension(ext)


bot.run(os.environ["TOKEN"])