# admin/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем .env явно из папки admin/
ENV_PATH = Path(__file__).parent / ".env"
load_dotenv(ENV_PATH)

# 🔐 Авторизация
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "admin123")
ADMIN_SECRET = os.getenv("ADMIN_SECRET", "dev-secret-change-me")

# 🗄️ База данных
DB_PATH_RAW = os.getenv("DB_PATH")
if not DB_PATH_RAW:
    raise EnvironmentError("❌ Переменная DB_PATH не задана в .env!")

# Нормализуем путь под ОС и проверяем существование
DB_PATH = Path(DB_PATH_RAW).resolve()
if not DB_PATH.exists():
    raise FileNotFoundError(f"❌ База данных не найдена: {DB_PATH}")

# Строка подключения для Peewee/SQLAlchemy
DATABASE_URL = f"sqlite:///{DB_PATH}"

print(f"✅ Конфиг загружен. БД: {DB_PATH}")

ADMIN_TELEGRAM_TOKEN = os.getenv("ADMIN_TELEGRAM_TOKEN", "t")
ADMIN_TELEGRAM_CHAT_ID =  os.getenv("ADMIN_TELEGRAM_CHAT_ID", "t")