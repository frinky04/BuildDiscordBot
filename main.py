import discord
import os
import json
import requests
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

build_confirmation = False

# Load secrets
def load_secrets():
    secrets = {}
    try:
        with open("secrets.txt", 'r') as file:
            for line in file:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    secrets[key] = value
    except FileNotFoundError:
        print("Secrets file not found!")
    return secrets

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.command()
async def build(ctx):
    global build_confirmation
    build_confirmation = True
    await ctx.send('⚠️ Please use `!confirm` to confirm the build')

@bot.command()
async def confirm(ctx):
    global build_confirmation
    if build_confirmation:
        build_confirmation = False
        await start_build(ctx)
    else:
        await ctx.send('❌ Please use `!build` to start the build process')

async def start_build(ctx):
    await bot.wait_until_ready()
    await ctx.send('🚀 Starting build...')

    if not BUILD_API_URL:
        await ctx.send("❌ Error: Build API URL is not set. Contact the administrator.")
        return

    try:
        response = requests.post(
            BUILD_API_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps({"content": "!start"})
        )

        if response.status_code == 200:
            await ctx.send("✅ Build successfully started!")
        else:
            await ctx.send(f"❌ Failed to start build: {response.status_code} - {response.text}")

    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")



secrets = load_secrets()
DISCORD_TOKEN = secrets.get("DISCORD_TOKEN")
BUILD_API_URL = secrets.get("BUILD_API_URL")

if not DISCORD_TOKEN:
    DISCORD_TOKEN = input('Please enter your Discord token: ').strip()
    with open('secrets.txt', 'a') as file:
        file.write(f'\nDISCORD_TOKEN={DISCORD_TOKEN}')

if not BUILD_API_URL:
    BUILD_API_URL = input('Please enter your build API URL: ').strip()
    with open('secrets.txt', 'a') as file:
        file.write(f'\nBUILD_API_URL={BUILD_API_URL}')

bot.run(DISCORD_TOKEN)
