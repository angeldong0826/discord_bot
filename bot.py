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

#idea feature
@bot.command(name="idea", help="Get a side project idea")
async def idea(ctx):
    await ctx.send("Ideas are hard")
    await ctx.send("Worry not, I think you should...")

    topics = ['chat bot', 'cli', 'game', 'web bot', 'browser extention', 'api', 'web interface']
    areas = ['note taking', 'social life', 'physical fitness', 'mental health', 'pet care']

    idea = f'Create a new {random.choice(topics)} that helps with {random.choice(areas)}! :slight_smile:'
    await ctx.send(idea)

#calculator feature
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

#register feature
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
    # print(cur.rowcount, "records inserted.")
    
    # close connection
    conn.close()

    #cur.copy_to(sys.stdout, 'users', sep='\t')

#add favorite artist feature
@bot.command(name="add", help="Add your favorite artists")
async def add(ctx, artist: str):

    #display artists before inserting
    cur.execute("Select * from artists")
    results = cur.fetchall()
    print("From 'artists' table:")
    for i in results:
        print(i)
    
    #statement to insert artist
    cur.execute(
        """INSERT INTO artists (name) 
        SELECT %s
        WHERE NOT EXISTS ( 
            SELECT * 
            FROM artists as a 
            WHERE a.name= %s)""", (artist.lower(), artist.lower())
        )
    
    print("After insertion....")

    #print artists after insertion
    cur.execute("Select * from artists")
    myresult = cur.fetchall()
    print("From 'artists' table:")
    for i in myresult:
        print(i)
    
    cur.execute("Commit")
    await(ctx.send("Artist successfully added."))
    await(ctx.send("artist name: " + artist.lower()))

    #display favorites before inserting
    cur.execute("Select * from favorites")
    results = cur.fetchall()
    print("From 'favorites' table:")
    for i in results:
        print(i)

    #statement to insert favorite
    id = cur.execute("SELECT artistid FROM artists WHERE name=%s", (artist.lower()))
    # id = cur.execute("SELECT artistid FROM artists WHERE name =%s", ("olivia rodrigo"))
    # id = cur.execute("SELECT artistid FROM artists WHERE name='olivia rodrigo")

    cur.execute(
        "INSERT INTO favorites (artistid, discordid) VALUES (%s, %s)", (id, ctx.author.id)
    )

    print("After insertion....")

    #print favorites after insertion
    cur.execute("Select * from favorites")
    # rows_affected=cur.rowcount
    myresult = cur.fetchall()
    print("From 'favorites' table:")
    for i in myresult:
        print(i)

    cur.execute("Commit")
    await(ctx.send("Favorite successfully added."))
    await(ctx.send("favorite name: " + artist.lower()))
    # print(str(rows_affected) + " records inserted.")

    # close connection
    conn.close()

@bot.command(name="displayartists", help="Display your list of favorite artists")
async def displayartists(ctx):
    await(ctx.send("Your Favorite Artists:') :"))
    cur.execute("Select * from artists")
    results = cur.fetchall()
    for i in results:
        await(ctx.send(i))

@bot.command(name="displayfavorites")
async def displayfavorites(ctx):
    await(ctx.send("Your Favorite Artists:"))
    cur.execute("Select * from favorites")
    results = cur.fetchall()
    for i in results:
        await(ctx.send(i))

@bot.command(name="new", help="Look for new song release by artist")
async def new(ctx, artist: str):

    cid = os.getenv('SPOTIFY_CID')
    secret = os.getenv('SPOTFY_SECRET')

    cid='0c7d55253fcc4ef78a49bc9493591ad6'
    secret='79b9ade77bdc477d81f8c43c20ec872e'

    client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    results = sp.search(q=artist)

    for idx, track in enumerate(results['tracks']['items']):
        await ctx.send(track['name'])

    # song_count = 50
    # new_release = sp.new_releases(None, song_count, 0)

    # for i in range(song_count):
    #     if new_release['albums']['items'][i]['artists'][0]['name'] == artist: # if artist names match
    #         await ctx.send('"' + new_release['albums']['items'][i]['name'] + '" by ' + artist) # return corresponding song title
    #         await ctx.send(new_release['albums']['items'][i]['external_urls']['spotify']) # return corresponding artist spotify link


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
