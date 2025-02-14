import discord
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
    await ctx.send('⚠️ Please use `!confirm` to confirm the build ⚠️')
    
@bot.command()
async def confirm(ctx):
    global build_confirmation
    if build_confirmation:
        build_confirmation = False
        await start_build()
    else:
        await ctx.send('❌ Please use `!build` to start the build process ❌')
    
async def start_build():
    
    await bot.wait_until_ready()
    channel = bot.get_channel(833979386450398830)
    await channel.send('🚀 Starting build 🚀')



# bot.run('MTMzOTc5Mzg2NDUwMzk4ODMwNA.GYrP7s.Elcw_BWSekNNaqgEmSyR5IzWHzGl9NjlmH91pQ')
# leaked the token, but its fine, i reset it already