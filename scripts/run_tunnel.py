# scripts/run_tunnel.py
# !/usr/bin/env python3
"""
Лаунчер Cloudflare Tunnel с авто-уведомлениями в ТГ и авто-перезапуском.
Запуск: python scripts/run_tunnel.py
"""

import subprocess
import re
import time
import sys
from pathlib import Path

# Добавляем корень проекта в PATH, чтобы импорты работали
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.tunnel_notifier import notify_tunnel_up, notify_tunnel_restart, notify_tunnel_down

# 📍 Настройки
CLOUDFLARED_PATH = r"C:\tools\cloudflared\cloudflared.exe"
LOCAL_PORT = 5001
MAX_RESTARTS = 5  # сколько раз перезапускать при падениях
RESTART_DELAY = 5  # пауза между перезапусками (сек)


def extract_url(output_line: str) -> str | None:
    """Извлекает URL из вывода cloudflared"""
    # Ищем строку вида: https://xxx-trycloudflare-com.trycloudflare.com
    match = re.search(r'https://[a-zA-Z0-9.-]+trycloudflare\.com', output_line)
    if match:
        return match.group(0)
    return None


def run_tunnel():
    """Запускает cloudflared и мониторит вывод"""
    cmd = [CLOUDFLARED_PATH, "tunnel", "--url", f"http://localhost:{LOCAL_PORT}"]

    print(f"🚀 Запуск: {' '.join(cmd)}")
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,  # построчный вывод
        encoding='utf-8',
        errors='replace'
    )

    url_sent = False
    current_url = None

    # Читаем вывод построчно
    for line in iter(process.stdout.readline, ''):
        if not line:
            break

        # Печатаем в консоль (чтобы видеть логи)
        print(f"[cloudflared] {line.strip()}")

        # Ловим ссылку
        if not url_sent:
            url = extract_url(line)
            if url:
                current_url = url
                print(f"✅ Ссылка найдена: {url}")
                if notify_tunnel_up(url, LOCAL_PORT):
                    print("📬 Уведомление отправлено в ТГ")
                    url_sent = True
                else:
                    print("❌ Не удалось отправить уведомление")

    # Процесс завершился
    return_code = process.wait()
    return return_code, current_url


def main():
    restarts = 0
    last_url = None

    print("🔗 Лаунчер туннеля запущен. Нажми Ctrl+C для остановки.\n")

    while True:
        print(f"\n{'=' * 60}")
        print(f"🔄 Попытка #{restarts + 1}")
        print(f"{'=' * 60}\n")

        return_code, url = run_tunnel()

        # Сохраняем URL для уведомления о перезапуске
        if url:
            last_url = url

        # Если процесс упал с ошибкой
        if return_code != 0:
            notify_tunnel_down(f"Код выхода: {return_code}")
            print(f"❌ Процесс завершился с кодом {return_code}")
        else:
            print("✅ Процесс завершился штатно")

        # Логика перезапуска
        restarts += 1
        if restarts >= MAX_RESTARTS:
            print(f"🛑 Достигнут лимит перезапусков ({MAX_RESTARTS}). Останавливаемся.")
            break

        print(f"⏳ Перезапуск через {RESTART_DELAY} сек...")
        time.sleep(RESTART_DELAY)

        # Уведомление о перезапуске (если уже была ссылка)
        if last_url:
            notify_tunnel_restart(last_url, reason=f"попытка #{restarts + 1}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Остановлено пользователем")
        notify_tunnel_down("Остановлено вручную")
    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")
        notify_tunnel_down(f"Критическая ошибка: {str(e)[:300]}")