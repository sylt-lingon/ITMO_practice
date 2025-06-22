from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    if not TOKEN:
        raise ValueError("Не найден TELEGRAM_BOT_TOKEN в .env файле!")