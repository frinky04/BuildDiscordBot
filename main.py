import discord
import sys
import os
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

build_confirmation = False

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
    await ctx.send('🚀 Starting build')


bot.run(os.getenv('DISCORD_TOKEN'))
