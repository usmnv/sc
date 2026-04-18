from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, Contact, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from database import user_exists, register_user, get_user
from keyboards import main_menu_keyboard
from states import Registration

router = Router()

def phone_keyboard():
    button = KeyboardButton(text="📱 Отправить номер телефона", request_contact=True)
    return ReplyKeyboardMarkup(keyboard=[[button]], resize_keyboard=True)

def goal_keyboard():
    """Клавиатура с целями обучения"""
    builder = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎓 Бакалавриат", callback_data="goal_bachelor")],
        [InlineKeyboardButton(text="🇨🇳 Изучение китайского языка", callback_data="goal_language")],
        [InlineKeyboardButton(text="📚 Магистратура", callback_data="goal_master")],
        [InlineKeyboardButton(text="📖 Подготовительные курсы", callback_data="goal_preparation")],
        [InlineKeyboardButton(text="🏫 Другое", callback_data="goal_other")]
    ])
    return builder

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

@router.message(Registration.waiting_phone, F.contact)
async def process_phone(message: Message, state: FSMContext):
    contact = message.contact
    phone = contact.phone_number
    
    await state.update_data(phone=phone)
    
    # Убираем клавиатуру с контактом
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
    
    # Показываем кнопки с целями
    await message.answer(
        "🎯 *Какую цель ставишь?*\n\n"
        "Выбери один из вариантов:",
        parse_mode="Markdown",
        reply_markup=goal_keyboard()
    )
    # Не меняем состояние, ждем callback

@router.callback_query(F.data.startswith("goal_"))
async def process_goal(callback: CallbackQuery, state: FSMContext):
    goal_map = {
        "goal_bachelor": "Поступление в бакалавриат",
        "goal_language": "Изучение китайского языка",
        "goal_master": "Магистратура",
        "goal_preparation": "Подготовительные курсы",
        "goal_other": "Другое"
    }
    
    goal = goal_map.get(callback.data, "Не указано")
    data = await state.get_data()
    tg_id = callback.from_user.id
    
    await register_user(
        tg_id=tg_id,
        name=data["name"],
        phone=data["phone"],
        city=data["city"],
        goal=goal
    )
    
    await callback.message.edit_text(
        f"✅ *Регистрация завершена, {data['name']}!*\n\n"
        f"Теперь ты можешь пользоваться всеми функциями бота.",
        parse_mode="Markdown"
    )
    
    await callback.message.answer(
        "🏠 *Главное меню*\n\nВыбери нужный раздел:",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )
    await state.clear()
    await callback.answer()

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
