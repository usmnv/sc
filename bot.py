import asyncio
import logging
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import init_db

from handlers import start, admission, exchange, guide, faq, manager

logging.basicConfig(level=logging.INFO)

# ========== ПРОСТОЙ WEB-СЕРВЕР ДЛЯ HEALTHCHECK (НУЖЕН ДЛЯ AMVERA) ==========
class HealthHandler(BaseHTTPRequestHandler):
    """Обрабатывает GET запросы для проверки работоспособности"""
    
    def do_GET(self):
        if self.path == '/health' or self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def log_message(self, format, *args):
        # Отключаем логи healthcheck сервера, чтобы не засоряли вывод
        pass

def run_health_server():
    """Запускает HTTP сервер на порту 80 для healthcheck"""
    server = HTTPServer(('0.0.0.0', 80), HealthHandler)
    logging.info("Healthcheck сервер запущен на порту 80")
    server.serve_forever()

# ========== ОСНОВНОЙ БОТ ==========
async def main():
    # Инициализация базы данных
    await init_db()
    logging.info("База данных инициализирована")
    
    # Создаем бота и диспетчер
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Подключаем все роутеры (обработчики команд)
    dp.include_router(start.router)
    dp.include_router(admission.router)
    dp.include_router(exchange.router)
    dp.include_router(guide.router)
    dp.include_router(faq.router)
    dp.include_router(manager.router)
    
    # Запускаем healthcheck сервер в отдельном потоке (нужен для Amvera)
    health_thread = Thread(target=run_health_server, daemon=True)
    health_thread.start()
    
    # Запускаем бота в режиме Long Polling
    logging.info("Бот запущен и готов к работе!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())