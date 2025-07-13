from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
KEY = os.getenv("KEY_ALL_ORDERS")
KEY_SEND = os.getenv("KEY_SEND")
ADMIN_ID = os.getenv("ADMIN_CHAT_ID")