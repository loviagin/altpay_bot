from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import logging

from db import get_order, update_order, get_all_orders
from states import OrderStates

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    logger.info(f"📥 Получена команда /start от {message.from_user.id if message.from_user else 'unknown'}")
    args = message.text.split() if message.text else []
    if len(args) > 1 and args[1].startswith("order_"):
        order_id = args[1].split("_")[1]
        order = await get_order(order_id)
        if order:
            await state.update_data(order_id=order_id)
            await message.answer(
                f"Заявка #{order_id}\nСумма: ${order['amount']}\nСервис: {order['service']}\nК оплате: {order['price']} руб."
            )
            await message.answer("Введите ваше имя:")
            await state.set_state(OrderStates.waiting_for_name)
            return

    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text="📝 Новая заявка")
    keyboard.button(text="📦 Статус заявки")
    keyboard.button(text="❓ Помощь")
    await message.answer(
        "Добро пожаловать в AltPay! Выберите действие:",
        reply_markup=keyboard.as_markup(resize_keyboard=True)
    )
    logger.info(f"✅ Отправлен ответ на /start")

@router.message(Command("new"))
async def new_command(message: Message):
    logger.info(f"📥 Получена команда /new от {message.from_user.id if message.from_user else 'unknown'}")
    await message.answer("Для создания новой заявки перейдите на https://altpay.lovigin.com")
    logger.info(f"✅ Отправлен ответ на /new")

@router.message(Command("status"))
async def status_command(message: Message):
    logger.info(f"📥 Получена команда /status от {message.from_user.id if message.from_user else 'unknown'}")
    await message.answer("Введите номер вашей заявки для проверки статуса:")
    logger.info(f"✅ Отправлен ответ на /status")

@router.message(Command("help"))
async def help_command(message: Message):
    logger.info(f"📥 Получена команда /help от {message.from_user.id if message.from_user else 'unknown'}")
    await message.answer(
        "🛠 AltPay Bot — помощник для оплаты зарубежных сервисов.\n\n"
        "🔹 /new — создать новую заявку\n"
        "🔹 /status — проверить статус заявки\n"
        "🔹 /person — Позвать оператора\n\n"
        "Подробнее: https://altpay.lovigin.com"
    )
    logger.info(f"✅ Отправлен ответ на /help")

@router.message(Command("key"))
async def fetch_orders(message: Message):
    logger.info(f"📥 Получена команда /key от {message.from_user.id if message.from_user else 'unknown'}")
    data = await get_all_orders()
    text = "\n\n".join(
        [f"#{o['_id']} • ${o.get('amount')} • {o.get('service')} • {o.get('name')} • {o.get('method')} • {o.get('contact')} • {o.get('status')}" for o in data]
    ) or "Нет заявок."
    await message.answer(text)
    logger.info(f"✅ Отправлен ответ на /key")

@router.message(OrderStates.waiting_for_name)
async def get_name(message: Message, state: FSMContext):
    logger.info(f"📥 Получено имя от {message.from_user.id if message.from_user else 'unknown'}: {message.text}")
    data = await state.get_data()
    await update_order(data["order_id"], {"name": message.text})
    await message.answer("Укажите удобный способ перевода (карта, СБП, SWIFT):")
    await state.set_state(OrderStates.waiting_for_payment_method)

@router.message(OrderStates.waiting_for_payment_method)
async def get_method(message: Message, state: FSMContext):
    logger.info(f"📥 Получен способ оплаты от {message.from_user.id if message.from_user else 'unknown'}: {message.text}")
    data = await state.get_data()
    await update_order(data["order_id"], {"method": message.text})
    await message.answer("Оставьте Telegram или email для связи:")
    await state.set_state(OrderStates.waiting_for_contact)

@router.message(OrderStates.waiting_for_contact)
async def get_contact(message: Message, state: FSMContext):
    logger.info(f"📥 Получен контакт от {message.from_user.id if message.from_user else 'unknown'}: {message.text}")
    data = await state.get_data()
    await update_order(data["order_id"], {
        "contact": message.text,
        "status": "заполнена"
    })
    await message.answer("Спасибо! Заявка передана в обработку. Мы свяжемся с вами в ближайшее время.")
    await state.clear()