import aiohttp
import json
from datetime import datetime, timedelta

# Кэш для курса валют
_exchange_cache = {
    "data": None,
    "timestamp": None
}

async def get_exchange_rate() -> dict:
    """Возвращает курс CNY к RUB, USD, KZT"""
    global _exchange_cache
    
    # Кэш на 1 час
    if _exchange_cache["timestamp"] and datetime.now() - _exchange_cache["timestamp"] < timedelta(hours=1):
        return _exchange_cache["data"]
    
    try:
        # Бесплатный API (не требует ключа)
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.exchangerate-api.com/v4/latest/CNY") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    usd = data["rates"].get("USD", 0.138)
                    rub = data["rates"].get("RUB", 12.5)
                    kzt = data["rates"].get("KZT", 62.0)
                    
                    result = {
                        "cny_to_usd": round(usd, 4),
                        "cny_to_rub": round(rub, 2),
                        "cny_to_kzt": round(kzt, 2),
                        "updated_at": datetime.now().strftime("%d.%m.%Y %H:%M")
                    }
                    
                    _exchange_cache["data"] = result
                    _exchange_cache["timestamp"] = datetime.now()
                    return result
                else:
                    raise Exception(f"API вернул статус {resp.status}")
    except Exception as e:
        # Если API недоступен, возвращаем примерные значения
        return {
            "cny_to_usd": 0.138,
            "cny_to_rub": 12.50,
            "cny_to_kzt": 62.00,
            "updated_at": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "note": "Примерные значения (API временно недоступен)"
        }