# auth_utils.py
import sqlite3, hashlib

DB_PATH = "users.db"

def create_user_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY,
        username TEXT,
        password_hash TEXT,
        approved INTEGER DEFAULT 0
    )""")
    conn.commit(); conn.close()

def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def add_user(email, username, password) -> bool:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users VALUES (?,?,?,0)",
                  (email, username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(email, password) -> bool:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT password_hash, approved FROM users WHERE email=?", (email,))
    row = c.fetchone(); conn.close()
    if row and row[0] == hash_password(password) and row[1] == 1:
        return True
    return False

def get_pending_users():
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("SELECT email, username FROM users WHERE approved=0")
    rows = c.fetchall(); conn.close()
    return [{"email": r[0], "username": r[1]} for r in rows]

def approve_user(email):
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("UPDATE users SET approved=1 WHERE email=?", (email,))
    conn.commit(); conn.close()
