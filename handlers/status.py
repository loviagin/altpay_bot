from aiogram import Router
from aiogram.types import Message
from db import get_order
import re

router = Router()

@router.message(lambda msg: msg.text == "📦 Статус заявки")
async def ask_for_order_id(message: Message):
    await message.answer("Введите номер вашей заявки (например: 12345):")

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