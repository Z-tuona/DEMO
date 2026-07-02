"""
SQLite 元数据库操作
- knowledge_bases 表：知识库名称、描述、创建时间
- documents 表：文档信息，外键关联知识库
- conversations 表：对话会话
- messages 表：对话消息，外键关联对话
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
        CREATE TABLE IF NOT EXISTS conversations (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT    NOT NULL DEFAULT '新对话',
            created_at  TEXT    DEFAULT (datetime('now','localtime')),
            updated_at  TEXT    DEFAULT (datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS messages (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            role            TEXT    NOT NULL CHECK(role IN ('user','assistant')),
            content         TEXT    NOT NULL DEFAULT '',
            created_at      TEXT    DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
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


# ========== 对话 CRUD ==========
def create_conversation(title='新对话'):
    conn = get_conn()
    cur = conn.execute(
        'INSERT INTO conversations (title) VALUES (?)', (title,)
    )
    conv_id = cur.lastrowid
    conn.commit()
    conn.close()
    return get_conversation(conv_id)


def get_conversation(conv_id):
    conn = get_conn()
    row = conn.execute(
        'SELECT c.*, (SELECT COUNT(*) FROM messages m WHERE m.conversation_id = c.id) as message_count '
        'FROM conversations c WHERE c.id = ?', (conv_id,)
    ).fetchone()
    if row:
        result = dict(row)
        msgs = conn.execute(
            'SELECT * FROM messages WHERE conversation_id = ? ORDER BY id ASC', (conv_id,)
        ).fetchall()
        result['messages'] = [dict(m) for m in msgs]
        conn.close()
        return result
    conn.close()
    return None


def list_conversations():
    conn = get_conn()
    rows = conn.execute(
        'SELECT c.*, (SELECT COUNT(*) FROM messages m WHERE m.conversation_id = c.id) as message_count '
        'FROM conversations c ORDER BY c.updated_at DESC'
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_conversation(conv_id, title=None):
    conn = get_conn()
    if title is not None:
        conn.execute(
            "UPDATE conversations SET title = ?, updated_at = datetime('now','localtime') WHERE id = ?",
            (title, conv_id)
        )
    else:
        conn.execute(
            "UPDATE conversations SET updated_at = datetime('now','localtime') WHERE id = ?",
            (conv_id,)
        )
    conn.commit()
    conn.close()
    return get_conversation(conv_id)


def delete_conversation(conv_id):
    conn = get_conn()
    conn.execute('DELETE FROM conversations WHERE id = ?', (conv_id,))
    conn.commit()
    conn.close()


def conversation_exists(conv_id):
    conn = get_conn()
    row = conn.execute('SELECT 1 FROM conversations WHERE id = ?', (conv_id,)).fetchone()
    conn.close()
    return row is not None


# ========== 消息 CRUD ==========
def add_message(conv_id, role, content):
    conn = get_conn()
    cur = conn.execute(
        'INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)',
        (conv_id, role, content)
    )
    msg_id = cur.lastrowid
    conn.execute(
        "UPDATE conversations SET updated_at = datetime('now','localtime') WHERE id = ?",
        (conv_id,)
    )
    conn.commit()
    conn.close()
    return msg_id


def get_messages(conv_id):
    conn = get_conn()
    rows = conn.execute(
        'SELECT * FROM messages WHERE conversation_id = ? ORDER BY id ASC', (conv_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def replace_all_messages(conv_id, messages):
    """全量替换对话消息 — 先删后批量插入"""
    conn = get_conn()
    conn.execute('DELETE FROM messages WHERE conversation_id = ?', (conv_id,))
    for msg in messages:
        conn.execute(
            'INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)',
            (conv_id, msg.get('role', 'user'), msg.get('content', ''))
        )
    conn.execute(
        "UPDATE conversations SET updated_at = datetime('now','localtime') WHERE id = ?",
        (conv_id,)
    )
    conn.commit()
    conn.close()


# 启动时建表
init_db()
