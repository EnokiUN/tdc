import discord
import json
import os
import sys
from utils import *

HOME = "/data/data/com.termux/files/home/.tdc" # Had to manually add the .terminalcord path for termux reasons.

intents = discord.Intents.all()
client = discord.Client(intents=intents)

client.channel = None

@client.event
async def on_ready():
    sys.stdout.flush()
    print("Discord started.")
    guild = await select_guild(client)
    await select_channel(client, guild)
    await process_messages(client)

@client.event
async def on_message(message: discord.Message):
    if client.channel.id is None: return
    if message.channel.id == client.channel.id or client.user in message.mentions:
        if message.channel.id != client.channel.id:
            print(f"----- New Mention from #{message.channel} - {message.guild}")
        if message.reference:
            refmsg = await message.channel.fetch_message(message.reference.message_id)
            if refmsg is None:
                return print("╭───> [Unable to Load Message]")
            print(f"╭───> [{refmsg.author}]: {refmsg.clean_content}")
        print(f"[{message.author}]: {message.clean_content}")
        if message.channel.id != client.channel.id:
            print("----------")

if not os.path.exists(HOME):
    print("No .tdc configuratuon exists")
    sys.exit()

with open(HOME) as f:
    DATA = json.load(f)

TOKEN = DATA.get("token", None)
BOT = DATA.get("bot", None)

if any([i is None for i in [TOKEN, BOT]]):
    print("Impropper data in .tdc")
    sys.exit()

# client.run(TOKEN, bot=BOT)
client.run(TOKEN)

