from aiogram import Router, F
from aiogram.types import CallbackQuery

from utils.api import get_exchange_rate

router = Router()

@router.callback_query(F.data == "menu_exchange")
async def exchange_menu(callback: CallbackQuery):
    rate = await get_exchange_rate()
    
    text = (
        "💱 *Актуальный курс валют*\n\n"
        f"🇨🇳 1 Китайский юань (CNY) =\n\n"
        f"💵 {rate['cny_to_usd']} USD\n"
        f"🇷🇺 {rate['cny_to_rub']} RUB\n"
        f"🇰🇿 {rate['cny_to_kzt']} KZT\n\n"
        f"🕐 Обновлено: {rate['updated_at']}"
    )
    
    if rate.get("note"):
        text += f"\n\n⚠️ {rate['note']}"
    
    text += "\n\n💡 *Совет:* Лучше менять валюту в Китае в банках или через Alipay/WeChat"
    
    from keyboards import back_to_main_button
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_to_main_button())
    await callback.answer()