# google-bot-pub
A bot that handles Google Drive access

This bot currently has the ability to manage authentication, upload and download files, and create shareable links all of which is triggerd through input from visible discord channels.

AUTHENTICATION:
For the discord guild, create a .env file containing a user generated token(DISCORD_TOKEN), and a title for the guild(DISCORD_GUILD).
You must generate your own credentials for both a google app, and a discord bot to use this bot.
This bot requires the ability to read/send messages, see voice and text channels, and speak in voice channels.

FILE MANAGEMENT:
Files are sourced using built in types and locations.  To add a location, include the target folder ids in the .env file for a .webm folder(WEBM_FOLDER), a .wav folder(WAV_FOLDER), and an uploads folder(UPLOAD_FOLDER). Any or all of these ids can be identical.
Files are downloaded and uploaded from the same folder(BASE_FILENAME). Designate this folder in the .env.

LINK GENERATION:
Links are generated based off of requested files and automatically shared in the same channel they were requested in.

