from os import name
import re
from discord.enums import UserFlags
from discord.ext import commands
import random
import psycopg2
import os
import spotipy
import sys
from spotipy.oauth2 import SpotifyClientCredentials

from dotenv import load_dotenv

#load dotenv for sensitive information purposes
load_dotenv('.env')


#connect to database
try:
    conn = psycopg2.connect(
        dbname="spotifybot",
        user="postgres",
        password="Jeremiah29:11",
        host="localhost",
        port="5432"
    )
    print("Connected to database.")
except:
    print ("Unable to connect to database")

#make cursor for establish connection
cur = conn.cursor()


#initialize bot
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

@bot.command(name = "login")
async def login(ctx):

    #display records before inserting
    cur.execute("Select * from users")
    results = cur.fetchall()
    for i in results:
        print(i)

    #statement to insert record
    cur.execute(
        """INSERT INTO users (discordid, username) 
        SELECT %s, %s
        WHERE NOT EXISTS ( 
            SELECT * 
            FROM users as u 
            WHERE u.discordid= %s)""", (ctx.author.id, ctx.author.name, ctx.author.id)
        )

    print("After insertion....")

    # print records after insertion
    cur.execute("Select * from users")

    myresult = cur.fetchall()
    for i in myresult:
        print(i)
    cur.execute("Commit")

    await(ctx.send("User info successfully logged/found."))
    await(ctx.send("username: " + ctx.author.name))
    await(ctx.send("discord id: " + str(ctx.author.id)))
    print(cur.rowcount, "records inserted.")
    
    # close connection
    # conn.close()

# cur.copy_to(sys.stdout, 'users', sep='\t')


@bot.command(name="new", help="Look for new song release by artist")
async def new(ctx, artist: str):

    cid = os.getenv('SPOTIFY_CID')
    secret = os.getenv('SPOTFY_SECRET')

    cid='0c7d55253fcc4ef78a49bc9493591ad6'
    secret='79b9ade77bdc477d81f8c43c20ec872e'

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
