"""
database.py — 数据访问层（SQLite / PostgreSQL 双后端）

规则：
- 如果环境变量 DATABASE_URL 存在，则连接 PostgreSQL（Supabase 等）
- 否则回退到本地 SQLite（data/notes.db）
- 所有公共函数签名保持与旧版 SQLite 完全一致
"""
import os
import sqlite3
from datetime import datetime
from pathlib import Path

# ── 数据库选择 ─────────────────────────────────────────────────────
DATABASE_URL = os.environ.get("DATABASE_URL") or ""

# Streamlit Cloud: 从 st.secrets 读取（环境变量不可用时）
if not DATABASE_URL:
    try:
        import streamlit as st
        DATABASE_URL = st.secrets.get("DATABASE_URL", "") or ""
    except Exception:
        pass

_IS_PG = bool(DATABASE_URL)
_DEBUG_DB_INFO = f"PG={_IS_PG} | url={'SET' if _IS_PG else 'NOT_SET'}"

if _IS_PG:
    import psycopg2
    from psycopg2.extras import RealDictCursor

DB_PATH = Path(__file__).parent / "data" / "notes.db"


# ── 内部工具函数 ───────────────────────────────────────────────────
def _sql(sql: str) -> str:
    """PostgreSQL 使用 %s 占位符，SQLite 使用 ? 占位符。"""
    if _IS_PG:
        return sql.replace("?", "%s")
    return sql


def _get_conn():
    """获取原始连接对象。"""
    if _IS_PG:
        return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def _dict(row):
    """统一把行对象转成普通 dict。"""
    if row is None:
        return None
    if isinstance(row, dict):
        return dict(row)
    return dict(row)


def _execute(cur, sql: str, params=()):
    """执行 SQL，自动处理占位符差异。"""
    return cur.execute(_sql(sql), params)


def _fetchall_dict(cur):
    """把当前游标结果全部转成 dict 列表。"""
    rows = cur.fetchall()
    return [_dict(r) for r in rows]


def _fetchone_dict(cur):
    """把当前游标第一行转成 dict 或 None。"""
    row = cur.fetchone()
    return _dict(row)


def _lastrowid(cur):
    """获取刚插入行的自增 ID。"""
    if _IS_PG:
        return cur.fetchone()["id"]
    return cur.lastrowid


# ── 初始化 ─────────────────────────────────────────────────────────
def init_db():
    conn = _get_conn()
    cur = conn.cursor()

    # ---------- 日程 ----------
    if _IS_PG:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id          SERIAL PRIMARY KEY,
            title       TEXT    NOT NULL,
            date        TEXT    NOT NULL,
            start_time  TEXT,
            end_time    TEXT,
            location    TEXT,
            note        TEXT,
            color       TEXT    DEFAULT '#4f8ef7',
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
    else:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            title      TEXT    NOT NULL,
            date       TEXT    NOT NULL,
            start_time TEXT,
            end_time   TEXT,
            location   TEXT,
            note       TEXT,
            color      TEXT    DEFAULT '#4f8ef7',
            created_at TEXT    DEFAULT (datetime('now','localtime'))
        )
        """)

    # ---------- 笔记 ----------
    if _IS_PG:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id          SERIAL PRIMARY KEY,
            title       TEXT    NOT NULL,
            content     TEXT,
            tags        TEXT    DEFAULT '',
            pinned      INTEGER DEFAULT 0,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
    else:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            title      TEXT    NOT NULL,
            content    TEXT,
            tags       TEXT    DEFAULT '',
            pinned     INTEGER DEFAULT 0,
            created_at TEXT    DEFAULT (datetime('now','localtime')),
            updated_at TEXT    DEFAULT (datetime('now','localtime'))
        )
        """)

    # ---------- 项目 ----------
    if _IS_PG:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id          SERIAL PRIMARY KEY,
            name        TEXT    NOT NULL,
            description TEXT,
            status      TEXT    DEFAULT 'active',
            color       TEXT    DEFAULT '#7c5cfc',
            deadline    TEXT,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
    else:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            description TEXT,
            status      TEXT    DEFAULT 'active',
            color       TEXT    DEFAULT '#7c5cfc',
            deadline    TEXT,
            created_at  TEXT    DEFAULT (datetime('now','localtime'))
        )
        """)

    # ---------- 任务 ----------
    if _IS_PG:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id          SERIAL PRIMARY KEY,
            project_id  INTEGER REFERENCES projects(id) ON DELETE CASCADE,
            title       TEXT    NOT NULL,
            description TEXT,
            status      TEXT    DEFAULT 'todo',
            priority    TEXT    DEFAULT 'medium',
            due_date    TEXT,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
    else:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id  INTEGER REFERENCES projects(id) ON DELETE CASCADE,
            title       TEXT    NOT NULL,
            description TEXT,
            status      TEXT    DEFAULT 'todo',
            priority    TEXT    DEFAULT 'medium',
            due_date    TEXT,
            created_at  TEXT    DEFAULT (datetime('now','localtime'))
        )
        """)

    conn.commit()
    cur.close()
    conn.close()


# ─────────────────────────── 日程 CRUD ───────────────────────────
def add_event(title, date, start_time="", end_time="", location="", note="", color="#4f8ef7"):
    conn = _get_conn()
    cur = conn.cursor()
    _execute(cur,
        "INSERT INTO events(title,date,start_time,end_time,location,note,color) VALUES(?,?,?,?,?,?,?)",
        (title, date, start_time, end_time, location, note, color)
    )
    conn.commit()
    cur.close()
    conn.close()


def get_events(month: str = None):
    """month 格式 YYYY-MM，不传则返回全部"""
    conn = _get_conn()
    cur = conn.cursor()
    if month:
        if _IS_PG:
            _execute(cur,
                "SELECT * FROM events WHERE TO_CHAR(date, 'YYYY-MM')=? ORDER BY date, start_time",
                (month,)
            )
        else:
            _execute(cur,
                "SELECT * FROM events WHERE strftime('%Y-%m', date)=? ORDER BY date, start_time",
                (month,)
            )
    else:
        _execute(cur, "SELECT * FROM events ORDER BY date, start_time")
    rows = _fetchall_dict(cur)
    cur.close()
    conn.close()
    return rows


def get_events_by_date(date: str):
    conn = _get_conn()
    cur = conn.cursor()
    _execute(cur, "SELECT * FROM events WHERE date=? ORDER BY start_time", (date,))
    rows = _fetchall_dict(cur)
    cur.close()
    conn.close()
    return rows


def delete_event(event_id: int):
    conn = _get_conn()
    cur = conn.cursor()
    _execute(cur, "DELETE FROM events WHERE id=?", (event_id,))
    conn.commit()
    cur.close()
    conn.close()


def update_event(event_id, **kwargs):
    if not kwargs:
        return
    sets = ", ".join(f"{k}=?" for k in kwargs)
    conn = _get_conn()
    cur = conn.cursor()
    _execute(cur, f"UPDATE events SET {sets} WHERE id=?", (*kwargs.values(), event_id))
    conn.commit()
    cur.close()
    conn.close()


# ─────────────────────────── 笔记 CRUD ───────────────────────────
def add_note(title, content="", tags="", pinned=0):
    conn = _get_conn()
    cur = conn.cursor()
    if _IS_PG:
        _execute(cur,
            "INSERT INTO notes(title,content,tags,pinned) VALUES(?,?,?,?) RETURNING id",
            (title, content, tags, pinned)
        )
    else:
        _execute(cur,
            "INSERT INTO notes(title,content,tags,pinned) VALUES(?,?,?,?)",
            (title, content, tags, pinned)
        )
    note_id = _lastrowid(cur)
    conn.commit()
    cur.close()
    conn.close()
    return note_id


def get_notes(search="", tag=""):
    conn = _get_conn()
    cur = conn.cursor()
    query = "SELECT * FROM notes WHERE 1=1"
    params = []
    if search:
        query += " AND (title LIKE ? OR content LIKE ?)"
        params += [f"%{search}%", f"%{search}%"]
    if tag:
        query += " AND (',' || tags || ',') LIKE ?"
        params.append(f"%,{tag},%")
    query += " ORDER BY pinned DESC, updated_at DESC"
    _execute(cur, query, params)
    rows = _fetchall_dict(cur)
    cur.close()
    conn.close()
    return rows


def get_note(note_id: int):
    conn = _get_conn()
    cur = conn.cursor()
    _execute(cur, "SELECT * FROM notes WHERE id=?", (note_id,))
    row = _fetchone_dict(cur)
    cur.close()
    conn.close()
    return row


def update_note(note_id, **kwargs):
    kwargs["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sets = ", ".join(f"{k}=?" for k in kwargs)
    conn = _get_conn()
    cur = conn.cursor()
    _execute(cur, f"UPDATE notes SET {sets} WHERE id=?", (*kwargs.values(), note_id))
    conn.commit()
    cur.close()
    conn.close()


def delete_note(note_id: int):
    conn = _get_conn()
    cur = conn.cursor()
    _execute(cur, "DELETE FROM notes WHERE id=?", (note_id,))
    conn.commit()
    cur.close()
    conn.close()


def get_all_tags():
    conn = _get_conn()
    cur = conn.cursor()
    _execute(cur, "SELECT tags FROM notes WHERE tags != ''")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    tags = set()
    for r in rows:
        for t in r["tags"].split(","):
            t = t.strip()
            if t:
                tags.add(t)
    return sorted(tags)


# ─────────────────────────── 项目 CRUD ───────────────────────────
def add_project(name, description="", color="#7c5cfc", deadline=""):
    conn = _get_conn()
    cur = conn.cursor()
    if _IS_PG:
        _execute(cur,
            "INSERT INTO projects(name,description,color,deadline) VALUES(?,?,?,?) RETURNING id",
            (name, description, color, deadline)
        )
    else:
        _execute(cur,
            "INSERT INTO projects(name,description,color,deadline) VALUES(?,?,?,?)",
            (name, description, color, deadline)
        )
    pid = _lastrowid(cur)
    conn.commit()
    cur.close()
    conn.close()
    return pid


def get_projects(status="active"):
    conn = _get_conn()
    cur = conn.cursor()
    _execute(cur, "SELECT * FROM projects WHERE status=? ORDER BY created_at DESC", (status,))
    rows = _fetchall_dict(cur)
    cur.close()
    conn.close()
    return rows


def get_project(project_id: int):
    conn = _get_conn()
    cur = conn.cursor()
    _execute(cur, "SELECT * FROM projects WHERE id=?", (project_id,))
    row = _fetchone_dict(cur)
    cur.close()
    conn.close()
    return row


def update_project(project_id, **kwargs):
    sets = ", ".join(f"{k}=?" for k in kwargs)
    conn = _get_conn()
    cur = conn.cursor()
    _execute(cur, f"UPDATE projects SET {sets} WHERE id=?", (*kwargs.values(), project_id))
    conn.commit()
    cur.close()
    conn.close()


def delete_project(project_id: int):
    conn = _get_conn()
    cur = conn.cursor()
    _execute(cur, "DELETE FROM projects WHERE id=?", (project_id,))
    conn.commit()
    cur.close()
    conn.close()


# ─────────────────────────── 任务 CRUD ───────────────────────────
def add_task(project_id, title, description="", priority="medium", due_date=""):
    conn = _get_conn()
    cur = conn.cursor()
    _execute(cur,
        "INSERT INTO tasks(project_id,title,description,priority,due_date) VALUES(?,?,?,?,?)",
        (project_id, title, description, priority, due_date)
    )
    conn.commit()
    cur.close()
    conn.close()


def get_tasks(project_id: int):
    conn = _get_conn()
    cur = conn.cursor()
    _execute(cur,
        "SELECT * FROM tasks WHERE project_id=? ORDER BY status, priority DESC, created_at",
        (project_id,)
    )
    rows = _fetchall_dict(cur)
    cur.close()
    conn.close()
    return rows


def update_task(task_id, **kwargs):
    sets = ", ".join(f"{k}=?" for k in kwargs)
    conn = _get_conn()
    cur = conn.cursor()
    _execute(cur, f"UPDATE tasks SET {sets} WHERE id=?", (*kwargs.values(), task_id))
    conn.commit()
    cur.close()
    conn.close()


def delete_task(task_id: int):
    conn = _get_conn()
    cur = conn.cursor()
    _execute(cur, "DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    cur.close()
    conn.close()


# ─────────────────────────── 统计 ───────────────────────────
def get_stats():
    conn = _get_conn()
    cur = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")

    if _IS_PG:
        _execute(cur, "SELECT COUNT(*) AS cnt FROM events WHERE date=%s", (today,))
        today_events = cur.fetchone()["cnt"]
        _execute(cur, "SELECT COUNT(*) AS cnt FROM notes")
        total_notes = cur.fetchone()["cnt"]
        _execute(cur, "SELECT COUNT(*) AS cnt FROM projects WHERE status='active'")
        active_projects = cur.fetchone()["cnt"]
        _execute(cur, "SELECT COUNT(*) AS cnt FROM tasks WHERE status='todo'")
        todo_tasks = cur.fetchone()["cnt"]
        _execute(cur, "SELECT COUNT(*) AS cnt FROM tasks WHERE status='doing'")
        doing_tasks = cur.fetchone()["cnt"]
        _execute(cur, "SELECT COUNT(*) AS cnt FROM tasks WHERE status='done'")
        done_tasks = cur.fetchone()["cnt"]
    else:
        _execute(cur, "SELECT COUNT(*) FROM events WHERE date=?", (today,))
        today_events = cur.fetchone()[0]
        _execute(cur, "SELECT COUNT(*) FROM notes")
        total_notes = cur.fetchone()[0]
        _execute(cur, "SELECT COUNT(*) FROM projects WHERE status='active'")
        active_projects = cur.fetchone()[0]
        _execute(cur, "SELECT COUNT(*) FROM tasks WHERE status='todo'")
        todo_tasks = cur.fetchone()[0]
        _execute(cur, "SELECT COUNT(*) FROM tasks WHERE status='doing'")
        doing_tasks = cur.fetchone()[0]
        _execute(cur, "SELECT COUNT(*) FROM tasks WHERE status='done'")
        done_tasks = cur.fetchone()[0]

    cur.close()
    conn.close()

    return {
        "today_events": today_events,
        "total_notes": total_notes,
        "active_projects": active_projects,
        "todo_tasks": todo_tasks,
        "doing_tasks": doing_tasks,
        "done_tasks": done_tasks,
    }
