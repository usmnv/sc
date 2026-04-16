from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command

from config import MANAGER_CONTACT, MANAGER_PHONE, MANAGER_WHATSAPP, MANAGER_CHAT_ID
from keyboards import back_to_main_button

router = Router()

@router.callback_query(F.data == "menu_manager")
async def manager_menu(callback: CallbackQuery):
    text = (
        "📞 *Связь с менеджером*\n\n"
        f"• Telegram: {MANAGER_CONTACT}\n"
        f"• WhatsApp: {MANAGER_WHATSAPP}\n"
        f"• Телефон: {MANAGER_PHONE}\n\n"
        "Также ты можешь написать свой вопрос прямо сюда, и мы ответим в течение часа!\n\n"
        "📝 Напиши /ask <вопрос> чтобы задать вопрос менеджеру"
    )
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_to_main_button())
    await callback.answer()

@router.message(Command("ask"))
async def ask_question(message: Message):
    question = message.text.replace("/ask", "").strip()
    if not question:
        await message.answer(
            "❓ Напиши вопрос после команды.\n\n"
            "Пример: `/ask Как поступить в Цинхуа?`",
            parse_mode="Markdown"
        )
        return
    
    await message.answer(
        "✅ *Твой вопрос отправлен менеджеру!*\n\n"
        f"Твой вопрос: _{question[:100]}_\n\n"
        "Мы ответим в ближайшее время!",
        parse_mode="Markdown"
    )
    
    # Если указан ID чата менеджера, отправляем туда уведомление
    if MANAGER_CHAT_ID:
        from aiogram import Bot
        from config import BOT_TOKEN
        
        bot = Bot(token=BOT_TOKEN)
        try:
            await bot.send_message(
                MANAGER_CHAT_ID,
                f"📨 *Новый вопрос от пользователя*\n\n"
                f"👤 ID: {message.from_user.id}\n"
                f"👤 Username: @{message.from_user.username or 'нет'}\n"
                f"❓ Вопрос: {question}"
            )
        except Exception as e:
            logging.error(f"Не удалось отправить вопрос менеджеру: {e}")