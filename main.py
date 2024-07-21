import os
import re
import discord
from discord.ext import commands
from pytube import YouTube
import openai
from requests import get
from youtube_transcript_api import YouTubeTranscriptApi
import json

# Set up OpenAI
openai.api_key = os.environ['OPENAI_API_KEY']

# Initialize Discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def response(a: str):
    response = openai.Completion.create(
        model="gpt-3.5-turbo",
        prompt=f"{a}\n\nTl;dr",
        max_tokens=50,
        temperature=0.5,
        n=1,
        stop=None
    )
    summary = response.choices[0].text.strip()
    return summary

def func(transcript):
    text = ""
    for entry in transcript:
        text += entry['text'] + " "
    return text.strip()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command(name='start')
async def start_command(ctx):
    await ctx.send("Simply share the link and choose the Function✨.")

@bot.command(name='download')
async def download_command(ctx, url: str):
    try:
        yt = YouTube(url)
        video_info = (
            f"**Title:** {yt.title}\n"
            f"**Channel:** {yt.author}\n"
            f"**Views:** {yt.views}\n"
            f"**Length:** {yt.length} seconds"
        )
        await ctx.send(video_info)

        options = ["1080p", "720p", "360p", "144p", "Audio", "Summary"]
        options_message = "Choose a format: " + ", ".join([f"`{opt}`" for opt in options])
        await ctx.send(options_message)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        reply = await bot.wait_for('message', check=check)
        choice = reply.content.lower()

        if choice in ["1080p", "720p", "360p", "144p"]:
            resolution_stream = yt.streams.filter(res=choice, progressive=True).first()
            if resolution_stream:
                await ctx.send(f"Downloading {choice} video...")
                resolution_stream.download(filename="video.mp4")
                await ctx.send(file=discord.File("video.mp4"))
            else:
                await ctx.send(f"{choice} resolution is not available.")
        elif choice == "audio":
            audio_stream = yt.streams.filter(only_audio=True).first()
            await ctx.send("Downloading audio...")
            audio_stream.download(filename="audio.mp3")
            await ctx.send(file=discord.File("audio.mp3"))
        elif choice == "summary":
            transcript = YouTubeTranscriptApi.get_transcript(yt.video_id)
            text = func(transcript)
            summary = response(text)
            await ctx.send(f"Summary: {summary}")
        else:
            await ctx.send("Invalid choice. Please try again.")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

bot.run(os.environ['534bd5919e3d971d3280513643bf535f28bdcf8553f49678416d0c7ed16b6e97'])
