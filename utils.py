import asyncio
import curses
import sys
import re
import discord

commands = {}

def command(names):
    def inner(func):
        for i in names:
            commands[i] = func
        return func
    return inner

@command(["guild", "g"])
async def guild_command(client, *args, **kwargs):
    guild = await select_guild(client)
    channel = await select_channel(client, guild)

@command(["channel", "c"])
async def channel_command(client, *args, **kwargs):
    channel = await select_channel(client, client.channel.guild)

@command(["quit", "q"])
async def quit_command(client, *args, **kwargs):
    quit()

@command(["send", "s"])
async def send(client, content, *args, **kwargs):
    emotes = re.findall(":([a-zA-Z0-9_-]{2,32}):", content)
    for i in emotes:
        emote = discord.utils.get(client.emojis, name=i)
        if emote is not None:
            animated = "a" if emote.animated else ""
            content = content.replace(f":{i}:", f"<{animated}:{emote.name}:{emote.id}>")
    await client.channel.send(content)

@command(["emoji", "e"])
async def emoji_command(client, name, *args, **kwargs):
    emoji = discord.utils.get(client.emojis, name=name)
    animated = "a" if emoji.animated else ""
    await client.channel.send(f"<{animated}:{emoji.name}:{emoji.id}>")

@command(["reply", "r"])
async def reply(client, arg, *args, **kwargs):
    message, content = arg.split(" ", 1)
    message = int(message) - 1
    if message + 1 > len(client.seen_messages):
        return print("Unknown message")
    emotes = re.findall(":([a-zA-Z0-9_-]{2,32}):", content)
    for i in emotes:
        emote = discord.utils.get(client.emojis, name=i)
        if i is not None:
            animated = "a" if emote.animated else ""
            content = content.replace(f":{i}:", f"<{animated}:{emote.name}:{emote.id}>")
    await client.seen_messages[message].reply(content)

async def process_messages(client):
    while True:
        msg = await ainput()
        msg = msg.strip()
        if msg.startswith(":") and msg[1] != ":":
            msg_split = msg[1:].split(" ",1)
            command = msg_split[0]
            if not command in commands:
                print("Unknown command, \"::\" to escape")
            else:
                if len(msg_split) > 1:
                    args = msg_split[1]
                    await commands[command](client, args)
                else:
                    await commands[command](client)
        else:
            print ("\033[A \033[A")
            if msg.startswith(":"):
                msg = msg[1:]
            await send(client, msg)

async def handle_selection(stdscr, text):
    height, width = stdscr.getmaxyx()
    stdscr.clear()
    selection_pad = curses.newpad(1024, 1024)
    lines = text.splitlines()
    line = 1
    offset = 0
    stdscr.getch()
    selection_pad.clear()
    selection_pad.addstr(0, 0, text)
    selection_pad.addstr(line, 0, ">")
    selection_pad.refresh(offset, 0, 0, 0, height-1, width-1)
    while True:
        key = stdscr.getch()
        if key == -1:
            continue
        elif key == 113:
            exit()
        elif key == 10:
            break
        elif key == 65:
            line = max(1, line-1)
        elif key == 66:
            line = min(line+1, len(lines)-1)
        else:
            continue
        if line < height//2:
            offset = 0
        elif line > len(lines)-height//2:
            offset = len(lines)-height
        else:
            offset = line-height//2
        selection_pad.clear()
        selection_pad.addstr(0, 0, text)
        selection_pad.addstr(line, 0, ">")
        selection_pad.refresh(offset, 0, 0, 0, height-1, width-1)
    return line

async def select_guild(stdscr, client):
    text = "Choose a guild:"
    for i in client.guilds:
        text += f"\n  {i.name}"
    line = await handle_selection(stdscr, text)
    return client.guilds[line-1]
 
async def select_channel(stdscr, client, guild):
    client.channel = None
    text = f"Now choose a channel from {guild.name}"
    for i in guild.text_channels:
        text += f"\n  {i.name}"
    line = await handle_selection(stdscr, text)
    client.channel = guild.text_channels[line-1]
    return client.channel

