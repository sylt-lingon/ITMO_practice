# Базовый образ Python
FROM python:3.9-slim

# Рабочая директория
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем библиотеки
RUN pip install --no-cache-dir -r requirements.txt

# Копируем нужные файлы
COPY main1.py .
COPY tg_bot.py .
COPY queue_manager.py .
COPY config.py .
COPY .env.example .env

# Открываем порт для API
EXPOSE 8000

# Команда запуска (и API, и бот)
CMD ["sh", "-c", "uvicorn main1:app --host 0.0.0.0 --port 8000 & python tg_bot.py"]