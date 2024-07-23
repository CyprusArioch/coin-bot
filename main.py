import nest_asyncio
import asyncio
nest_asyncio.apply()
import discord
import discord.ext.commands as commands
from os import getenv
bot = discord.Bot()
import pymongo

client = pymongo.MongoClient(getenv("MONGO_URI"))
db = client["coinbot"]
coinscol = db["coins"]

class NotAuthorized(commands.CheckFailure):
    pass

def is_arioch():
    async def predicate(ctx):
        if ctx.author.id == 226622910599659524 or ctx.author.id == 301256373747056641:
            return True
        raise NotAuthorized("You are not arioch, you cannot run this command.")
    return commands.check(predicate)

@bot.slash_command(name='adduser', description='Add a user to the database')
@is_arioch()
async def adduser(ctx, username: str):
    query = { "username": username }
    doc = coinscol.find_one(query)
    if doc != None:
        await ctx.respond("This user has already been added.", ephemeral=True)
        return
    newuser = { "username": username, "coins": 0 }
    temp = coinscol.insert_one(newuser)
    await ctx.respond(f"User '{username}' has been added.", ephemeral=True)
    return

@bot.slash_command(name='removeuser', description='Remove a user from the database')
@is_arioch()
async def removeuser(ctx, username: str):
    query = { "username": username }
    doc = coinscol.find_one(query)
    if doc == None:
        await ctx.respond("This user does not exist.", ephemeral=True)
        return
    coinscol.delete_one(query)
    await ctx.respond(f"User {username} has been deleted.", ephemeral=True)
    return

@bot.event
async def on_application_command_error(ctx, error):
    if isinstance(error, NotAuthorized):
        await ctx.respond(error, ephemeral=True)
        return

bot.run(getenv("BOT_TOKEN"))