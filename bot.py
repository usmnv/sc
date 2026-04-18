import asyncio
import logging
import os
import sys
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import init_db

from handlers import start, admission, exchange, guide, faq, manager

logging.basicConfig(level=logging.INFO)

class HealthHandler(BaseHTTPRequestHandler):
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
        pass

def run_health_server():
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    logging.info(f"Healthcheck сервер запущен на порту {port}")
    server.serve_forever()

async def main():
    try:
        # Инициализация базы данных
        await init_db()
        logging.info("База данных инициализирована")
        
        # Создаем бота и диспетчер
        bot = Bot(token=BOT_TOKEN)
        dp = Dispatcher(storage=MemoryStorage())
        
        # Подключаем все роутеры
        dp.include_router(start.router)
        dp.include_router(admission.router)
        dp.include_router(exchange.router)
        dp.include_router(guide.router)
        dp.include_router(faq.router)
        dp.include_router(manager.router)
        
        # Запускаем healthcheck сервер
        health_thread = Thread(target=run_health_server, daemon=True)
        health_thread.start()
        
        # Запускаем бота
        logging.info("Бот запущен и готов к работе!")
        await dp.start_polling(bot)
        
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
