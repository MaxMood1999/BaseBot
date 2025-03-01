from aiogram import Dispatcher, Bot

from utils.config import CF as conf

TOKEN = conf.bot.TOKEN



dp = Dispatcher()
bots = Bot(token=TOKEN)

