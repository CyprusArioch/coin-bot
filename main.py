import nest_asyncio
nest_asyncio.apply()
import discord
import discord.ext.commands as commands
from os import getenv
bot = discord.Bot()
import pymongo

admin_roles = [226622910599659524, 301256373747056641]

client = pymongo.MongoClient(getenv("MONGO_URI"))
db = client["coinbot"]
coinscol = db["coins"]

class NotAuthorized(commands.CheckFailure):
    pass

def is_arioch():
    async def predicate(ctx):
        if ctx.author.id in admin_roles:
            return True
        raise NotAuthorized("You are not arioch, you cannot run this command.")
    return commands.check(predicate)

@bot.slash_command(name='adduser', description='Add a user to the database')
@is_arioch()
async def adduser(ctx, member: discord.Member, username: str):
    discordid = member.id
    query = { "discordid": discordid }
    doc = coinscol.find_one(query)
    if doc != None:
        await ctx.respond("This user has already been added.", ephemeral=True)
        return
    newuser = { "discordid": discordid, "username": username, "coins": 0 }
    temp = coinscol.insert_one(newuser)
    await ctx.respond(f"User '{username}' has been added.", ephemeral=True)

@bot.slash_command(name='removeuser', description='Remove a user from the database')
@is_arioch()
async def removeuser(ctx, member: discord.Member):
    discordid = member.id
    query = { "discordid": discordid }
    doc = coinscol.find_one(query,{ "_id": 0, "username": 1 })
    if doc == None:
        await ctx.respond("This user does not exist.", ephemeral=True)
        return
    coinscol.delete_one(query)
    username = doc["username"]
    await ctx.respond(f"User {username} has been deleted.", ephemeral=True)
    return

@bot.slash_command(name='viewcoins', description='View coins for a user')
async def viewcoins(ctx, member: discord.Member):
    if (ctx.author.id != member.id) and (ctx.author.id not in admin_roles):
        raise NotAuthorized("You can only run this command to view your own coins.")
    discordid = member.id
    query = { "discordid": discordid }
    doc = coinscol.find_one(query)
    if doc == None:
        await ctx.respond("User does not exist.", ephemeral=True)
        return
    username = doc["username"]
    embed = discord.Embed(title=f"{username}'s Coins", description=f"Discord ID: {str(discordid)}")
    embed.add_field(name="Coins", value=str(doc["coins"]))
    await ctx.respond(embed=embed)

@bot.slash_command(name="addcoins", description="Give coins to a user")
@is_arioch()
async def addcoins(ctx, member: discord.Member, coins: float):
    discordid = member.id
    query = { "discordid": discordid }
    doc = coinscol.find_one(query)
    if doc == None:
        await ctx.respond("User does not exist.", ephemeral=True)
        return
    newcoins = doc["coins"] + coins
    newvalue = { "$set": { "coins": newcoins } }
    coinscol.update_one(query, newvalue)
    username = doc["username"]
    await ctx.respond(f"{str(coins)} coins given to {username}")

@bot.slash_command(name="removecoins", description="Remove coins from a user")
@is_arioch()
async def removecoins(ctx, member: discord.Member, coins: float):
    discordid = member.id
    query = { "discordid": discordid }
    doc = coinscol.find_one(query)
    if doc == None:
        await ctx.respond("User does not exist.", ephemeral=True)
        return
    newcoins = doc["coins"] - coins
    newvalue = { "$set": { "coins": newcoins } }
    coinscol.update_one(query, newvalue)
    username = doc["username"]
    await ctx.respond(f"{str(coins)} coins removed from {username}")

@bot.slash_command(name="setcoins", description="Set a users coins")
@is_arioch()
async def setcoins(ctx, member: discord.Member, coins: float):
    discordid = member.id
    query = { "discordid": discordid }
    doc = coinscol.find_one(query)
    if doc == None:
        await ctx.respond("User does not exist.", ephemeral=True)
        return
    newcoins = coins
    newvalue = { "$set": { "coins": newcoins } }
    coinscol.update_one(query, newvalue)
    username = doc["username"]
    await ctx.respond(f"{username} has had their coins set to {str(newcoins)}")

@bot.slash_command(name="viewall", description="View all users and their coin amounts")
@is_arioch()
async def viewall(ctx):
    embed = discord.Embed(title="Coin amounts", description="All user's coin amounts")
    for doc in coinscol.find():
        embed.add_field(name="Username", value=doc["username"])
        embed.add_field(name="Discord ID", value=str(doc["discordid"]), inline=True)
        embed.add_field(name="Coins", value=str(doc["coins"]), inline=True)
    await ctx.respond(embed=embed)
        


@bot.event
async def on_application_command_error(ctx, error):
    if isinstance(error, NotAuthorized):
        await ctx.respond(error, ephemeral=True)
        return
    else:
        await ctx.respond(error)
        return

bot.run(getenv("BOT_TOKEN"))