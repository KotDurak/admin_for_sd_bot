import sqlite3
import config
from contextlib import contextmanager

@contextmanager
def get_db_connection():
    """Безопасный контекстный менеджер для SQLite"""
    conn = sqlite3.connect(
        str(config.DB_PATH),
        timeout=10.0,
        check_same_thread=False
    )
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=10000;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()