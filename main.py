import os
import disnake
from disnake.ext import commands
from utils.databases import UsersDataBase
from disnake import TextInputStyle
from disnake.ext import tasks
import datetime
import time
bot = commands.Bot(command_prefix='!', intents=disnake.Intents.all())
bot.remove_command('help')
@bot.event
async def on_ready():
    await UsersDataBase().create_table()
    print('ready')

for file in os.listdir("./cogs"):
    if file.endswith('.py') and file != 'select.py':  # НЕ грузим select.py
        bot.load_extension(f"cogs.{file[:-3]}")

bot.run('Твой токен')
