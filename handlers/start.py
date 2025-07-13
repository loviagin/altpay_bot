from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
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
            await state.update_data(service=order["service"])
            await state.update_data(price=order["price"])
            await state.update_data(amount=order["amount"])
            await message.answer(
                f"Заявка #{order_id}\nСумма: ${order['amount']}\nСервис: {order['service']}", reply_markup=ReplyKeyboardRemove()
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
    await message.answer("Введите номер вашей заявки для проверки статуса:", reply_markup=ReplyKeyboardRemove())
    logger.info(f"✅ Отправлен ответ на /status")

@router.message(Command("help"))
async def help_command(message: Message):
    logger.info(f"📥 Получена команда /help от {message.from_user.id if message.from_user else 'unknown'}")
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text="Позвать оператора")
    await message.answer(
        "🛠 AltPay Bot — помощник для оплаты зарубежных сервисов.\n\n"
        "🔹 /new — создать новую заявку\n"
        "🔹 /status — проверить статус заявки\n"
        "Подробнее: https://altpay.lovigin.com",
        reply_markup=keyboard.as_markup(resize_keyboard=True)
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
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text="✅ Есть")
    keyboard.button(text="❌ Нет, надо создать")
    await message.answer("Есть ли у Вас уже аккаунт, на который нужно совершить оплату?", reply_markup=keyboard.as_markup(resize_keyboard=True))
    await state.set_state(OrderStates.waiting_for_account_existing)

@router.message(OrderStates.waiting_for_account_existing)
async def account_exist(message: Message, state: FSMContext):
    logger.info(f"📥 Получен ответ о наличии аккаунта о пользователя {message.from_user.id if message.from_user else 'unknown'}: {message.text}")
    data = await state.get_data()

    if message.text == "✅ Есть":
        await update_order(data["order_id"], {"account_exist": True})
        await message.answer("Напишите логин и пароль к аккаунту: ", reply_markup=ReplyKeyboardRemove())
        await state.set_state(OrderStates.waiting_for_account_info)
    else:
        await update_order(data["order_id"], {"account_exist": False})
        await update_order(data["order_id"], {"account_info": "Нужно создать"})
        await message.answer("Сейчас можете предоставить любые дополнительные инструкции или пожелания: ", reply_markup=ReplyKeyboardRemove())
        await state.set_state(OrderStates.waiting_for_additional_info)

@router.message(OrderStates.waiting_for_account_info)
async def account_info(message: Message, state: FSMContext):
    logger.info(f"📥 Получена информация об аккаунте {message.from_user.id if message.from_user else 'unknown'}: {message.text}")
    data = await state.get_data()

    await update_order(data["order_id"], {"account_info": message.text})
    await message.answer("Сейчас можете предоставить любые дополнительные инструкции или пожелания: ", reply_markup=ReplyKeyboardRemove())
    await state.set_state(OrderStates.waiting_for_additional_info)

@router.message(OrderStates.waiting_for_additional_info)
async def account_info(message: Message, state: FSMContext):
    logger.info(f"📥 Получены доп инструкции {message.from_user.id if message.from_user else 'unknown'}: {message.text}")
    data = await state.get_data()

    await update_order(data["order_id"], {"instructions": message.text})

    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text="💳 Карта")
    keyboard.button(text="🧾 СБП")
    keyboard.button(text="₿ Крипта")
    await message.answer("Укажите удобный способ оплаты (карта, СБП, SWIFT):", reply_markup=keyboard.as_markup(resize_keyboard=True))

    await state.set_state(OrderStates.waiting_for_payment_method)

@router.message(OrderStates.waiting_for_payment_method)
async def get_method(message: Message, state: FSMContext):
    logger.info(f"📥 Получен способ оплаты от {message.from_user.id if message.from_user else 'unknown'}: {message.text}")
    data = await state.get_data()
    await update_order(data["order_id"], {"method": message.text})
    contact_button = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Отправить контакт", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await message.answer("Оставьте Telegram или email для связи:", reply_markup=contact_button)
    await state.set_state(OrderStates.waiting_for_contact)

@router.message(OrderStates.waiting_for_contact)
async def get_contact(message: Message, state: FSMContext):
    logger.info(f"📥 Получен контакт от {message.from_user.id if message.from_user else 'unknown'}: {message.text}")
    data = await state.get_data()
    await update_order(data["order_id"], {
        "contact": message.text,
        "status": "В обработке"
    })
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text="📝 Новая заявка")
    keyboard.button(text="📦 Статус заявки")
    keyboard.button(text="❓ Помощь")
    summary = (
        "Спасибо! Заявка передана в обработку. Мы свяжемся с вами в ближайшее время.\n"
        f"🧾 Заявка #{data["order_id"]}\n"
        f"Сервис: {data['service']}\n"
        f"Цена: ${data['amount']}\n"
        f"Имя: {data.get('name') or 'не указано'}\n"
        f"Наличие аккаунта: {data.get('account_exist') or 'не указано'}\n"
        f"Доступ к аккаунту: {data.get('account_info') or 'не указано'}\n"
        f"Инструкции: {data.get('instructions') or 'не указано'}\n"
        f"Метод оплаты: {data.get('method') or 'не указано'}\n"
        f"Сумма: {data.get('price') or 'не указано'} руб.\n"
        f"Контакт: {data.get('contact') or 'не указано'}\n"
    )
    await message.answer(summary, reply_markup=keyboard.as_markup(resize_keyboard=True))
    await state.clear()