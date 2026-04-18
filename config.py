import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден!")

MANAGER_CONTACT = os.getenv("MANAGER_CONTACT", "@china_study_manager")
MANAGER_PHONE = os.getenv("MANAGER_PHONE", "+8612345678901")
MANAGER_WHATSAPP = os.getenv("MANAGER_WHATSAPP", "+8612345678901")
MANAGER_CHAT_ID = os.getenv("MANAGER_CHAT_ID", None)
if MANAGER_CHAT_ID:
    MANAGER_CHAT_ID = int(MANAGER_CHAT_ID)

DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Таймауты для API
REQUEST_TIMEOUT = 60
CONNECTION_TIMEOUT = 30
