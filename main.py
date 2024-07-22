import nest_asyncio
import asyncio
nest_asyncio.apply()
import discord
from os import getenv

bot = discord.Bot()

bot.run(getenv("BOT_TOKEN"))