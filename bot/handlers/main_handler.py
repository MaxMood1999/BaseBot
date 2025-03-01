import asyncio
from os import getenv

import socks
import urllib3
from aiogram import html, Router, F
from aiogram.enums import ChatMemberStatus
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardButton, ReplyKeyboardRemove, BotCommand
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv
from sqlalchemy import insert, select, delete

from bot.buttons.reply import admin_panel, back_button, order_buttons
from bot.dispacher import bots
from bot.handlers.functions import handle_follow, handle_like, handle_comment, \
    check_account_status, get_accounts_for_follow, get_working_for_comment, get_working_for_like
from db import db
from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from db.models import AccountData, Worked

load_dotenv()

PROXY = getenv("PROXY_URL")


main_router = Router()

db.init()

class OrderStates(StatesGroup):
    waiting_for_accounts = State()
    waiting_for_username = State()
    waiting_for_count = State()
    waiting_like_count = State()
    waiting_komment_count = State()
    waiting_for_media_link = State()
    waiting_for_com_link = State()
    waiting_for_account_username = State()
    waiting_for_account_password = State()


class AdminFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in {5490986430,6304778368}
#=======ADMIN START ===================================

@main_router.message(F.text == "Ortga qaytish 🔙" , AdminFilter())
@main_router.message(CommandStart() , AdminFilter() )
async def admin_start(message:Message, state:FSMContext):
    await state.clear()
    rkb = await admin_panel()
    await message.reply(text="Hush kelibsiz admin", reply_markup=rkb)
#========AKKAUNTLARNI DATABAZAGA SAQLASH=============================
@main_router.message(F.text == "Akkaunt qoshish🎦", AdminFilter())
async def add_accounts_to_database(message:Message, state:FSMContext):
    await state.set_state(OrderStates.waiting_for_accounts)
    button = await back_button()
    await message.reply(text="""Malumotlarni Jonating 
Qabul qilinadigan format:
username1:password1
username2:password2
username3:password3""", reply_markup=button)

@main_router.message(F.text, OrderStates.waiting_for_accounts)
async def save_accaunt_to_database(message:Message, state:FSMContext):
    try:
        list_form = message.text.split("\n")
        for username in list_form:
            u, b = username.split(":")
            print(u,b)

            await AccountData.create(username=u, password=b)

        main_kb = await admin_panel()
        await message.answer("Akkaunt muvaffaqiyatli qo'shildi!", reply_markup=main_kb)
        await state.clear()
    except Exception as e:
        print(f"{e} malumot togri kelmadi")
        await state.clear()


@main_router.message(F.text== "Buyurtma berish 📢")
async def process_order(message:Message):
    buttons = await order_buttons()
    await message.answer("Qaysi turdagi buyurtma kerak?", reply_markup=buttons)

#==============Obuna===================

@main_router.message(F.text == "Obuna")
async def process_follow(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Iltimos, foydalanuvchi nomini kiriting:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(OrderStates.waiting_for_username)

@main_router.message(OrderStates.waiting_for_username)
async def process_follow_username(message: types.Message, state: FSMContext):
    await state.update_data(username=message.text)
    await message.answer("Nechta obuna kerak?:")
    await state.set_state(OrderStates.waiting_for_count)

@main_router.message(lambda message: message.text.isdigit(), OrderStates.waiting_for_count)
async def process_follow_count(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    count = int(message.text)

    account = await get_accounts_for_follow(user_data["username"], count, PROXY)

    if not account:
        await message.answer("Amalyot bajarilmadi!")
        await state.clear()
        return

    main_kb = await admin_panel()
    await message.answer(f"{account} ta obuna muvaffaqiyatli qo'yildi!", reply_markup=main_kb)
    await state.clear()



#=================Like====================
@main_router.message(F.text == "Like")
async def process_like(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Iltimos, media linkini kiriting:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(OrderStates.waiting_for_media_link)

@main_router.message(OrderStates.waiting_for_media_link)
async def process_like_link(message: types.Message, state: FSMContext):
    await state.update_data(waiting_for_media_link=message.text)
    await message.answer("Nechta like kerak?:")
    await state.set_state(OrderStates.waiting_like_count)


@main_router.message(lambda message: message.text.isdigit(),OrderStates.waiting_like_count)
async def process_like_count(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    count = int(message.text)
    main_kb = await admin_panel()
    account = await get_working_for_like(user_data["waiting_for_media_link"],count, PROXY)
    if not account:
        await message.answer("Xatolik yuz berdi, qayta urinib ko'ring.", reply_markup=main_kb)
        await state.clear()
        return



    await message.answer(f"{account} ta like muvaffaqiyatli qo'yildi!", reply_markup=main_kb)


@main_router.message(F.text == "Komment")
async def process_comment(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Iltimos, media linkini kiriting:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(OrderStates.waiting_for_com_link)

@main_router.message(OrderStates.waiting_for_com_link)
async def process_comment_text(message: types.Message, state: FSMContext):
    await state.update_data(waiting_for_com_link=message.text)
    await message.answer("Nechta komment kerak? (maks 150 kuniga):")
    await state.set_state(OrderStates.waiting_komment_count)


@main_router.message(lambda message: message.text.isdigit(), OrderStates.waiting_komment_count)
async def process_comment_count(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    count = int(message.text)
    main_kb = await admin_panel()
    account = await get_working_for_comment(user_data["waiting_for_com_link"], count, PROXY)
    if not account:
        await message.answer("Xatolik yuz berdi, qayta urinib ko'ring.", reply_markup=main_kb)
        await state.clear()
        return

    await message.answer(f"{account} ta komment muvaffaqiyatli qo'yildi!", reply_markup=main_kb)




#================statistika=========================
@main_router.message(F.text == "Statistika 🛠")
async def show_stats(message: types.Message):
        print("keldi")
        datas = await check_account_status()

        main_kb = await admin_panel()
        stats = (f"Ishlaydigan akkauntlar: {datas}\n"
                 )
        await message.answer(stats, reply_markup=main_kb)













