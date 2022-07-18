# bot.py
from __future__ import print_function
import os
import re
import discord
import time
from gdrive import gdrive
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
BASE_FILENAME = os.getenv('BASE_FILENAME')
client = discord.Client()
voiceChannel = discord.VoiceChannel
drive = gdrive()

##### REGEX STATEMENTS #####
gwebm = re.compile('!WEBM')
rwebm = re.compile('!RANDOMWEBM')
upl = re.compile('!UPLOAD')
gwav = re.compile('!WAV')
rwav = re.compile('!RANDOMWAV')
pwav = re.compile('!PLAY')
##### REGEX STATEMENTS END #####

##### WAV FUNCTIONS #####

# retrieves a shareable link to a wav file within the google drive with given filename
#
async def get_wav(message):
    args = message.content.split()
    fileName = args[1]
    fileLocation = BASE_FILENAME + fileName + '.wav'
    if os.path.isfile(fileLocation):
        await message.channel.send(file=discord.File(fileLocation))
    else:
        file = drive.download_file(fileName.lower(), 'wav')
        if file == 0:
            await message.channel.send('FILE NOT FOUND')
        else:
            await message.channel.send(file=discord.File(fileLocation))

# retrieves a shareable link to a random wav file within the google drive
#
async def random_wav(message):
    await message.channel.send(drive.random_file('wav'))

# downloads a given wav file, joins a given voice channel, and plays the wav file
#
async def play_wav(message):
    args = message.content.split()
    fileName = args[1]
    fileLocation = BASE_FILENAME + fileName + '.wav'
    if os.path.isfile(fileLocation):
        voiceChannel = await client.guilds[0].voice_channels[int(args[2])].connect()
        time.sleep(.1)
        voiceChannel.play(discord.FFmpegPCMAudio(fileLocation))
        while voiceChannel.is_playing():
            pass
        await voiceChannel.disconnect()
    else:
        file = drive.download_file(args[2].lower(), 'wav')
        if file == 0:
            await message.channel.send('FILE NOT FOUND')
        else:
            voiceChannel = await client.guilds[0].voice_channels[int(args[2])].connect()
            time.sleep(.1)
            voiceChannel.play(discord.FFmpegPCMAudio(fileLocation))
            while voiceChannel.is_playing():
                pass
            await voiceChannel.disconnect()

##### WEBM FUNCTIONS #####

# retrieves a shareable link to a webm file within the google drive with given filename
#
async def get_webm(message):
        args = message.content.split()
        fileName = args[1]
        file = drive.retrieve_file(fileName +'.webm', 'webm')
        if file == 0:
            await message.channel.send('FILE NOT FOUND')
        else:
            await message.channel.send(file)

#retrieves a shareable link to a random webm file within the google drive 
#
async def random_webm(message):
    await message.channel.send(drive.random_file('webm'))

##### FILE MANAGEMENT FUNCTIONS #####

# retrieves attached media and uploads it to the google drive with current filename
#
async def upload_media(message):
    if message.attachments:
        await message.attachments[0].save(BASE_FILENAME + message.attachments[0].filename)
        drive.upload_file(message.attachments[0].filename.lower(), 'wav')
    else: await message.channel.send('FILE NOT UPLOADED')

# triggers on client.run, clarifies guild access
#
@client.event
async def on_ready():
    for guild in client.guilds:
            if guild.name == GUILD:
                    break
    print(
            f'{client.user} is connected to the following guild :\n'
            f'{guild.name}(id: {guild.id})'
    )
# triggers when a message is edited with bots scope
#
@client.event
async def on_message_edit(before, after):
    if after.author == client.user:
        return
    if(before.content != after.content):
        await before.channel.send(before.author.name + ' has edited their message:\n' + before.content)

# triggers when a message is posted within bots scope
#
@client.event    
async def on_message(message):
    
    if message.author == client.user:
        return
            
    messageUppercase = message.content.upper()        

    if gwebm.search(messageUppercase):
        await get_webm(message)

    elif rwebm.search(messageUppercase):
        await random_webm(message)

    elif gwav.search(messageUppercase):
        await get_wav(message)

    elif rwav.search(messageUppercase):
        await random_wav(message)

    elif pwav.search(messageUppercase):
        await play_wav(message)

    elif upl.search(messageUppercase):
        await upload_media(message)

            
client.run(TOKEN)
