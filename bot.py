from os import name
from discord.ext import commands
import random

import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from dotenv import load_dotenv
load_dotenv('.env')

bot = commands.Bot(command_prefix='!')

@bot.command(name="idea", help="Get a side project idea")
async def idea(ctx):
    await ctx.send("Ideas are hard")
    await ctx.send("Worry not, I think you should...")

    topics = ['chat bot', 'cli', 'game', 'web bot', 'browser extention', 'api', 'web interface']
    areas = ['note taking', 'social life', 'physical fitness', 'mental health', 'pet care']

    idea = f'Create a new {random.choice(topics)} that helps with {random.choice(areas)}! :slight_smile:'
    await ctx.send(idea)


@bot.command(name="calc", help="Perform a calculation where fn is either +,-,*, or /")
async def calc(ctx, x: float, fn: str, y: float):
    if fn == '+':
        await ctx.send(x + y)
    elif fn == '-':
        await ctx.send(x - y)
    elif fn == '*':
        await ctx.send(x * y)
    elif fn == '/':
        await ctx.send(x / y)
    else:
        await ctx.send("We only support 4 function operations")


@bot.command(name="search", help="Look for new song release by artist")
async def search(ctx, artist: str):

    cid = os.getenv('SPOTIFY_CID')
    secret = os.getenv('SPOTFY_SECRET')

    client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # results = sp.search(q=artist)

    # for idx, track in enumerate(results['tracks']['items']):
    #     await ctx.send(track['name'])

    song_count = 50
    new_release = sp.new_releases(None, song_count, 0)

    for i in range(song_count):
        if new_release['albums']['items'][i]['artists'][0]['name'] == artist: # if artist names match
            await ctx.send('"' + new_release['albums']['items'][i]['name'] + '" by ' + artist) # return corresponding song title
            await ctx.send(new_release['albums']['items'][i]['external_urls']['spotify']) # return corresponding artist spotify link


# client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
# sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# # results = sp.search(q=artist)

# # for idx, track in enumerate(results['tracks']['items']):
# #     await ctx.send(track['name'])

# for i in range(0, 1000, 50):

#     song_count = 50
#     new_release = sp.new_releases(None, song_count, i)

#     for j in range(song_count):
#         print(new_release['albums']['items'][j]['name'])
#         # print(i+j)


# make sure to create a token file (in real life use env variables)
with open("BOT_TOKEN.txt", "r") as token_file:
    TOKEN = token_file.read()
    print("Token file read")
    bot.run(TOKEN)
