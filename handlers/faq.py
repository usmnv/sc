from aiogram import Router, F
from aiogram.types import CallbackQuery

from database import get_all_faq
from keyboards import faq_keyboard, back_to_main_button

router = Router()

@router.callback_query(F.data == "menu_faq")
async def faq_menu(callback: CallbackQuery):
    faq_list = await get_all_faq()
    
    await callback.message.edit_text(
        "❓ *Часто задаваемые вопросы*\n\n"
        "Выбери вопрос, чтобы увидеть ответ:",
        parse_mode="Markdown",
        reply_markup=faq_keyboard(faq_list)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("faq_"))
async def show_faq_answer(callback: CallbackQuery):
    faq_id = int(callback.data.split("_")[1])
    
    from database import DB_PATH
    import aiosqlite
    
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM faq WHERE id = ?", (faq_id,))
        faq = await cursor.fetchone()
    
    if faq:
        text = f"❓ *{faq['question']}*\n\n{faq['answer']}"
        await callback.message.answer(text, parse_mode="Markdown", reply_markup=back_to_main_button())
    else:
        await callback.answer("Вопрос не найден")
    
    await callback.answer()