import asyncio
import logging
import sys

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode


from utils.config import CF as cf
from bot.handlers import dp
import asyncio





async def main() -> None:
    bot = Bot(token=cf.bot.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())