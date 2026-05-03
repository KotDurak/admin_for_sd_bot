# utils/tunnel_notifier.py
import requests
import config
import logging

logger = logging.getLogger(__name__)

def send_telegram_message(text: str, parse_mode: str = "HTML"):
    """Отправляет сообщение в ТГ админу"""
    try:
        url = f"https://api.telegram.org/bot{config.ADMIN_TELEGRAM_TOKEN}/sendMessage"
        data = {
            "chat_id": config.ADMIN_TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True
        }
        resp = requests.post(url, json=data, timeout=10)
        if resp.status_code != 200:
            logger.warning(f"ТГ-уведомление не отправлено: {resp.text}")
            return False
        return True
    except Exception as e:
        logger.error(f"Ошибка отправки в ТГ: {e}")
        return False

def notify_tunnel_up(url: str, port: int = 5001):
    """Сообщение при успешном подъёме туннеля"""
    text = (
        f"🟢 <b>Туннель поднят!</b>\n\n"
        f"🌐 <a href='{url}'>{url}</a>\n"
        f"🔗 Локально: http://localhost:{port}\n"
        f"⏰ Запущен: сейчас"
    )
    return send_telegram_message(text)

def notify_tunnel_restart(url: str, reason: str = "перезапуск"):
    """Сообщение при перезапуске туннеля"""
    text = (
        f"🔁 <b>Туннель перезапущен</b>\n"
        f"Причина: {reason}\n\n"
        f"🌐 <a href='{url}'>{url}</a>"
    )
    return send_telegram_message(text)

def notify_tunnel_down(error: str = None):
    """Сообщение при падении туннеля"""
    text = f"🔴 <b>Туннель упал</b>"
    if error:
        text += f"\n\n❗ Ошибка:\n<code>{error[:500]}</code>"  # обрезаем, если длинно
    return send_telegram_message(text)