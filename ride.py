import asyncio
import logging
import sys
from typing import Any, Dict

from aiogram import Bot, Dispatcher, F, Router, html
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from os import getenv

from dotenv import load_dotenv


from Controllers.BaseController import BaseController
from Controllers.UserController import UserController
from Controllers.DriverController import DriverController

load_dotenv()
TOKEN = getenv("BOT_TOKEN")
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)

router = Router()
baseController = BaseController(html)
userController = UserController(html, bot)

class Contact(StatesGroup):
    contact = State()
    role = State()

class Profile(StatesGroup):
    updateFirstName = State()
    updateLastName = State()
    updatePhone = State()
    updateRole = State()

class Location(StatesGroup):
    currentLocation = State()
    destination = State()

class Options(StatesGroup):
    option = State()
    menu = State()

@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await state.set_state(Contact.contact)
    await userController.start_handler(message)



@router.message(Contact.contact)
async def handle_contact_message(message: Message, state: FSMContext):
    await state.set_state(Contact.role)
    await userController.handle_contact_message(message)

@router.message(Contact.role)
async def role_handler(message: Message, state: FSMContext):
    await userController.role_handler(message)
    await main_menu_handler(message, state)



@router.message(Command("menu"))
async def main_menu_handler(message: Message, state: FSMContext):
    await state.set_state(Options.option)
    print(await userController.user_type(message))
    if await userController.user_type(message) != "Driver":
        await message.answer("Please select an option!",
            reply_markup=ReplyKeyboardMarkup(
                resize_keyboard=True,
                keyboard=[
                    [
                        KeyboardButton(text="Order Ride"),
                        KeyboardButton(text="Show History"),
                    ],
                    [
                        KeyboardButton(text="Profile"),
                    ]
                ],
            ),
        )
    else:
        await message.answer("Please select an option!",
            reply_markup=ReplyKeyboardMarkup(
                resize_keyboard=True,
                keyboard=[
                    [
                        KeyboardButton(text="Profile"),
                        KeyboardButton(text="Show History"),
                    ]
                ],
            ),
        )

@router.message(Command("profile"))
async def update_firstName(message: Message, state: FSMContext):
    await state.set_state(Profile.updateFirstName)
    await message.answer("Please enter your first name", reply_markup=ReplyKeyboardRemove())



@router.message(Options.option)
async def order_ride_handler(message: Message, state: FSMContext):
    print(message.text)
    if message.text == "Order Ride":
        await state.set_state(Location.currentLocation)
        await userController.order_ride_handler(message)
    elif message.text == "Show History":
        await main_menu_handler(message, state)
        await userController.show_history_handler(message)
    elif message.text == "Profile":
        await state.set_state(Profile.updateFirstName)
        await message.answer("Please enter your first name", reply_markup=ReplyKeyboardRemove())




@router.message(Location.currentLocation)
async def handle_location(message: Message, state: FSMContext):
    await state.set_state(Location.destination)
    await userController.current_location_handler(message)

@router.message(Location.destination)
async def handle_location(message: Message, state: FSMContext):
    data = await state.get_data()
    connected = await userController.destination_location_handler(message)
    if connected:
        await state.set_state(Options.option)
        await message.answer("return to main menu",
            reply_markup=ReplyKeyboardMarkup(
                resize_keyboard=True,
                keyboard=[
                    [
                        KeyboardButton(text="/menu"),
                    ]
                ],
            ),
        )

@router.message(Profile.updateFirstName)
async def update_lastName(message: Message, state: FSMContext):
    await state.update_data(firstName=message.text)
    await state.set_state(Profile.updateLastName)
    await message.answer("Please enter your last name")

@router.message(Profile.updateLastName)
async def update_phone(message: Message, state: FSMContext):
    await state.update_data(lastName=message.text)
    await state.set_state(Profile.updatePhone)
    await message.answer("Please enter phone number")

@router.message(Profile.updatePhone)
async def update_role(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(Profile.updateRole)
    await message.answer("Please enter your role",
        reply_markup=ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=[
                [
                    KeyboardButton(text="Driver"),
                    KeyboardButton(text="Passenger"),
                ]
            ],
        ),
    )

@router.message(Profile.updateRole)
async def update_profile(message: Message, state: FSMContext):
    await state.update_data(role=message.text)
    data = await state.get_data()
    await userController.update_profile_handler(message, data)
    await main_menu_handler(message, state)
    # await state.set_state(Options.option)



@router.message(Location.currentLocation)
async def handle_location(message: Message, state: FSMContext):
    await state.set_state(Location.destination)
    await message.answer("Please enter destination")

@router.message(Location.destination)
async def handle_location(message: Message, state: FSMContext):
    await userController.share_location_handler(message)


@router.callback_query(lambda c: c.data in ["accept", "decline"])
async def callback_query_handler(query: Message):
    if await userController.callback_query_handler(query):
        await userController.accept_ride_handler(True)
    else:
        await userController.accept_ride_handler(False)




async def main():
    dp = Dispatcher()
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())