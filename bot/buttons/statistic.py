import asyncio
from instagrapi import Client
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Mapped, mapped_column, Session
from sqlalchemy.ext.declarative import declarative_base
import random

from db import db
from db.models import AccountData

db.init()
async def check_account_status(username: str, password: str, proxy: str = None) -> bool:
    cl = Client()
    if proxy:
        cl.set_proxy(proxy)

    try:
        await asyncio.to_thread(cl.login, username, password) # noqa
        await asyncio.to_thread(cl.logout)
        return True
    except Exception as e:
        print(f"{username} tekshiruvda xatolik: {e}")
        return False


async def analyze_accounts(proxy: str = None):

    working_accounts = []
    blocked_accounts = []
    query = select(AccountData)
    acc = await db.execute(query)
    accounts = acc.scalars().all()

    for account in accounts:
            is_working = await check_account_status(account.username, account.password, proxy)
            if is_working:
                working_accounts.append(account.username)
                print(f"{account.username} ishlayapti!")
            else:
                blocked_accounts.append(account.username)
                print(f"{account.username} bloklangan yoki xato!")

            await asyncio.sleep(random.uniform(10, 30))

    return f"""
=== Natijalar ===
Ishlaydigan akkauntlar soni: {len(working_accounts)}
Bloklangan akkauntlar soni: {len(blocked_accounts)}
Umumiy akkauntlar soni: {len(accounts)}
"""
