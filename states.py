from aiogram.fsm.state import StatesGroup, State

class OrderStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_payment_method = State()
    waiting_for_contact = State()