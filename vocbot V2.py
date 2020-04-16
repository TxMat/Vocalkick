import discord
import asyncio
from time import sleep, time

print(discord.__version__)
TOKEN = "Njk3MzQzMTIwNDMzNzQxOTQ3.Xo2YMw.5PGHVvsDXlaz6iXwKAsE6gHWmCQ"

OPTIONS = {}
OPTIONS["alone_time"] = 300
OPTIONS["reason"] = "as-tu oublié de te déconnecter du vocal? ne t'inquiete pas je l'ai fait pour toi :)"
OPTIONS["prefix"] = "§"
OPTIONS["running"] = True


client = discord.Client()
CHANNELS = {}

async def option(message, var, value, *args):
    OPTIONS[var] = type(OPTIONS[var])(value)

async def change_presence(message, *args):
    await client.change_presence(activity=discord.Activity(name=" ".join(args), type=discord.ActivityType.playing))

async def toogle_stop(message, *args):
    OPTIONS["running"] = not OPTIONS["running"]
    if OPTIONS["running"] == True:
        await change_presence(message, 'online and ready')
        print("resuming")
    else:
        print("stopped")
        await change_presence(message, 'paused by :', str(message.author))

    
async def helpa(message, ty):
    mem = message.author
    if ty == "dm":
        await mem.create_dm()
        await mem.dm_channel.send("**command list:** \n__option alone_time :__ temps ")


async def helpp(message, *args):
    await message.channel.send(content="faites §h dm pour avoir de de l'aide en dm ou §h ch pour que j'envoie l'aide ici.")

actions = {"option": option, "desc": change_presence, "stop": toogle_stop, "help": helpp, "h": helpa}


@client.event
async def on_message(message):
    if len(message.content) and message.content[0] == OPTIONS["prefix"]:
        a = message.content[1:].split(" ")
        if a[0] not in actions:
            print("wrong command:", message.content, "by :", message.author)
            return
        print("executing command:", message.content, "by :", message.author)
        await actions[a[0]](message, *a[1:])


@client.event
async def on_ready():
    print('{} is online'.format(client.user))
    await change_presence(None, 'online and ready') 
    

async def on_delay(channel):
    if not OPTIONS["running"]:
        if channel in CHANNELS:
            del CHANNELS[channel]
        return
    await asyncio.sleep(OPTIONS["alone_time"])
    while not OPTIONS["running"]:
        await asyncio.sleep(OPTIONS["alone_time"])
    if channel in CHANNELS:
        del CHANNELS[channel]
        members = channel.members
        if len(members) != 1:
            return
        print(members[0], "kicked!")
        await members[0].edit(voice_channel=None, reason=OPTIONS["reason"])
        await members[0].create_dm()
        await members[0].dm_channel.send(OPTIONS["reason"], delete_after = 86400)
        
    

@client.event
async def on_voice_state_update(member, before, after):
    if after.channel and before.channel != after.channel:
        if after.channel in CHANNELS:
            del CHANNELS[after.channel]
    
    if before.channel and  before.channel != after.channel:
        if len(before.channel.members) == 1:
            CHANNELS[before.channel] = True
            await on_delay(before.channel)
        else:
            if before.channel in CHANNELS:
                del CHANNELS[before.channel]
        
client.run(TOKEN)

