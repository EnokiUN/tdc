import asyncio
import curses
from curses import wrapper
import discord
import json
import os
import sys
from utils import select_guild, select_channel, process_messages

HOME = os.path.expanduser("~/.tdc")

intents = discord.Intents.all()
client = discord.Client(intents=intents)

client.seen_messages = []
client.channel = None

@client.event
async def on_ready():
    wrapper(main)
    # guild = await select_guild(client)
    # await select_channel(client, guild)
    # while True:
    #     try:
    #         await process_messages(client)
    #     except Exception as e:
    #         print("Fatal Error:")
    #         print(e)

async def process_UI(stdscr, client):
    stdscr.nodelay(True)
    height, width = stdscr.getmaxyx()
    guild = await select_guild(stdscr, client)
    await select_channel(stdscr, client, guild)
    input_box =  curses.newpad(2000, 2000)
    stdscr.clear()
    stdscr.refresh()
    text = str()
    while True:
        key = stdscr.getch()
        if key == -1:
            continue
        if key == 127: # Backspace
            # text = text[:-1]
            text += 'sus'
        elif key == 10: # Enter
            if text == ":wq":
                exit()
            await client.channel.send(text)
            text = str()
        else:
            text += chr(key)
        input_box.clear()
        input_box.addstr(0, 0, text)
        input_box.refresh(0, max(0, len(text)-width), height-1, 0, height-1, width-1)

def main(stdscr):
    loop = asyncio.get_event_loop()
    loop.create_task(process_UI(stdscr, client))

@client.event
async def on_message(message: discord.Message):
    client.seen_messages.append(message)
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

