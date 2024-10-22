import discord
from discord.ext import commands, tasks


intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True
intents.voice_states = True 

bot = commands.Bot(command_prefix='!', intents=intents)
block = discord.Status.offline

@bot.event
async def on_ready():
    check_voice_channels.start()

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    member = message.author
    print(f'{member}, {member.status}')
    if isinstance(member, discord.Member):
        if member.status == block:
            await message.delete()
            await message.channel.send(f'{message.author.mention}')

    await bot.process_commands(message)

async def check_status(member):
    try:
        if member.status == block:
            await member.move_to(None)
            return True
        return False
    except discord.Forbidden:
        print(f'Permission error {member.display_name}')


@bot.event
async def on_voice_state_update(member, before, after):
    print(f'{member},{member.status}')
    if after.channel and not before.channel:
        await check_status(member)
    elif before.channel and after.channel == before.channel:
        await check_status(member)

@tasks.loop(seconds=10)
async def check_voice_channels():
    for guild in bot.guilds:
        for channel in guild.voice_channels:
            offline = [member for member in channel.members if member.status == block]
            for member in offline:
                print(f"{member.display_name}, {channel.name}, {member.status}")
                await check_status(member)


bot.run('TOKEN')
