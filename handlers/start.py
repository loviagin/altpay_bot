from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from db import get_order, update_order
from states import OrderStates

router = Router()

@router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    args = message.text.split()
    if len(args) > 1 and args[1].startswith("order_"):
        order_id = args[1].split("_")[1]
        order = await get_order(order_id)
        if order:
            await state.update_data(order_id=order_id)
            await message.answer(
                f"Заявка #{order_id}\nСумма: {order['price']} ₽\nСервис: {order['service']}"
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

@router.message(Command("new"))
async def new_command(message: Message):
    await message.answer("Для создания новой заявки перейдите на https://altpay.lovigin.com")

@router.message(Command("status"))
async def status_command(message: Message):
    await message.answer("Введите номер вашей заявки для проверки статуса:")

@router.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "🛠 AltPay Bot — помощник для оплаты зарубежных сервисов.\n\n"
        "🔹 /new — создать новую заявку\n"
        "🔹 /status — проверить статус\n"
        "🔹 /help — помощь\n\n"
        "Подробнее: https://altpay.lovigin.com"
    )

@router.message(OrderStates.waiting_for_name)
async def get_name(message: Message, state: FSMContext):
    data = await state.get_data()
    await update_order(data["order_id"], {"name": message.text})
    await message.answer("Укажите удобный способ перевода (карта, СБП, SWIFT):")
    await state.set_state(OrderStates.waiting_for_payment_method)

@router.message(OrderStates.waiting_for_payment_method)
async def get_method(message: Message, state: FSMContext):
    data = await state.get_data()
    await update_order(data["order_id"], {"method": message.text})
    await message.answer("Оставьте Telegram или email для связи:")
    await state.set_state(OrderStates.waiting_for_contact)

@router.message(OrderStates.waiting_for_contact)
async def get_contact(message: Message, state: FSMContext):
    data = await state.get_data()
    await update_order(data["order_id"], {
        "contact": message.text,
        "status": "заполнена"
    })
    await message.answer("Спасибо! Заявка передана в обработку. Мы свяжемся с вами в ближайшее время.")
    await state.clear()