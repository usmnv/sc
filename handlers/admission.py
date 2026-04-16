from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database import (
    get_all_programs, get_universities_by_program,
    get_universities_by_city, get_all_universities,
    get_cities_list
)
from keyboards import (
    programs_keyboard, city_choice_keyboard,
    university_list_keyboard, back_to_main_button
)
from states import CitySearch

router = Router()

# Соответствие кодов программ ID в БД
PROGRAM_CODE_TO_ID = {
    "1_4": 1,
    "1_3": 2,
    "bach_4": 3,
    "mag": 4,
    "lang_1": 5,
}

@router.callback_query(F.data == "menu_admission")
async def admission_menu(callback: CallbackQuery):
    programs = await get_all_programs()
    await callback.message.edit_text(
        "🎓 *Выбери программу обучения:*\n\n"
        "• 1+4 — языковой год + бакалавриат\n"
        "• 1+3 — ускоренный бакалавриат\n"
        "• Бакалавриат 4 года — нужен HSK\n"
        "• Магистратура — нужен HSK 4+\n"
        "• 1 год языкового — только язык",
        parse_mode="Markdown",
        reply_markup=programs_keyboard(programs)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("prog_"))
async def program_selected(callback: CallbackQuery, state: FSMContext):
    program_code = callback.data.split("_")[1]
    program_id = PROGRAM_CODE_TO_ID.get(program_code)
    
    if not program_id:
        await callback.answer("Ошибка: программа не найдена")
        return
    
    await state.update_data(program_code=program_code, program_id=program_id)
    
    cities = await get_cities_list()
    await callback.message.edit_text(
        f"📍 Выбери город или найди по названию:",
        reply_markup=city_choice_keyboard(cities)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("city_"))
async def city_selected(callback: CallbackQuery, state: FSMContext):
    city = callback.data.split("_", 1)[1]
    data = await state.get_data()
    program_code = data.get("program_code")
    program_id = data.get("program_id")
    
    universities = await get_universities_by_program(program_id)
    # Фильтруем по городу
    filtered = [u for u in universities if u["city"].lower() == city.lower()]
    
    if not filtered:
        await callback.message.answer(f"❌ В городе {city} нет вузов по выбранной программе.")
        return
    
    await show_universities(callback, filtered, program_code)

@router.callback_query(F.data == "city_search")
async def search_city_prompt(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "🔍 *Введи название города*\n\n"
        "Примеры: Пекин, Шанхай, Гуанчжоу, Ханчжоу, Нанкин",
        parse_mode="Markdown"
    )
    await state.set_state(CitySearch.waiting_city_name)
    await callback.answer()

@router.message(CitySearch.waiting_city_name)
async def handle_city_search(message: Message, state: FSMContext):
    city = message.text.strip()
    universities = await get_universities_by_city(city)
    
    if not universities:
        await message.answer(
            f"❌ Город '{city}' не найден.\n\n"
            f"Попробуй другой город или выбери из списка.",
            reply_markup=back_to_main_button()
        )
    else:
        await message.answer(f"🔍 Найдено {len(universities)} вузов в городе {city}:")
        for uni in universities:
            await send_university_card(message, uni)
        await message.answer("Нажми /start чтобы вернуться в главное меню")
    
    await state.clear()

async def show_universities(callback: CallbackQuery, universities: list, program_code: str):
    text = f"🏛 *Найдено {len(universities)} университетов:*\n\n"
    for i, uni in enumerate(universities[:10], 1):
        text += f"{i}. {uni['name_ru']} — {uni['city']}\n"
    
    if len(universities) > 10:
        text += f"\n...и еще {len(universities) - 10} вузов"
    
    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=university_list_keyboard(universities[:20], program_code)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("uni_"))
async def show_university_detail(callback: CallbackQuery):
    uni_id = int(callback.data.split("_")[1])
    
    from database import DB_PATH
    import aiosqlite
    
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM universities WHERE id = ?", (uni_id,))
        uni = await cursor.fetchone()
        
    if uni:
        await send_university_card(callback.message, dict(uni))
    else:
        await callback.answer("Университет не найден")
    
    await callback.answer()

async def send_university_card(message: Message, uni: dict):
    text = (
        f"🏛 *{uni['name_ru']}*\n"
        f"📖 *Китайское название:* {uni['name_cn']}\n"
        f"📍 *Город:* {uni['city']}\n"
        f"📚 *Программа:* {uni['duration']}\n"
        f"💰 *Стоимость:* {uni['price_per_year']} ¥/год\n\n"
        f"📝 *Описание:*\n{uni['description']}"
    )
    
    if uni['campus_photo_url'] and uni['campus_photo_url'].startswith('http'):
        try:
            await message.answer_photo(uni['campus_photo_url'], caption="🏫 Кампус университета")
        except:
            pass
    
    if uni['dorm_photo_url'] and uni['dorm_photo_url'].startswith('http'):
        try:
            await message.answer_photo(uni['dorm_photo_url'], caption="🛏 Общежитие")
        except:
            pass
    
    await message.answer(text, parse_mode="Markdown")