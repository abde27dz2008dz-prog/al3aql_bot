import sqlite3
import datetime
from config import DB_PATH, FREE_DAILY_CREDITS


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            credits_used_today INTEGER DEFAULT 0,
            last_reset DATE,
            is_premium INTEGER DEFAULT 0,
            premium_until DATE,
            referred_by INTEGER,
            joined_at DATETIME,
            total_replies INTEGER DEFAULT 0
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount_stars INTEGER,
            paid_at DATETIME
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            active INTEGER DEFAULT 1
        )
    """)
    conn.commit()
    conn.close()


def _today():
    return datetime.date.today().isoformat()


def get_or_create_user(user_id: int, username: str, referred_by: int = None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    if row is None:
        cur.execute(
            "INSERT INTO users (user_id, username, credits_used_today, last_reset, referred_by, joined_at) "
            "VALUES (?, ?, 0, ?, ?, ?)",
            (user_id, username, _today(), referred_by, datetime.datetime.now().isoformat())
        )
        conn.commit()
        cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        row = cur.fetchone()
    conn.close()
    return dict(row)


def _reset_if_new_day(user):
    if user["last_reset"] != _today():
        conn = get_conn()
        conn.execute(
            "UPDATE users SET credits_used_today=0, last_reset=? WHERE user_id=?",
            (_today(), user["user_id"])
        )
        conn.commit()
        conn.close()
        user["credits_used_today"] = 0
        user["last_reset"] = _today()
    return user


def is_premium_active(user) -> bool:
    if not user["is_premium"]:
        return False
    if user["premium_until"] is None:
        return False
    return datetime.date.fromisoformat(user["premium_until"]) >= datetime.date.today()


def can_use_bot(user_id: int, username: str) -> tuple[bool, dict]:
    user = get_or_create_user(user_id, username)
    user = _reset_if_new_day(user)
    if is_premium_active(user):
        return True, user
    if user["credits_used_today"] < FREE_DAILY_CREDITS:
        return True, user
    return False, user


def consume_credit(user_id: int):
    conn = get_conn()
    conn.execute(
        "UPDATE users SET credits_used_today = credits_used_today + 1, "
        "total_replies = total_replies + 1 WHERE user_id=?",
        (user_id,)
    )
    conn.commit()
    conn.close()


def activate_premium(user_id: int, days: int = 30):
    until = (datetime.date.today() + datetime.timedelta(days=days)).isoformat()
    conn = get_conn()
    conn.execute(
        "UPDATE users SET is_premium=1, premium_until=? WHERE user_id=?",
        (until, user_id)
    )
    conn.commit()
    conn.close()


def log_payment(user_id: int, amount_stars: int):
    conn = get_conn()
    conn.execute(
        "INSERT INTO payments (user_id, amount_stars, paid_at) VALUES (?, ?, ?)",
        (user_id, amount_stars, datetime.datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def add_referral_bonus(referrer_id: int, bonus: int):
    conn = get_conn()
    conn.execute(
        "UPDATE users SET credits_used_today = MAX(credits_used_today - ?, 0) WHERE user_id=?",
        (bonus, referrer_id)
    )
    conn.commit()
    conn.close()


def get_stats():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS c FROM users")
    total_users = cur.fetchone()["c"]
    cur.execute("SELECT COUNT(*) AS c FROM users WHERE is_premium=1")
    premium_users = cur.fetchone()["c"]
    cur.execute("SELECT COALESCE(SUM(amount_stars),0) AS s FROM payments")
    total_stars = cur.fetchone()["s"]
    conn.close()
    return {"total_users": total_users, "premium_users": premium_users, "total_stars": total_stars}


def add_ad(text: str):
    conn = get_conn()
    conn.execute("INSERT INTO ads (text, active) VALUES (?, 1)", (text,))
    conn.commit()
    conn.close()


def get_random_active_ad():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM ads WHERE active=1 ORDER BY RANDOM() LIMIT 1")
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None
