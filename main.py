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
    username = username.lower()
    query = { "username": username }
    doc = coinscol.find_one(query)
    if doc != None:
        await ctx.respond("This user has already been added.", ephemeral=True)
        return
    newuser = { "username": username, "coins": 0 }
    temp = coinscol.insert_one(newuser)
    await ctx.respond(f"User '{username}' has been added.", ephemeral=True)

@bot.slash_command(name='removeuser', description='Remove a user from the database')
@is_arioch()
async def removeuser(ctx, username: str):
    username = username.lower()
    query = { "username": username }
    doc = coinscol.find_one(query)
    if doc == None:
        await ctx.respond("This user does not exist.", ephemeral=True)
        return
    coinscol.delete_one(query)
    await ctx.respond(f"User {username} has been deleted.", ephemeral=True)
    return

@bot.slash_command(name='view', description='View coins for a user')
@is_arioch()
async def view(ctx, username: str):
    username = username.lower()
    query = { "username": username }
    doc = coinscol.find_one(query)
    if doc == None:
        await ctx.respond("User does not exist.", ephemeral=True)
        return
    embed = discord.Embed(title=f"{username}'s Coins", description=f"Coins for user {username}")
    embed.add_field(name="Coins", value=str(doc["coins"]))
    await ctx.respond(embed=embed)

@bot.slash_command(name="addcoins", description="Give coins to a user")
async def addcoins(ctx, username: str, coins: float):
    username = username.lower()
    query = { "username": username }
    doc = coinscol.find_one(query)
    if doc == None:
        await ctx.respond("User does not exist.", ephemeral=True)
        return
    newcoins = doc["coins"] + coins
    newvalue = { "$set": { "coins": newcoins } }
    coinscol.update_one(query, newvalue)
    await ctx.respond(f"{str(coins)} coins given to {username}")

@bot.slash_command(name="removecoins", description="Remove coins from a user")
async def removecoins(ctx, username: str, coins: float):
    username = username.lower()
    query = { "username": username }
    doc = coinscol.find_one(query)
    if doc == None:
        await ctx.respond("User does not exist.", ephemeral=True)
        return
    newcoins = doc["coins"] - coins
    newvalue = { "$set": { "coins": newcoins } }
    coinscol.update_one(query, newvalue)
    await ctx.respond(f"{str(coins)} coins removed from {username}")

@bot.slash_command(name="setcoins", description="Set a users coins")
async def setcoins(ctx, username: str, coins: float):
    username = username.lower()
    query = { "username": username }
    doc = coinscol.find_one(query)
    if doc == None:
        await ctx.respond("User does not exist.", ephemeral=True)
        return
    newcoins = coins
    newvalue = { "$set": { "coins": newcoins } }
    coinscol.update_one(query, newvalue)
    await ctx.respond(f"{username} has had their coins set to {str(newcoins)}")

@bot.event
async def on_application_command_error(ctx, error):
    if isinstance(error, NotAuthorized):
        await ctx.respond(error, ephemeral=True)
        return

bot.run(getenv("BOT_TOKEN"))