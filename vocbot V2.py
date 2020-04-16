import discord
import asyncio
from time import sleep, time
from json import load as json_load

print(discord.__version__)


with open("config.json") as f:
    CONFIG = json_load(f)


OPTIONS = {}

client = discord.Client()
CHANNELS = {}

async def option(message, var, value, *args):
    OPTIONS[message.guild.id][var] = type(OPTIONS[message.guild.id][var])(value)

async def change_presence(message, *args):
    await client.change_presence(activity=discord.Activity(name=" ".join(args), type=discord.ActivityType.playing))

async def toogle_stop(message, *args):
    OPTIONS[message.guild.id]["running"] = not OPTIONS[message.guild.id]["running"]
    if OPTIONS[message.guild.id]["running"] == True:
        await change_presence(message, 'online and ready §help')
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
    emoji = "👌"
    mem = message.author
    await message.channel.send(content="send ;)")
    await message.add_reaction(emoji)
    await mem.create_dm()
    await mem.dm_channel.send("__**command list:**__ \n\n**option alone_time :** temps (en sec) qu'un utilisateur peut rester seul dans un vocal\n\n**option_raison :** le message qui sera envoyé aux utilisateur kickés (le message se supprime au bout de 24 h)\n\n**stop :** permet d'arreter le bot temporairement en cas de problèmes (pour relancer le bot il suffit de refaire la commande)\n\n**option_prefix :** permet de changer le prefix du bot (§ par defaut)\n\n**help :** envoie ce message à l'utilisateur qui effectue la commande")

actions = {"option": option, "desc": change_presence, "stop": toogle_stop, "help": helpp,}
admin_actions = ["desc"]

@client.event
async def on_message(message):
    if type(message.channel) != discord.TextChannel:
        return
    if len(message.content) and message.content[0] == OPTIONS[message.guild.id]["prefix"]:
        
        a = message.content[1:].split(" ")
        if a[0] not in actions:
            print("wrong command:", message.content, "by :", message.author)
            return
        if a[0] in admin_actions and message.author.id not in CONFIG["admins"]:
            print("wrong permission to use command:", message.content, "by :", message.author)
            return
        print("executing command:", message.content, "by :", message.author)
        await actions[a[0]](message, *a[1:])


@client.event
async def on_ready():
    print('{} is online'.format(client.user))
    await change_presence(None, 'online and ready §help') 
    for server in client.guilds:
        OPTIONS[server.id] = {}
        OPTIONS[server.id]["alone_time"] = 300
        OPTIONS[server.id]["reason"] = "as-tu oublié de te déconnecter du vocal? ne t'inquiete pas je l'ai fait pour toi :)"	
        OPTIONS[server.id]["prefix"] = "§"	
        OPTIONS[server.id]["running"] = True
        
@client.event
async def on_guild_join(guild):
    OPTIONS[server.id] = {}
    OPTIONS[server.id]["alone_time"] = 300
    OPTIONS[server.id]["reason"] = "as-tu oublié de te déconnecter du vocal? ne t'inquiete pas je l'ai fait pour toi :)"	
    OPTIONS[server.id]["prefix"] = "§"	
    OPTIONS[server.id]["running"] = True

async def on_delay(channel):
    if not OPTIONS[channel.guild.id]["running"]:
        if channel in CHANNELS:
            del CHANNELS[channel]
        return
    await asyncio.sleep(OPTIONS[channel.guild.id]["alone_time"])
    while not OPTIONS[channel.guild.id]["running"]:
        await asyncio.sleep(OPTIONS[channel.guild.id]["alone_time"])
    if channel in CHANNELS:
        del CHANNELS[channel]
        members = channel.members
        if len(members) != 1:
            return
        print(members[0], "kicked!")
        await members[0].edit(voice_channel=None, reason=OPTIONS[channel.guild.id]["reason"])
        await members[0].create_dm()
        await members[0].dm_channel.send(OPTIONS[channel.guild.id]["reason"], delete_after = 86400)
        
    
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
        
client.run(CONFIG["token"])

