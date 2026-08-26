"""SQLite 存储层（用户 + 投稿），纯标准库零依赖"""
import json
import os
import sqlite3
import time

import auth

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DB_PATH = os.path.join(DATA_DIR, "lingking.db")

# 默认管理员账号（初始化时若不存在则创建）
DEFAULT_ADMIN = {
    "username": "admin",
    "email": "admin@lingking.local",
    "password": "admin123",  # 首次启动后请尽快修改
}

VALID_BOARDS = {"photo", "resource", "diary"}
VALID_STATUSES = {"pending", "approved", "rejected"}


def get_conn():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _row_to_dict(row):
    d = dict(row)
    # JSON 字段解析
    for key in ("payload", "review_note"):
        if key in d and isinstance(d[key], str):
            try:
                d[key] = json.loads(d[key])
            except Exception:
                pass
    return d


def init_db():
    """建表（幂等），并初始化默认管理员账号"""
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                username      TEXT NOT NULL UNIQUE,
                email         TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                nickname      TEXT NOT NULL DEFAULT '',
                avatar        TEXT NOT NULL DEFAULT '',
                role          TEXT NOT NULL DEFAULT 'member',
                created_at    INTEGER NOT NULL
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS submissions (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                board         TEXT NOT NULL,
                status        TEXT NOT NULL DEFAULT 'pending',
                payload       TEXT NOT NULL,
                submitter_id  INTEGER NOT NULL,
                submitter_name TEXT NOT NULL DEFAULT '',
                created_at    INTEGER NOT NULL,
                reviewed_at   INTEGER,
                reviewed_by   INTEGER,
                review_note   TEXT
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sub_board ON submissions(board)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sub_status ON submissions(status)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sub_created ON submissions(created_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sub_submitter ON submissions(submitter_id)")

    _ensure_default_admin()


def _ensure_default_admin():
    """默认管理员账号不存在则创建（便于首次进入审核后台）"""
    existing = find_by_identifier(DEFAULT_ADMIN["username"]) or find_by_identifier(DEFAULT_ADMIN["email"])
    if existing:
        # 如果用户已存在但不是 admin 角色，提升为 admin（避免用户自己注册把 admin 用户名占用）
        if existing["role"] != "admin":
            with get_conn() as conn:
                conn.execute("UPDATE users SET role='admin' WHERE id=?", (existing["id"],))
        return
    pw_hash = auth.hash_password(DEFAULT_ADMIN["password"])
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO users (username, email, password_hash, role, created_at) VALUES (?, ?, ?, 'admin', ?)",
            (DEFAULT_ADMIN["username"], DEFAULT_ADMIN["email"], pw_hash, int(time.time())),
        )


# ----------------- 用户 ----------------- #

def create_user(username: str, email: str, password_hash: str, role: str = "member") -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO users (username, email, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)",
            (username, email, password_hash, role, int(time.time())),
        )
        return cur.lastrowid


def find_by_identifier(identifier: str):
    """支持用户名或邮箱登录"""
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE username = ? OR email = ?",
            (identifier, identifier),
        ).fetchone()


def find_by_id(uid: int):
    with get_conn() as conn:
        return conn.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()


def list_users(limit: int = 200):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, username, email, nickname, role, created_at FROM users ORDER BY id ASC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]


def set_user_role(uid: int, role: str):
    role = "admin" if role == "admin" else "member"
    with get_conn() as conn:
        conn.execute("UPDATE users SET role=? WHERE id=?", (role, uid))


# ----------------- 投稿 ----------------- #

def create_submission(board: str, payload: dict, submitter_id: int, submitter_name: str):
    if board not in VALID_BOARDS:
        raise ValueError(f"不支持的板块: {board}")
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO submissions (board, status, payload, submitter_id, submitter_name, created_at) VALUES (?, 'pending', ?, ?, ?, ?)",
            (board, json.dumps(payload, ensure_ascii=False), submitter_id, submitter_name or "", int(time.time())),
        )
        return cur.lastrowid


def list_submissions(board: str = None, status: str = None, submitter_id: int = None, limit: int = 500):
    sql = "SELECT s.*, u.username AS submitter_uname FROM submissions s LEFT JOIN users u ON u.id = s.submitter_id WHERE 1=1"
    args = []
    if board:
        if board not in VALID_BOARDS:
            return []
        sql += " AND s.board = ?"
        args.append(board)
    if status:
        if status not in VALID_STATUSES:
            return []
        sql += " AND s.status = ?"
        args.append(status)
    if submitter_id is not None:
        sql += " AND s.submitter_id = ?"
        args.append(int(submitter_id))
    sql += " ORDER BY s.created_at DESC LIMIT ?"
    args.append(int(limit))
    with get_conn() as conn:
        rows = conn.execute(sql, args).fetchall()
        return [_row_to_dict(r) for r in rows]


def get_submission(sid: int):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM submissions WHERE id=?", (sid,)).fetchone()
        return _row_to_dict(row) if row else None


def review_submission(sid: int, new_status: str, reviewer_id: int, review_note: str = None):
    if new_status not in ("approved", "rejected"):
        raise ValueError(f"不合法的审核状态: {new_status}")
    with get_conn() as conn:
        conn.execute(
            "UPDATE submissions SET status=?, reviewed_at=?, reviewed_by=?, review_note=? WHERE id=?",
            (
                new_status,
                int(time.time()),
                reviewer_id,
                json.dumps({"note": review_note or ""}, ensure_ascii=False) if review_note else None,
                sid,
            ),
        )


def delete_submission(sid: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM submissions WHERE id=?", (sid,))


def count_submissions(status: str = None, board: str = None):
    sql = "SELECT COUNT(*) AS c FROM submissions WHERE 1=1"
    args = []
    if status:
        sql += " AND status=?"
        args.append(status)
    if board:
        sql += " AND board=?"
        args.append(board)
    with get_conn() as conn:
        return conn.execute(sql, args).fetchone()["c"]


def list_approved_board(board: str):
    """返回某板块已审核通过的投稿列表（供 Gallery/Resources/Diary 等页面合并展示）"""
    if board not in VALID_BOARDS:
        return []
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM submissions WHERE board=? AND status='approved' ORDER BY created_at DESC",
            (board,),
        ).fetchall()
        return [_row_to_dict(r) for r in rows]
