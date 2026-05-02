# 🎨 AnimeGen Admin Panel

Панель управления для телеграм-бота генерации аниме-артов.  
Позволяет управлять пользователями, квотами, рекламой, платежами и аналитикой.

## 🛠 Стек
- **Backend**: Python 3.10+, Flask 3.0, Peewee ORM
- **Frontend**: Jinja2 + Bootstrap 4 + Chart.js
- **Auth**: Flask-Login (простая авторизация админа)
- **DB**: SQLite (`bot_data.db`)
- **AI**: Stable Diffusion (локально) + внешние API (опционально)

## 🚀 Запуск
```bash
# 1. Активируй виртуалку
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate  # Windows

# 2. Установи зависимости
pip install -r requirements.txt

# 3. Запусти
python app.py

# 4. Открой в браузере
# → http://127.0.0.1:5001/admin/
# Логин/пароль — из config.py (ADMIN_USER / ADMIN_PASS)

📁 Структура

admin_sd_bot/
├── app.py                 # Точка входа, инициализация Flask-Admin
├── config.py              # Настройки (секреты, доступы)
├── db/
│   ├── base.py           # Подключение к БД
│   ├── quotas.py         # Логика для квот (raw SQL)
│   ├── user_settings.py  # Пользователи + статистика
│   └── dashboard.py      # Агрегации для дашборда
├── routes/
│   ├── quotas.py         # Flask-Admin View для квот
│   ├── user_settings.py  # Кастомный CRUD пользователей
│   └── dashboard.py      # Дашборд с графиками
├── templates/admin/
│   ├── master.html       # Базовый шаблон (меню, хедер)
│   ├── login.html        # Страница входа
│   ├── dashboard/        # Дашборд с графиками
│   ├── quotas/           # Страницы квот (список + форма)
│   └── user_settings/    # Страницы пользователей
├── models.py             # Peewee-модели (для стандартных вьюх)
├── admin/views.py        # Настроенные ModelView для простых таблиц
└── requirements.txt      # Зависимости