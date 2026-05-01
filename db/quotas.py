from db.base import get_db_connection
from typing import List, Tuple, Optional, Dict

def get_quotas(page=1, per_page=20, banned=None, search="") -> Tuple[List[Dict], int, int]:
    base_sql = """
        SELECT q.id, q.user_id, u.username, q.paid_credits, q.paid_used, 
               q.is_banned, q.is_unlimited, q.free_used, q.free_limit
        FROM user_quota q LEFT JOIN user_settings u ON q.user_id = u.user_id WHERE 1=1
    """
    params = []
    if banned is not None: base_sql += " AND q.is_banned = ?"; params.append(banned)
    if search: base_sql += " AND (u.username LIKE ? OR CAST(q.user_id AS TEXT) LIKE ?)"; params.extend([f"%{search}%", f"%{search}%"])

    with get_db_connection() as conn:
        total = conn.execute(f"SELECT COUNT(*) FROM ({base_sql})", params).fetchone()[0]
        total_pages = max(1, (total + per_page - 1) // per_page)
        offset = (page - 1) * per_page
        rows = conn.execute(base_sql + " ORDER BY q.id DESC LIMIT ? OFFSET ?", params + [per_page, offset]).fetchall()
        return [dict(r) for r in rows], total, total_pages

def get_quota_by_id(qid: int) -> Optional[Dict]:
    with get_db_connection() as conn:
        row = conn.execute("SELECT * FROM user_quota WHERE id = ?", (qid,)).fetchone()
        return dict(row) if row else None

def create_quota(data: dict) -> int:
    with get_db_connection() as conn:
        cur = conn.execute(
            """INSERT INTO user_quota 
               (user_id, is_unlimited, is_banned, free_used, free_limit, paid_credits, paid_used) 
               VALUES (?,?,?,?,?,?,?)""",
            (int(data['user_id']), int(data.get('is_unlimited', 0)), int(data.get('is_banned', 0)),
             int(data.get('free_used', 0)), int(data.get('free_limit', 0)),
             int(data.get('paid_credits', 0)), int(data.get('paid_used', 0)))
        )
        return cur.lastrowid

def update_quota(qid: int, data: dict) -> bool:
    with get_db_connection() as conn:
        conn.execute(
            """UPDATE user_quota SET user_id=?, is_unlimited=?, is_banned=?, 
               free_used=?, free_limit=?, paid_credits=?, paid_used=? WHERE id=?""",
            (int(data['user_id']), int(data.get('is_unlimited', 0)), int(data.get('is_banned', 0)),
             int(data.get('free_used', 0)), int(data.get('free_limit', 0)),
             int(data.get('paid_credits', 0)), int(data.get('paid_used', 0)), qid)
        )
        return True

def delete_quota(qid: int) -> bool:
    with get_db_connection() as conn:
        conn.execute("DELETE FROM user_quota WHERE id = ?", (qid,))
        return True