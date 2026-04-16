from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database import user_exists, register_user, get_user
from keyboards import main_menu_keyboard, back_to_main_button
from states import Registration

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    tg_id = message.from_user.id
    
    if await user_exists(tg_id):
        user = await get_user(tg_id)
        await message.answer(
            f"👋 С возвращением, {user[2]}!\n\n"
            f"Выбери действие:",
            reply_markup=main_menu_keyboard()
        )
    else:
        await message.answer(
            "🎓 *Добро пожаловать в China Study Bot!*\n\n"
            "Я помогу тебе:\n"
            "• Выбрать программу обучения в Китае\n"
            "• Найти подходящий университет\n"
            "• Узнать о жизни в Китае\n"
            "• Получить ответы на частые вопросы\n\n"
            "Давай познакомимся! Как тебя зовут?",
            parse_mode="Markdown"
        )
        await state.set_state(Registration.waiting_name)

@router.message(Registration.waiting_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📱 Отправь номер телефона (можно просто написать)")
    await state.set_state(Registration.waiting_phone)

@router.message(Registration.waiting_phone)
async def process_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("🏙 Из какого ты города?")
    await state.set_state(Registration.waiting_city)

@router.message(Registration.waiting_city)
async def process_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer(
        "🎯 Какую цель ставишь?\n"
        "(например: поступление в бакалавриат, изучение языка, магистратура)"
    )
    await state.set_state(Registration.waiting_goal)

@router.message(Registration.waiting_goal)
async def process_goal(message: Message, state: FSMContext):
    data = await state.get_data()
    tg_id = message.from_user.id
    
    await register_user(
        tg_id=tg_id,
        name=data["name"],
        phone=data["phone"],
        city=data["city"],
        goal=message.text
    )
    
    await message.answer(
        f"✅ Регистрация завершена, {data['name']}!\n\n"
        f"Теперь ты можешь пользоваться всеми функциями бота.",
        reply_markup=main_menu_keyboard()
    )
    await state.clear()

@router.callback_query(F.data == "back_main")
async def back_to_main(callback: CallbackQuery):
    await callback.message.edit_text(
        "🏠 *Главное меню*\n\nВыбери нужный раздел:",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )
    await callback.answer()