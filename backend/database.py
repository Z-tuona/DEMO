"""
SQLite 元数据库操作
- knowledge_bases 表：知识库名称、描述、创建时间
- documents 表：文档信息，外键关联知识库
"""
import sqlite3
import os
from config import SQLITE_DB_PATH


def get_conn():
    """获取数据库连接"""
    os.makedirs(os.path.dirname(SQLITE_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """创建表结构"""
    conn = get_conn()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS knowledge_bases (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            description TEXT    DEFAULT '',
            created_at  TEXT    DEFAULT (datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS documents (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            kb_id               INTEGER NOT NULL,
            filename            TEXT    NOT NULL,
            original_filename   TEXT    NOT NULL,
            file_type           TEXT    NOT NULL,
            file_size           INTEGER NOT NULL,
            chunk_count         INTEGER NOT NULL DEFAULT 0,
            created_at          TEXT    DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (kb_id) REFERENCES knowledge_bases(id) ON DELETE CASCADE
        );
    ''')
    conn.commit()
    conn.close()


# ========== 知识库 CRUD ==========
def create_kb(name, description=''):
    conn = get_conn()
    cur = conn.execute(
        'INSERT INTO knowledge_bases (name, description) VALUES (?, ?)',
        (name, description)
    )
    kb_id = cur.lastrowid
    conn.commit()
    conn.close()
    return get_kb(kb_id)


def get_kb(kb_id):
    conn = get_conn()
    row = conn.execute('SELECT * FROM knowledge_bases WHERE id = ?', (kb_id,)).fetchone()
    if row:
        doc_count = conn.execute(
            'SELECT COUNT(*) as cnt FROM documents WHERE kb_id = ?', (kb_id,)
        ).fetchone()['cnt']
        result = dict(row)
        result['doc_count'] = doc_count
        conn.close()
        return result
    conn.close()
    return None


def list_kbs():
    conn = get_conn()
    rows = conn.execute(
        'SELECT k.*, (SELECT COUNT(*) FROM documents d WHERE d.kb_id = k.id) as doc_count '
        'FROM knowledge_bases k ORDER BY k.created_at DESC'
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_kb(kb_id, name=None, description=None):
    conn = get_conn()
    if name is not None:
        conn.execute('UPDATE knowledge_bases SET name = ? WHERE id = ?', (name, kb_id))
    if description is not None:
        conn.execute('UPDATE knowledge_bases SET description = ? WHERE id = ?', (description, kb_id))
    conn.commit()
    conn.close()
    return get_kb(kb_id)


def delete_kb(kb_id):
    conn = get_conn()
    conn.execute('DELETE FROM knowledge_bases WHERE id = ?', (kb_id,))
    conn.commit()
    conn.close()


def get_kb_count():
    conn = get_conn()
    count = conn.execute('SELECT COUNT(*) as cnt FROM knowledge_bases').fetchone()['cnt']
    conn.close()
    return count


# ========== 文档 CRUD ==========
def add_document(kb_id, filename, original_filename, file_type, file_size, chunk_count):
    conn = get_conn()
    cur = conn.execute(
        'INSERT INTO documents (kb_id, filename, original_filename, file_type, file_size, chunk_count) '
        'VALUES (?, ?, ?, ?, ?, ?)',
        (kb_id, filename, original_filename, file_type, file_size, chunk_count)
    )
    doc_id = cur.lastrowid
    conn.commit()
    conn.close()
    return doc_id


def list_documents(kb_id):
    conn = get_conn()
    rows = conn.execute(
        'SELECT * FROM documents WHERE kb_id = ? ORDER BY created_at DESC', (kb_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_document(doc_id):
    conn = get_conn()
    row = conn.execute('SELECT * FROM documents WHERE id = ?', (doc_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def delete_document(doc_id):
    conn = get_conn()
    conn.execute('DELETE FROM documents WHERE id = ?', (doc_id,))
    conn.commit()
    conn.close()


# 启动时建表
init_db()
