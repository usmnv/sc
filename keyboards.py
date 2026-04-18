from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🎓 Поступление", callback_data="menu_admission")
    builder.button(text="💱 Обменник валют", callback_data="menu_exchange")
    builder.button(text="🇨🇳 Гид по жизни", callback_data="menu_guide")
    builder.button(text="❓ Вопросы и ответы", callback_data="menu_faq")
    builder.button(text="📞 Связаться с менеджером", callback_data="menu_manager")
    builder.adjust(1)
    return builder.as_markup()

def back_to_main_button() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="◀ На главную", callback_data="back_main")
    return builder.as_markup()

def programs_keyboard(programs: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for prog in programs:
        builder.button(text=prog["name"], callback_data=f"prog_{prog['code']}")
    builder.button(text="◀ На главную", callback_data="back_main")
    builder.adjust(1)
    return builder.as_markup()

def city_choice_keyboard(cities: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for city in cities[:12]:
        builder.button(text=f"🏙 {city}", callback_data=f"city_{city}")
    builder.button(text="🔍 Поиск по названию", callback_data="city_search")
    builder.button(text="◀ Назад", callback_data="menu_admission")
    builder.adjust(2)
    return builder.as_markup()

def university_list_keyboard(universities: list, program_code: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for uni in universities:
        short_name = uni["name_ru"][:30]
        builder.button(text=f"📚 {short_name} - {uni['city']}", callback_data=f"uni_{uni['id']}")
    builder.button(text="◀ Выбрать другой город", callback_data=f"prog_{program_code}")
    builder.button(text="🏠 Главное меню", callback_data="back_main")
    builder.adjust(1)
    return builder.as_markup()

def faq_keyboard(faq_list: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for faq in faq_list:
        builder.button(text=f"❓ {faq['question'][:40]}", callback_data=f"faq_{faq['id']}")
    builder.button(text="◀ На главную", callback_data="back_main")
    builder.adjust(1)
    return builder.as_markup()

def guide_keyboard(articles: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for article in articles:
        builder.button(text=f"📖 {article['title']}", callback_data=f"guide_{article['id']}")
    builder.button(text="◀ На главную", callback_data="back_main")
    builder.adjust(1)
    return builder.as_markup()
