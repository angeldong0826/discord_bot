from discord.ext import commands
import psycopg2
import os
import spotipy
import sys
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

load_dotenv('.env') #load dotenv for sensitive information purposes

#connect to database
try:
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('USER'),
        password=os.getenv('PASSWORD'),
        host=os.getenv('HOST'),
        port=os.getenv('PORT')
    )
    print("Connected to database.")
except:
    print ("Unable to connect to database.")

#connect to spotify api
cid = os.getenv('SPOTIFY_CID')
secret = os.getenv('SPOTIFY_SECRET')

client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

#initialize bot
bot = commands.Bot(command_prefix='!')


#register command
@bot.command(name = "login")
async def login(ctx):
    cur = conn.cursor() #make cursor to establish connection

    #display records before inserting
    print("From 'users' table:")
    cur.copy_to(sys.stdout, 'users', sep='\t')

    #statement to insert record
    cur.execute(
        """INSERT INTO users (discordid, username) 
        SELECT %s, %s
        WHERE NOT EXISTS ( 
            SELECT * 
            FROM users as u 
            WHERE u.discordid= %s)""", (ctx.author.id, ctx.author.name, ctx.author.id)
        )

    print("\nAfter insertion...\n")

    # print records after insertion
    print("From 'users' table:")
    cur.copy_to(sys.stdout, 'users', sep='\t')

    await(ctx.send("User info successfully logged/found."))
    await(ctx.send("username: " + ctx.author.name))
    await(ctx.send("discord id: " + str(ctx.author.id)))
    # print(cur.rowcount, "records inserted.")

    cur.execute("Commit")
    conn.close() #close connection


#add favorite artist command
@bot.command(name="add", help="Add your favorite artists")
async def add(ctx, artist: str):
    cur = conn.cursor() #make cursor to establish connection
    artist = artist.lower()

    # #check if artist is on spotify
    results = sp.search(artist)
    item_count = results['tracks']['items']
    if (len(item_count) > 0): #if found on spotify
        pass
    else:
        await ctx.send("Invalid Artist")
        return

    #display artists before inserting
    print("From 'artists' table:")
    cur.copy_to(sys.stdout, 'artists', sep='\t')

    #statement to insert artist
    cur.execute(
        """INSERT INTO artists (name) 
        SELECT %s
        WHERE NOT EXISTS ( 
            SELECT * 
            FROM artists as a 
            WHERE a.name= %s)""", (str(artist), str(artist))
        )
    
    print("\nAfter insertion...\n")

    #print artists after insertion
    print("From 'artists' table:")
    cur.copy_to(sys.stdout, 'artists', sep='\t')
    
    cur.execute("Commit")
    await(ctx.send("Artist successfully added."))
    await(ctx.send("artist name: " + artist))

    #display favorites before inserting
    print("\nFrom 'favorites' table:")
    cur.copy_to(sys.stdout, 'favorites', sep='\t')

    #statement to insert favorite
    cur.execute("SELECT artistid FROM artists WHERE name = %s", (artist,))
    id = cur.fetchall() #obtain corresponding id of input artist

    print(type(id))

    cur.execute("SELECT * FROM favorites WHERE (artistid, discordid) = (%s, %s)", (id, ctx.author.id,))
    match = cur.fetchall()

    if(len(match) == 0):
        cur.execute("INSERT INTO favorites (artistid, discordid) VALUES (%s, %s)", (list(id), ctx.author.id))
        await ctx.send("Artist successfully favored.")
    else:
        await ctx.send("Artist already favored.")

    print("\nAfter insertion...\n")

    #print favorites after insertion
    print("From 'favorites' table:")
    cur.copy_to(sys.stdout, 'favorites', sep='\t')

    await(ctx.send("Artist successfully favored."))
    #rows_affected=cur.rowcount
    #print(str(rows_affected) + " records inserted.")

    cur.execute("Commit")
    conn.close() #close connection


@bot.command(name="displayartists", help="Display your list of favorite artists")
async def displayartists(ctx):
    cur = conn.cursor() #make cursor to establish connection
    await(ctx.send("Your Favorite Artists:"))
    cur.execute("Select * from artists")
    results = cur.fetchall()
    for i in results:
        await(ctx.send(i))
    await ctx.send("End of list.")


@bot.command(name="displayfavorites")
async def displayfavorites(ctx):
    cur = conn.cursor() #make cursor to establish connection
    await(ctx.send("Your Favorite Artists:"))
    cur.execute("Select * from favorites")
    results = cur.fetchall()
    for i in results:
        await(ctx.send(i))
    

@bot.command(name="delete", help="delete artist from favorites")
async def delete(ctx, artist: str):
    cur = conn.cursor() #make cursor to establish connection
    artist = artist.lower()

    cur.execute("SELECT artistid FROM artists WHERE name = %s", (artist,))
    results = cur.fetchall()

    if (len(results) > 0):
        cur.execute("DELETE FROM artists where artistid =(%s)", (list(results)))
        await ctx.send("Artist removed from your favorites.")
    else:
        await ctx.send("Artist does not/no longer exists in your favorites.")
        await ctx.send("Use command !displayartists to view your favorite artists list.")

    cur.execute("Commit")
    conn.close()


@bot.command(name="new", help="Look for new song release by artist")
async def new(ctx, artist: str):
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

#opening personal token file
with open("BOT_TOKEN.txt", "r") as token_file:
    TOKEN = token_file.read()
    print("Token file read.\n")
    bot.run(TOKEN)