from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
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
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text="Spotify")
    keyboard.button(text="Netflix")
    keyboard.button(text="iCloud")
    keyboard.button(text="Apple")
    keyboard.button(text="Google")
    keyboard.button(text="YouTube")
    keyboard.button(text="Notion")
    keyboard.button(text="GitHub")
    keyboard.button(text="Steam")
    keyboard.button(text="Epic Games")
    keyboard.button(text="PlayStation")
    keyboard.button(text="Домены и хостинг")
    keyboard.button(text="AWS")
    keyboard.button(text="Upwork")
    keyboard.button(text="ChatGPT")
    keyboard.button(text="Cursor")
    keyboard.button(text="Claude")
    keyboard.button(text="Udemy")
    keyboard.button(text="Adobe")
    keyboard.button(text="Переводы")
    await message.answer(
        "🧾 Новая заявка.\n\n"
        "Выберите что нужно оплатить или введите название",
        reply_markup=keyboard.as_markup(resize_keyboard=True)
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