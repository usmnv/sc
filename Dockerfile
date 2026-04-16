FROM python:3.11-slim

WORKDIR /app

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Создаем папку для базы данных
RUN mkdir -p /app/data

# Открываем порт для healthcheck
EXPOSE 80

# Запускаем бота
CMD ["python", "bot.py"]