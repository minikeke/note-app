"""
database_pg.py — PostgreSQL 版本（用于云端部署）

用法：将 database.py 替换为此文件，或修改 import 语句。

环境变量：
    DATABASE_URL=postgresql://user:pass@host:5432/dbname

本地开发时如果不设置 DATABASE_URL，会自动回退到 SQLite。
"""
import os
import sqlite3
from datetime import datetime
from pathlib import Path

# ── 数据库选择 ───────────────────────────────────────────────────
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    IS_POSTGRES = True
else:
    IS_POSTGRES = False

DB_PATH = Path(__file__).parent / "data" / "notes.db"


def get_conn():
    """获取数据库连接，自动根据环境选择 PostgreSQL 或 SQLite。"""
    if IS_POSTGRES:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    else:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
    return conn


# ── 占位符适配 ───────────────────────────────────────────────────
SQL_PARAM = "%s" if IS_POSTGRES else "?"


def _sql(sql: str) -> str:
    """将 SQL 中的 ? 占位符转换为 %s（PostgreSQL 用）。"""
    return sql.replace("?", SQL_PARAM) if IS_POSTGRES else sql


# ── 建表 ─────────────────────────────────────────────────────────
def init_db():
    conn = get_conn()
    cur = conn.cursor()

    if IS_POSTGRES:
        # PostgreSQL 建表
        cur.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                date DATE NOT NULL,
                start_time TEXT,
                end_time TEXT,
                location TEXT,
                note TEXT,
                color TEXT DEFAULT '#3780EA',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT,
                tags TEXT,
                pinned INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'active',
                color TEXT DEFAULT '#3780EA',
                deadline DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'todo',
                priority TEXT DEFAULT 'medium',
                due_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    else:
        # SQLite 建表（保持原有逻辑）
        cur.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                date TEXT NOT NULL,
                start_time TEXT,
                end_time TEXT,
                location TEXT,
                note TEXT,
                color TEXT DEFAULT '#3780EA',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                tags TEXT,
                pinned INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'active',
                color TEXT DEFAULT '#3780EA',
                deadline TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'todo',
                priority TEXT DEFAULT 'medium',
                due_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)

    conn.commit()
    conn.close()


# ── 日程 CRUD ────────────────────────────────────────────────────
def add_event(title, date, start_time, end_time, location, note, color):
    conn = get_conn()
    cur = conn.cursor()
    sql = _sql("""
        INSERT INTO events (title, date, start_time, end_time, location, note, color)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """)
    cur.execute(sql, (title, date, start_time, end_time, location, note, color))
    conn.commit()
    conn.close()


def get_events_by_date(date: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(_sql("SELECT * FROM events WHERE date=? ORDER BY start_time"), (date,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_events():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM events ORDER BY date, start_time")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_event(event_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(_sql("DELETE FROM events WHERE id = ?"), (event_id,))
    conn.commit()
    conn.close()


def update_event(event_id, title, date, start_time, end_time, location, note, color):
    conn = get_conn()
    cur = conn.cursor()
    sql = _sql("""
        UPDATE events
        SET title=?, date=?, start_time=?, end_time=?, location=?, note=?, color=?
        WHERE id=?
    """)
    cur.execute(sql, (title, date, start_time, end_time, location, note, color, event_id))
    conn.commit()
    conn.close()


# ── 笔记 CRUD ────────────────────────────────────────────────────
def add_note(title, content, tags, pinned=0):
    conn = get_conn()
    cur = conn.cursor()
    now = datetime.now().isoformat()
    sql = _sql("""
        INSERT INTO notes (title, content, tags, pinned, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """)
    cur.execute(sql, (title, content, tags, pinned, now, now))
    conn.commit()
    conn.close()


def get_notes():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM notes ORDER BY pinned DESC, updated_at DESC")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_note(note_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(_sql("SELECT * FROM notes WHERE id = ?"), (note_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def update_note(note_id, title, content, tags, pinned):
    conn = get_conn()
    cur = conn.cursor()
    now = datetime.now().isoformat()
    sql = _sql("""
        UPDATE notes
        SET title=?, content=?, tags=?, pinned=?, updated_at=?
        WHERE id=?
    """)
    cur.execute(sql, (title, content, tags, pinned, now, note_id))
    conn.commit()
    conn.close()


def delete_note(note_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(_sql("DELETE FROM notes WHERE id = ?"), (note_id,))
    conn.commit()
    conn.close()


# ── 项目 CRUD ────────────────────────────────────────────────────
def add_project(name, description, color, deadline):
    conn = get_conn()
    cur = conn.cursor()
    sql = _sql("""
        INSERT INTO projects (name, description, color, deadline)
        VALUES (?, ?, ?, ?)
    """)
    cur.execute(sql, (name, description, color, deadline))
    conn.commit()
    conn.close()


def get_projects(status=None):
    conn = get_conn()
    cur = conn.cursor()
    if status:
        cur.execute(_sql("SELECT * FROM projects WHERE status = ? ORDER BY created_at DESC"), (status,))
    else:
        cur.execute("SELECT * FROM projects ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_project(project_id, name, description, color, deadline, status):
    conn = get_conn()
    cur = conn.cursor()
    sql = _sql("""
        UPDATE projects
        SET name=?, description=?, color=?, deadline=?, status=?
        WHERE id=?
    """)
    cur.execute(sql, (name, description, color, deadline, status, project_id))
    conn.commit()
    conn.close()


def delete_project(project_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(_sql("DELETE FROM projects WHERE id = ?"), (project_id,))
    conn.commit()
    conn.close()


# ── 任务 CRUD ────────────────────────────────────────────────────
def add_task(project_id, title, description, priority, due_date):
    conn = get_conn()
    cur = conn.cursor()
    sql = _sql("""
        INSERT INTO tasks (project_id, title, description, priority, due_date)
        VALUES (?, ?, ?, ?, ?)
    """)
    cur.execute(sql, (project_id, title, description, priority, due_date))
    conn.commit()
    conn.close()


def get_tasks(project_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(_sql("SELECT * FROM tasks WHERE project_id = ? ORDER BY priority DESC, due_date"), (project_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_task(task_id, title, description, status, priority, due_date):
    conn = get_conn()
    cur = conn.cursor()
    sql = _sql("""
        UPDATE tasks
        SET title=?, description=?, status=?, priority=?, due_date=?
        WHERE id=?
    """)
    cur.execute(sql, (title, description, status, priority, due_date, task_id))
    conn.commit()
    conn.close()


def delete_task(task_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(_sql("DELETE FROM tasks WHERE id = ?"), (task_id,))
    conn.commit()
    conn.close()


# ── 统计 ───────────────────────────────────────────────────────────
def get_stats():
    conn = get_conn()
    cur = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")
    cur.execute(_sql("SELECT COUNT(*) as cnt FROM events WHERE date = ?"), (today,))
    today_events = cur.fetchone()["cnt"]

    cur.execute("SELECT COUNT(*) as cnt FROM notes")
    total_notes = cur.fetchone()["cnt"]

    cur.execute(_sql("SELECT COUNT(*) as cnt FROM projects WHERE status = ?"), ("active",))
    active_projects = cur.fetchone()["cnt"]

    cur.execute(_sql("SELECT COUNT(*) as cnt FROM tasks WHERE status = ?"), ("todo",))
    todo_tasks = cur.fetchone()["cnt"]

    cur.execute(_sql("SELECT COUNT(*) as cnt FROM tasks WHERE status = ?"), ("doing",))
    doing_tasks = cur.fetchone()["cnt"]

    cur.execute(_sql("SELECT COUNT(*) as cnt FROM tasks WHERE status = ?"), ("done",))
    done_tasks = cur.fetchone()["cnt"]

    conn.close()
    return {
        "today_events": today_events,
        "total_notes": total_notes,
        "active_projects": active_projects,
        "todo_tasks": todo_tasks,
        "doing_tasks": doing_tasks,
        "done_tasks": done_tasks,
    }
