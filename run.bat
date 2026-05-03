@echo off
title 🌌 AnimeGen Admin Panel
chcp 65001 >nul 2>&1
cd /d "%~dp0"

:: 🎛️ НАСТРОЙКИ
set USE_TUNNEL=true
set TUNNEL_SCRIPT=scripts\run_tunnel.py
set CLOUDFLARED_PATH=C:\tools\cloudflared\cloudflared.exe
set ADMIN_PORT=5001

echo.
echo 🚀 Запуск AnimeGen Admin Panel...
echo 📂 Рабочая папка: %CD%
echo.

:: ✅ Проверка виртуального окружения
if not exist ".venv\Scripts\python.exe" (
    echo ❌ ОШИБКА: Виртуальное окружение .venv не найдено!
    echo 💡 Создай его и установи зависимости:
    echo    python -m venv .venv
    echo    .venv\Scripts\pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

:: 🌐 Запуск туннеля (если включено)
if /i "%USE_TUNNEL%"=="true" (
    echo 🔗 Проверка cloudflared...
    if not exist "%CLOUDFLARED_PATH%" (
        echo ⚠️ cloudflared.exe не найден в %CLOUDFLARED_PATH%
        echo 💡 Скачай: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
        echo ⏭️ Продолжаю без туннеля...
        set USE_TUNNEL=false
    ) else (
        echo 🚀 Запуск туннеля в отдельном окне...
        start "🌐 Cloudflare Tunnel" cmd /k "cd /d %CD% && .venv\Scripts\python.exe %TUNNEL_SCRIPT%"
        timeout /t 3 >nul
    )
)

:: ▶️ Запуск самого сервера
echo ✅ Окружение найдено. Запускаю сервер...
if /i "%USE_TUNNEL%"=="true" (
    echo 🔗 Админка будет доступна по ссылке из ТГ (когда туннель поднимется)
    echo 🔗 Локально: http://127.0.0.1:%ADMIN_PORT%/ (авто-редирект на /admin)
) else (
    echo 🔗 Локально: http://127.0.0.1:%ADMIN_PORT%/admin/
)
echo -----------------------------------------------

".venv\Scripts\python.exe" app.py

:: 🧹 Завершение
echo.
echo 🛑 Сервер остановлен.
if /i "%USE_TUNNEL%"=="true" (
    echo 💡 Туннель мог остаться работать в другом окне — закрой его при необходимости.
)
echo Нажми любую клавишу для выхода...
pause >nul