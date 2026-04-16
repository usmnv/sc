import sqlite3
import aiosqlite
import os
from typing import List, Dict, Optional

# ========== НАСТРОЙКА ПУТИ К БАЗЕ ДАННЫХ ==========
# Создаем папку data, если её нет (нужно для Amvera)
DB_DIR = "data"
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

DB_PATH = os.path.join(DB_DIR, "china_study.db")

# ========== ИНИЦИАЛИЗАЦИЯ БД ==========
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        # Таблица пользователей
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_id INTEGER UNIQUE,
                name TEXT,
                phone TEXT,
                city TEXT,
                goal TEXT,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица программ обучения
        await db.execute('''
            CREATE TABLE IF NOT EXISTS programs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE,
                name TEXT,
                description TEXT
            )
        ''')
        
        # Таблица университетов
        await db.execute('''
            CREATE TABLE IF NOT EXISTS universities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name_ru TEXT,
                name_cn TEXT,
                city TEXT,
                program_id INTEGER,
                description TEXT,
                dorm_photo_url TEXT,
                campus_photo_url TEXT,
                price_per_year INTEGER,
                duration TEXT,
                FOREIGN KEY(program_id) REFERENCES programs(id)
            )
        ''')
        
        # Таблица FAQ
        await db.execute('''
            CREATE TABLE IF NOT EXISTS faq (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                question TEXT,
                answer TEXT
            )
        ''')
        
        # Таблица для гида (статьи)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS guide_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT,
                image_url TEXT,
                order_num INTEGER
            )
        ''')
        
        await db.commit()
        
        # Заполняем начальными данными, если пусто
        await seed_data()

async def seed_data():
    async with aiosqlite.connect(DB_PATH) as db:
        # Проверяем, есть ли программы
        cursor = await db.execute("SELECT COUNT(*) FROM programs")
        count = (await cursor.fetchone())[0]
        
        if count == 0:
            # Программы обучения
            programs = [
                ("1_4", "1+4", "1 год языковой подготовки + 4 года бакалавриата"),
                ("1_3", "1+3", "1 год языковой подготовки + 3 года бакалавриата (ускоренный)"),
                ("bach_4", "Бакалавриат 4 года", "Прямое поступление на бакалавриат (требуется HSK)"),
                ("mag", "Магистратура", "2 года магистратуры (требуется HSK 4+)"),
                ("lang_1", "1 год языкового курса", "Только языковая подготовка, без поступления на основную программу"),
            ]
            await db.executemany("INSERT INTO programs (code, name, description) VALUES (?, ?, ?)", programs)
            
            # Университеты (фото пока пустые - добавишь позже через админку или вручную)
            universities = [
                ("Пекинский университет", "北京大学", "Пекин", 1, "Один из лучших университетов Китая. Сильные программы по гуманитарным и естественным наукам.", "", "", 28000, "1+4"),
                ("Пекинский университет", "北京大学", "Пекин", 3, "Бакалавриат в Пекинском университете", "", "", 30000, "4 года"),
                ("Университет Цинхуа", "清华大学", "Пекин", 1, "Ведущий технический вуз Китая. Инженерия, IT, бизнес.", "", "", 29000, "1+4"),
                ("Шанхайский университет Цзяо Тун", "上海交通大学", "Шанхай", 1, "Один из старейших университетов Китая. Медицина, инженерия, экономика.", "", "", 27000, "1+4"),
                ("Фуданьский университет", "复旦大学", "Шанхай", 3, "Элитный университет. Гуманитарные науки, экономика, менеджмент.", "", "", 31000, "4 года"),
                ("Чжэцзянский университет", "浙江大学", "Ханчжоу", 1, "Комплексный университет. Хорошие программы по IT и биотехнологиям.", "", "", 26000, "1+4"),
                ("Нанкинский университет", "南京大学", "Нанкин", 4, "Магистерские программы по гуманитарным и естественным наукам", "", "", 25000, "2 года"),
                ("Пекинский университет языка и культуры", "北京语言大学", "Пекин", 5, "Специализированный языковой университет. Лучший выбор для изучения китайского.", "", "", 22000, "1 год"),
            ]
            await db.executemany('''
                INSERT INTO universities (name_ru, name_cn, city, program_id, description, dorm_photo_url, campus_photo_url, price_per_year, duration)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', universities)
            
            # FAQ
            faq_items = [
                ("Регистрация WeChat", "Как зарегистрироваться в WeChat?", "1. Скачай приложение WeChat\n2. Введи номер телефона\n3. Подтверди кодом\n4. Если требуется приглашение от пользователя из Китая - обратись к менеджеру\n5. После регистрации привяжи банковскую карту для WeChat Pay"),
                ("Регистрация Alipay", "Как завести Alipay?", "1. Скачай Alipay\n2. Выбери 'International version'\n3. Зарегистрируйся по номеру телефона\n4. Добавь иностранную карту (Visa/Mastercard)\n5. Пройди верификацию по паспорту"),
                ("HSK требования", "Какой уровень HSK нужен?", "• Для языкового курса: не требуется\n• Для бакалавриата: HSK 4-5\n• Для магистратуры: HSK 5-6\n• Для технических специальностей: может быть ниже"),
                ("Виза", "Как получить студенческую визу (X1/X2)?", "1. Получи приглашение от университета (JW202)\n2. Запишись в посольство Китая\n3. Собери пакет документов: паспорт, фото, приглашение, медсправка\n4. Оплати визовый сбор\n5. Виза X1 (>180 дней) требует медосмотра в Китае"),
                ("Стоимость жизни", "Сколько стоит жизнь в Китае?", "• Пекин/Шанхай: 4000-7000 ¥/мес\n• Другие города: 2500-4500 ¥/мес\nВключает: общежитие (~1500 ¥), еда (~1500 ¥), транспорт (~200 ¥), связь (~100 ¥)"),
            ]
            await db.executemany("INSERT INTO faq (category, question, answer) VALUES (?, ?, ?)", faq_items)
            
            # Статьи гида
            guide_articles = [
                ("Как открыть банковский счет", "В Китае можно открыть счет в ICBC, Bank of China, China Construction Bank. Нужен паспорт, виза и номер телефона. Процесс занимает 30-60 минут.", "", 1),
                ("Мобильная связь", "Крупные операторы: China Mobile, China Unicom, China Telecom. Тарифы от 50 ¥/мес с 30-50 ГБ трафика.", "", 2),
                ("Транспорт", "Метро, автобусы, Didi (аналог Uber). Для метро можно купить транспортную карту или оплачивать Alipay/WeChat.", "", 3),
                ("Приложения для жизни", "WeChat (общение и оплата), Alipay (оплата), Didi (такси), Meituan (еда), Taobao (покупки), Baidu Maps (навигация на китайском).", "", 4),
            ]
            await db.executemany("INSERT INTO guide_articles (title, content, image_url, order_num) VALUES (?, ?, ?, ?)", guide_articles)
            
            await db.commit()

# ========== РАБОТА С ПОЛЬЗОВАТЕЛЯМИ ==========
async def user_exists(tg_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT id FROM users WHERE tg_id = ?", (tg_id,))
        return await cursor.fetchone() is not None

async def register_user(tg_id: int, name: str, phone: str, city: str, goal: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO users (tg_id, name, phone, city, goal) VALUES (?, ?, ?, ?, ?)",
            (tg_id, name, phone, city, goal)
        )
        await db.commit()

async def get_user(tg_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT * FROM users WHERE tg_id = ?", (tg_id,))
        return await cursor.fetchone()

# ========== РАБОТА С ПРОГРАММАМИ ==========
async def get_all_programs() -> List[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM programs ORDER BY id")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

# ========== РАБОТА С УНИВЕРСИТЕТАМИ ==========
async def get_universities_by_program(program_id: int) -> List[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM universities WHERE program_id = ? ORDER BY city, name_ru",
            (program_id,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

async def get_universities_by_city(city: str) -> List[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM universities WHERE city LIKE ? ORDER BY name_ru",
            (f"%{city}%",)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

async def get_all_universities() -> List[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM universities ORDER BY city, name_ru")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

async def get_cities_list() -> List[str]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT DISTINCT city FROM universities ORDER BY city")
        rows = await cursor.fetchall()
        return [row[0] for row in rows]

# ========== РАБОТА С FAQ ==========
async def get_all_faq() -> List[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM faq ORDER BY category, id")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

# ========== РАБОТА С ГИДОМ ==========
async def get_guide_articles() -> List[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM guide_articles ORDER BY order_num")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]