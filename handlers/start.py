from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, Contact
from aiogram.fsm.context import FSMContext

from database import user_exists, register_user, get_user
from keyboards import main_menu_keyboard
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
        # Автоматически берем имя из Telegram
        name = message.from_user.first_name
        if message.from_user.last_name:
            name += " " + message.from_user.last_name
        
        await state.update_data(name=name)
        
        # Просим отправить контакт
        await message.answer(
            f"🎓 *Добро пожаловать в China Study Bot, {name}!*\n\n"
            f"Я помогу тебе:\n"
            f"• Выбрать программу обучения в Китае\n"
            f"• Найти подходящий университет\n"
            f"• Узнать о жизни в Китае\n"
            f"• Получить ответы на частые вопросы\n\n"
            f"📱 *Пожалуйста, отправь свой номер телефона*, нажав на кнопку ниже:",
            parse_mode="Markdown",
            reply_markup=phone_keyboard()
        )
        await state.set_state(Registration.waiting_phone)

def phone_keyboard():
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    button = KeyboardButton(text="📱 Отправить номер телефона", request_contact=True)
    return ReplyKeyboardMarkup(keyboard=[[button]], resize_keyboard=True)

@router.message(Registration.waiting_phone, F.contact)
async def process_phone(message: Message, state: FSMContext):
    contact = message.contact
    phone = contact.phone_number
    
    await state.update_data(phone=phone)
    
    await message.answer(
        "🏙 *Из какого ты города?*\n\n"
        "Напиши название города (например: Москва, Пекин, Шанхай):",
        parse_mode="Markdown",
        reply_markup=None
    )
    await state.set_state(Registration.waiting_city)

@router.message(Registration.waiting_phone)
async def process_phone_invalid(message: Message, state: FSMContext):
    await message.answer(
        "❓ *Пожалуйста, используй кнопку ниже,* чтобы отправить свой номер телефона.\n\n"
        "Нажми на кнопку 📱 Отправить номер телефона",
        parse_mode="Markdown",
        reply_markup=phone_keyboard()
    )

@router.message(Registration.waiting_city)
async def process_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer(
        "🎯 *Какую цель ставишь?*\n\n"
        "Например:\n"
        "• Поступление в бакалавриат\n"
        "• Изучение китайского языка\n"
        "• Магистратура\n"
        "• Подготовительные курсы",
        parse_mode="Markdown"
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
        f"✅ *Регистрация завершена, {data['name']}!*\n\n"
        f"Теперь ты можешь пользоваться всеми функциями бота.",
        parse_mode="Markdown",
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

@router.message(Command("menu"))
async def cmd_menu(message: Message):
    await message.answer(
        "🏠 *Главное меню*",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )
