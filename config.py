import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла (только для локальной разработки)
load_dotenv()

# Токен бота - ОБЯЗАТЕЛЬНАЯ переменная
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError(
        "BOT_TOKEN не найден!\n"
        "Добавь переменную окружения BOT_TOKEN в Amvera или в файл .env"
    )

# Контакты менеджеров (можно переопределить через переменные окружения)
MANAGER_CONTACT = os.getenv("MANAGER_CONTACT", "@china_study_manager")
MANAGER_PHONE = os.getenv("MANAGER_PHONE", "+8612345678901")
MANAGER_WHATSAPP = os.getenv("MANAGER_WHATSAPP", "+8612345678901")

# ID чата менеджера для получения вопросов (опционально)
MANAGER_CHAT_ID = os.getenv("MANAGER_CHAT_ID", None)
if MANAGER_CHAT_ID:
    MANAGER_CHAT_ID = int(MANAGER_CHAT_ID)

# Режим отладки
DEBUG = os.getenv("DEBUG", "False").lower() == "true"