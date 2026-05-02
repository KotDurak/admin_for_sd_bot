# db/dashboard.py
from db.base import get_db_connection


def get_dashboard_stats(days=30):
    with get_db_connection() as conn:
        # 1️⃣ Карточки-метрики
        total_users = conn.execute("SELECT COUNT(*) FROM user_settings").fetchone()[0]
        requests_today = \
        conn.execute("SELECT COUNT(*) FROM generation_requests WHERE date(created_at) = date('now')").fetchone()[0]
        active_campaigns = conn.execute("SELECT COUNT(*) FROM ad_campaigns WHERE is_active = 1").fetchone()[0]

        top_model_row = conn.execute("""
            SELECT model_used, COUNT(*) as cnt FROM generation_requests 
            WHERE model_used IS NOT NULL GROUP BY model_used ORDER BY cnt DESC LIMIT 1
        """).fetchone()
        top_model = top_model_row[0] if top_model_row else "—"

        # 2️⃣ История запросов (для графика)
        history = conn.execute("""
            SELECT date(created_at) as day, COUNT(*) as cnt 
            FROM generation_requests 
            WHERE date(created_at) >= date('now', ?) 
            GROUP BY day ORDER BY day
        """, (f"-{days} days",)).fetchall()
        history_data = [{"day": row[0], "count": row[1]} for row in history]

        # 3️⃣ Топ-5 моделей и пресетов
        top_models = conn.execute("""
            SELECT model_used, COUNT(*) as cnt FROM generation_requests 
            WHERE model_used IS NOT NULL GROUP BY model_used ORDER BY cnt DESC LIMIT 5
        """).fetchall()

        top_presets = conn.execute("""
            SELECT preset_used, COUNT(*) as cnt FROM generation_requests 
            WHERE preset_used IS NOT NULL GROUP BY preset_used ORDER BY cnt DESC LIMIT 5
        """).fetchall()

        # 4️⃣ Активные кампании (быстрая статистика)
        campaigns = conn.execute("""
            SELECT id, title, remaining, total_sold, is_active, btn_text 
            FROM ad_campaigns ORDER BY created_at DESC LIMIT 5
        """).fetchall()

        return {
            "total_users": total_users,
            "requests_today": requests_today,
            "active_campaigns": active_campaigns,
            "top_model": top_model,
            "history": history_data,
            "top_models": [{"name": r[0], "count": r[1]} for r in top_models],
            "top_presets": [{"name": r[0], "count": r[1]} for r in top_presets],
            "campaigns": [dict(r) for r in campaigns]
        }