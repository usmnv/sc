from aiogram.fsm.state import State, StatesGroup

class Registration(StatesGroup):
    waiting_name = State()
    waiting_phone = State()
    waiting_city = State()
    waiting_goal = State()

class CitySearch(StatesGroup):
    waiting_city_name = State()