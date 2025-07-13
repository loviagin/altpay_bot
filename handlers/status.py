from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from db import get_order
import re
import random

from states import OrderStates

router = Router()

@router.message(lambda msg: msg.text == "📦 Статус заявки")
async def ask_for_order_id(message: Message):
    await message.answer("Введите номер вашей заявки (например: 12345):")

@router.message(lambda msg: msg.text == "❓ Помощь")
async def ask_for_help(message: Message):
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text="Позвать оператора")
    await message.answer(
        "🛠 AltPay Bot — помощник для оплаты зарубежных сервисов.\n\n"
        "🔹 /new — создать новую заявку\n"
        "🔹 /status — проверить статус заявки\n"
        "Подробнее: https://altpay.lovigin.com",
        reply_markup=keyboard.as_markup(resize_keyboard=True)
    )

@router.message(lambda msg: msg.text == "📝 Новая заявка")
async def ask_for_new_order(message: Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Spotify"), KeyboardButton(text="Netflix")],
            [KeyboardButton(text="iCloud"), KeyboardButton(text="Apple")],
            [KeyboardButton(text="Google"), KeyboardButton(text="YouTube")],
            [KeyboardButton(text="Notion"), KeyboardButton(text="GitHub")],
            [KeyboardButton(text="Steam"), KeyboardButton(text="Epic Games")],
            [KeyboardButton(text="PlayStation"), KeyboardButton(text="Домены и хостинг")],
            [KeyboardButton(text="AWS"), KeyboardButton(text="Upwork")],
            [KeyboardButton(text="ChatGPT"), KeyboardButton(text="Cursor")],
            [KeyboardButton(text="Claude"), KeyboardButton(text="Udemy")],
            [KeyboardButton(text="Adobe"), KeyboardButton(text="Переводы")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "🧾 Новая заявка.\n\n"
        "Для ознакомления с ценой вы можете воспользоваться нашим онлайн калькулятором http://alt.lovig.in/#calculator "
        "Выберите что нужно оплатить или введите название", reply_markup=keyboard
    )
    orderid = str(int(1000 + random.random() * 89999))
    await state.update_data(order_id=orderid)
    await state.set_state(OrderStates.waiting_for_service)

@router.message(lambda msg: re.fullmatch(r"\d{5,}", msg.text or ""))
async def process_order_id(message: Message):
    order_id = message.text
    order = await get_order(order_id)

    if order:
        summary = (
            f"🧾 Заявка #{order_id}\n"
            f"Сервис: {order['service']}\n"
            f"Цена: ${order['amount']}\n"
            f"Имя: {order.get('name') or 'не указано'}\n"
            f"Наличие аккаунта: {order.get('account_exist') or 'не указано'}\n"
            f"Доступ к аккаунту: {order.get('account_info') or 'не указано'}\n"
            f"Инструкции: {order.get('instructions') or 'не указано'}\n"
            f"Метод оплаты: {order.get('method') or 'не указано'}\n"
            f"Сумма: {order.get('price') or 'не указано'} руб.\n"
            f"Контакт: {order.get('contact') or 'не указано'}\n"
            f"Статус: {order.get('status') or 'не указан'}"
        )
        await message.answer(summary)
    else:
        await message.answer("Заявка с таким номером не найдена.")