#import required dependencies
import discord 
from discord.ext import commands
import aiohttp
import asyncio
import yt_dlp as youtube_dl
import requests
import json


intents = discord.Intents.default()
intents.members = True
intents.messages = True  # If your bot needs to read messages
intents.guilds = True  # If your bot works with guild information
intents.message_content = True  # Enable the message content intent explicitly

client = commands.Bot(command_prefix = '!', intents=intents)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.8):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        ytdl_format_options = {
            'format': 'bestaudio/best',
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0',  # IPv4 only
        }

        ffmpeg_options = {
            'options': '-vn',  # No video.
        }

        ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # Take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


@client.command()
async def join(ctx):
    if ctx.author.voice and ctx.author.voice.channel:
        channel = ctx.author.voice.channel
        await channel.connect()
        print(f"Joined {channel.name} in {ctx.guild.name}")
    else:
        await ctx.send("You are not in a voice channel.")

@client.command()
async def play(ctx, *, url):
    """Plays from a URL (almost anything yt_dlp supports)"""
    if not ctx.voice_client:
        await ctx.send("I am not connected to a voice channel.")
        return

    async with ctx.typing():
        try:
            player = await YTDLSource.from_url(url, loop=client.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
            await ctx.send(f'Now playing: {player.title}')
        except Exception as e:
            await ctx.send(f'An error occurred: {e}')
            print(f'Error: {e}')


@client.event
async def on_ready():
    print("The bot is now ready for use!")
    print("-----------------------------")

#-------------------------------COMMANDS-------------------------------
#hello
@client.command()
async def hello(ctx):
    await ctx.send("Jawn Lit!")

#goodbye 
@client.command()
async def goodbye(ctx):
    await ctx.send("Fuck u!")

#joke
async def get_joke():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://official-joke-api.appspot.com/random_joke') as resp:
            if resp.status == 200:
                joke_data = await resp.json()
                return f"{joke_data['setup']} - {joke_data['punchline']}"
            else:
                return "Failed to fetch a joke. Please try again later."

@client.command()
async def joke(ctx):
    joke = await get_joke()
    await ctx.send(joke)


# -------------------------------CRABS DISCORD-------------------------------
#hello message when user joins discord
@client.event
async def on_member_join(member):
    channel = client.get_channel(571125646386790400) #glizzy didnt ask general chat
    await channel.send("Lol, who the fuck invited you")

#goodbye message when user leaves discord
@client.event
async def on_member_remove(member):
    channel = client.get_channel(571125646386790400) #glizzy didnt ask general chat
    await channel.send("We didn't want you here anyways")


#-------------------------------BJ's DISCORD-------------------------------
#hello message when user joins discord
@client.event
async def on_member_join(member):
    channel = client.get_channel(510246560873971713) #Bj's discord general chat
    await channel.send("Lol, who the fuck invited you")

#goodbye message when user leaves discord
@client.event
async def on_member_remove(member):
    channel = client.get_channel(510246560873971713) #Bj's discord general chat
    await channel.send("We didn't want you here anyways")


client.run('discord key')
