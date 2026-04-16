from aiogram import Router, F
from aiogram.types import CallbackQuery

from database import get_guide_articles
from keyboards import guide_keyboard, back_to_main_button

router = Router()

@router.callback_query(F.data == "menu_guide")
async def guide_menu(callback: CallbackQuery):
    articles = await get_guide_articles()
    
    await callback.message.edit_text(
        "🇨🇳 *Гид по жизни в Китае*\n\n"
        "Выбери тему, которая тебя интересует:",
        parse_mode="Markdown",
        reply_markup=guide_keyboard(articles)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("guide_"))
async def show_guide_article(callback: CallbackQuery):
    article_id = int(callback.data.split("_")[1])
    
    from database import DB_PATH
    import aiosqlite
    
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM guide_articles WHERE id = ?", (article_id,))
        article = await cursor.fetchone()
    
    if article:
        text = f"📖 *{article['title']}*\n\n{article['content']}"
        
        if article['image_url'] and article['image_url'].startswith('http'):
            try:
                await callback.message.answer_photo(article['image_url'], caption=text, parse_mode="Markdown")
            except:
                await callback.message.answer(text, parse_mode="Markdown")
        else:
            await callback.message.answer(text, parse_mode="Markdown")
        
        await callback.message.answer(
            "🔍 Хочешь узнать больше? Нажми /start для возврата в меню",
            reply_markup=back_to_main_button()
        )
    else:
        await callback.answer("Статья не найдена")
    
    await callback.answer()