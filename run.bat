@echo off
title 🌌 AnimeGen Admin Panel
chcp 65001 >nul 2>&1
cd /d "%~dp0"

echo.
echo 🚀 Запуск AnimeGen Admin Panel...
echo 📂 Рабочая папка: %CD%
echo.

if not exist ".venv\Scripts\python.exe" (
    echo ❌ ОШИБКА: Виртуальное окружение .venv не найдено!
    echo 💡 Создай его и установи зависимости:
    echo    python -m venv .venv
    echo    .venv\Scripts\pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo ✅ Окружение найдено. Запускаю сервер...
echo 🔗 Админка доступна по адресу: http://127.0.0.1:5001/admin/
echo -----------------------------------------------
".venv\Scripts\python.exe" app.py

echo.
echo 🛑 Сервер остановлен. Нажми любую клавишу для выхода...
pause >nul