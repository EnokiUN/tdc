import asyncio
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
        if i is not None:
            animated = "a" if emote.animated else ""
            content = content.replace(f":{i}:", f"<{animated}:{emote.name}:{emote.id}>")
    await client.channel.send(content)

@command(["emoji", "e"])
async def emoji_command(client, name, *args, **kwargs):
    emoji = discord.utils.get(client.emojis, name=name)
    animated = "a" if emoji.animated else ""
    await client.channel.send(f"<{animated}:{emoji.name}:{emoji.id}>")

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

async def select_guild(client):
    print("Which server do you want to access")
    while True:
        print("\n".join([f"[{x+1}] {i}" for x, i in enumerate(client.guilds)]))
        choice = input()
        try:
            choice = int(choice)
            assert choice > 0, "Out of range"
            guild = client.guilds[choice-1]
        except Exception as e:
            print("Incorrect choice")
            print(e)
            continue
        else:
            break
    return guild
 
async def select_channel(client, guild):
    client.channel = None
    print(f"Now select a channel from {guild}")
    while True:
        print("\n".join([f"[{x+1}] {i}" for x, i in enumerate(guild.text_channels)]))
        choice = input()
        try:
            choice = int(choice)
            assert choice > 0, "Out of range"
            client.channel = guild.text_channels[choice-1]
        except Exception as e:
            print("Incorrect choice")
            continue
        else:
            break
    print(f"---------- #{client.channel} - {guild} ----------")
    return client.channel

async def ainput(string: str="") -> str:
    if string:
        await asyncio.get_event_loop().run_in_executor(None, lambda s=string: sys.stdout.write(s+' '))
    return await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
