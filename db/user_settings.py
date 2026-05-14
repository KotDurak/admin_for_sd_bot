# db/user_settings.py
from db.base import get_db_connection
from typing import List, Tuple, Optional, Dict
from datetime import datetime


# db/user_settings.py (фрагмент get_user_settings)
def get_user_settings(page=1, per_page=20, search="", model_filter=""):
    base_sql = """
        SELECT 
            us.*,
            -- 📊 Статистика из generation_requests (подзапросы)
            (SELECT COUNT(*) FROM generation_requests gr WHERE gr.user = us.user_id) as total_requests,
            (SELECT MAX(created_at) FROM generation_requests gr WHERE gr.user = us.user_id) as last_gen_at
        FROM user_settings us
        WHERE 1=1
    """
    params = []

    if search:
        base_sql += " AND (us.username LIKE ? OR CAST(us.user_id AS TEXT) LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    if model_filter:
        base_sql += " AND us.model = ?"
        params.append(model_filter)

    with get_db_connection() as conn:
        # Пагинация
        total = conn.execute(f"SELECT COUNT(*) FROM ({base_sql})", params).fetchone()[0]
        total_pages = max(1, (total + per_page - 1) // per_page)
        offset = (page - 1) * per_page

        rows = conn.execute(
            base_sql + " ORDER BY us.created_at DESC LIMIT ? OFFSET ?",
            params + [per_page, offset]
        ).fetchall()

        return [dict(r) for r in rows], total, total_pages

def get_user_setting_by_id(setting_id: int) -> Optional[Dict]:
    """Получить одну запись по ID"""
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT * FROM user_settings WHERE user_id = ?",
            (setting_id,)
        ).fetchone()
        return dict(row) if row else None


def get_user_setting_by_user_id(user_id: int) -> Optional[Dict]:
    """Получить запись по Telegram user_id"""
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT * FROM user_settings WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        return dict(row) if row else None


def create_user_setting(data: Dict) -> int:
    """Создать новую запись, вернуть ID"""
    with get_db_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO user_settings 
            (user_id, username, model, preset, requests_count, 
             last_request_at, vae, lora_string)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('user_id'),
            data.get('username'),
            data.get('model'),
            data.get('preset'),
            data.get('requests_count', 0),
            data.get('last_request_at'),
            data.get('vae'),
            data.get('lora_string')
        ))
        conn.commit()
        return cursor.lastrowid


def update_user_setting(setting_id: int, data: Dict) -> bool:
    """Обновить запись, вернуть успех"""
    with get_db_connection() as conn:
        conn.execute("""
            UPDATE user_settings SET 
                username = ?, model = ?, preset = ?, 
                requests_count = ?, last_request_at = ?,
                vae = ?, lora_string = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (
            data.get('username'),
            data.get('model'),
            data.get('preset'),
            data.get('requests_count', 0),
            data.get('last_request_at') or None,
            data.get('vae'),
            data.get('lora_string'),
            setting_id
        ))
        conn.commit()
        return True


def delete_user_setting(setting_id: int) -> bool:
    """Удалить запись по ID"""
    with get_db_connection() as conn:
        conn.execute("DELETE FROM user_settings WHERE user_id = ?", (setting_id,))
        conn.commit()
        return True