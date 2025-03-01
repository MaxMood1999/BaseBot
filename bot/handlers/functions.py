import asyncio
import random
from os import getenv

from aiogram import html, Router, F
from aiogram.enums import ChatMemberStatus
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardButton, ReplyKeyboardRemove, BotCommand
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv
from sqlalchemy import insert, select, delete, or_, not_
from instagrapi import Client
from bot.buttons.reply import admin_panel, back_button, order_buttons
from bot.dispacher import bots
from db import db
from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from db.models import AccountData, Worked
load_dotenv()
PROXY = getenv("PROXY_URL")
main_router = Router()

db.init()

class ChallengeRequiredError(Exception):
    def __init__(self, challenge_data: dict):
        self.challenge_data = challenge_data
        super().__init__("Challenge tufayli follow amalga oshirilmadi, bot davom etadi.")


async def get_accounts_for_follow(target, count, PROCXY):
    worked_subquery = (
        select(Worked.accounts_id)
        .where(Worked.target != target)
    ).scalar_subquery()
    query = (
        select(AccountData)
        .where(not_(AccountData.id.in_(worked_subquery)))
    )

    result = await db.execute(query)
    accounts= result.scalars().unique().all()

    tasks = [asyncio.create_task(handle_follow(account.id ,account.username, account.password,target, PROCXY)) for account in accounts[:count]]
    await asyncio.gather(*tasks)

    return len(tasks)


async def get_working_for_like(link, count, PROXY):
    accounts = await AccountData.get_all()

    tasks = [asyncio.create_task(handle_follow(account.id, account.username, account.password, link, PROXY)) for
             account in accounts[:count]]
    await asyncio.gather(*tasks)
    return len(tasks)


async def check_account_status() :
    query = await AccountData.get_all()
    return len(query)

def manual_input_code(self, username: str, choice=None):
    return 123456
class CustomClient(Client):
    challenge_code_handler = manual_input_code


async def handle_follow(ids, username: str, password: str, target_username: str, count: int, proxy: str = None):
    cl = CustomClient()
    if proxy:
        cl.set_proxy(proxy)
    try:
        print(username,password,target_username)
        await asyncio.to_thread(cl.login, username, password)
        user_id = cl.user_id_from_username(target_username)
        await asyncio.sleep(6)
        await asyncio.to_thread(cl.user_follow, user_id)
        await asyncio.sleep(random.uniform(25, 33))
        print(f"{target_username} ga follow qilindi!")
        await asyncio.to_thread(cl.logout)
        return True
    except (ChallengeRequiredError , Exception) as e:
        await AccountData.delete(ids)
        print(e)
        return False

    finally:
        await asyncio.to_thread(cl.logout)


async def handle_like(username: str, password: str, post_url: str, count: int, proxy: str = None):
    cl = Client()
    if proxy:
        cl.set_proxy(proxy)

    try:
        await asyncio.to_thread(cl.login, username, password)
        await asyncio.sleep(random.uniform(5, 6))
        media_pk = cl.media_pk_from_url(post_url)
        media_id = cl.media_id(media_pk)
        await asyncio.to_thread(cl.media_like, media_id)
        await asyncio.sleep(random.uniform(25, 26))
        print(f"Postga like bosildi: {post_url}")
        return True
    except (ChallengeRequiredError, Exception) as e:

        print(e)
        return False
    finally:
        await asyncio.to_thread(cl.logout)

emogi_list = ["😂", "🫡", "😉", "🤣", "😇", "🫠", "👍"]
async def get_working_for_comment(link, count, PROXY):
    accounts = await AccountData.get_all()

    tasks = [asyncio.create_task(handle_follow(account.id, account.username, account.password, link, PROXY)) for
             account in accounts[:count]]
    await asyncio.gather(*tasks)
    return len(tasks)

async def handle_comment(username: str, password: str, post_url: str, comment_text, proxy: str = None):
    cl = Client()
    if proxy:
        cl.set_proxy(proxy)

    try:
        await asyncio.to_thread(cl.login, username, password)
        await asyncio.sleep(random.uniform(4, 6))
        media_pk = cl.media_pk_from_url(post_url)
        media_id = cl.media_id(media_pk)

        await asyncio.to_thread(cl.media_comment, media_id, comment_text)
        await asyncio.sleep(random.uniform(24,26))
        print(f"Postga komment qoldirildi: {post_url}")
        return True
    except (ChallengeRequiredError, Exception) as e:

        print(e)
        return False
    finally:
        await asyncio.to_thread(cl.logout)