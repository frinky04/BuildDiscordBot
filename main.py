import discord
import os
import json
import requests
import asyncio
from discord.ext import commands, tasks
from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+ is required

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

last_nightly_build_date = None  # Tracks when the nightly build last ran

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

def check_build_status():
    """Helper function to check the current build status."""
    response = requests.post(
        BUILD_API_URL,
        headers={"Content-Type": "application/json"},
        data=json.dumps({"content": "!status"})
    )
    response_data = response.json()
    return response_data.get("status", "STOPPED")

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    nightly_build.start()  # Start the background nightly build task

@bot.command()
async def build(ctx, arg: str = None):
    if arg != "confirm":
        await ctx.send("Usage: `!build confirm`")
        return

    try:
        status = check_build_status()
        if status == "STOPPED":
            await start_build(ctx)
        else:
            await ctx.send("❌ Build is already in progress")
    except Exception as e:
        await ctx.send(f"❌ Error checking build status: {str(e)}")

@bot.command()
async def status(ctx):
    try:
        status = check_build_status()
        if(status == "STOPPED"):
            await ctx.send("Ready ✅")
        elif(status == "RUNNING"):
            await ctx.send("Running 📦")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

async def start_build(ctx):
    await bot.wait_until_ready()

    if not BUILD_API_URL:
        await ctx.send("❌ Error: Build API URL is not set. Contact the administrator.")
        return

    try:
        response = requests.post(
            BUILD_API_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps({"content": "!start"})
        )

        if response.status_code != 200:
            await ctx.send(f"❌ Failed to start build: {response.status_code} - {response.text}")
        else:
            await ctx.send("✅ Build started successfully.")
    except Exception as e:
        await ctx.send(f"❌ Error starting build: {str(e)}")

@tasks.loop(minutes=1)
async def nightly_build():
    global last_nightly_build_date
    now = datetime.now(ZoneInfo("America/New_York"))
    # If it is 3:00am EST and we haven't run the nightly build yet today
    if now.hour == 3 and now.minute == 0:
        if last_nightly_build_date != now.date():
            try:
                status = check_build_status()
                if status == "STOPPED":
                    channel = bot.get_channel(int(NIGHTLY_BUILD_CHANNEL))
                    if channel:
                        await channel.send("🤖 Automated nightly build starting")
                        await start_build(channel)
                        last_nightly_build_date = now.date()
                    else:
                        print("Nightly build channel not found.")
                else:
                    print("Build is already in progress. Skipping nightly build.")
            except Exception as e:
                print("Error during nightly build check:", e)

# Load secrets and tokens
secrets = load_secrets()
DISCORD_TOKEN = secrets.get("DISCORD_TOKEN")
BUILD_API_URL = secrets.get("BUILD_API_URL")
NIGHTLY_BUILD_CHANNEL = 1133267820042530907  # This doesn't need to be a secret

if not DISCORD_TOKEN:
    DISCORD_TOKEN = input("Please enter your Discord token: ").strip()
    with open("secrets.txt", "a") as file:
        file.write(f"\nDISCORD_TOKEN={DISCORD_TOKEN}")

if not BUILD_API_URL:
    BUILD_API_URL = input("Please enter your build API URL: ").strip()
    with open("secrets.txt", "a") as file:
        file.write(f"\nBUILD_API_URL={BUILD_API_URL}")

bot.run(DISCORD_TOKEN)
