import os
import sqlite3
from pathlib import Path
from typing import Any
from uuid import uuid4

DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "data" / "memory.db"
DB_PATH = Path(os.getenv("MEMORY_DB_PATH") or str(DEFAULT_DB_PATH))


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def init_memory() -> None:
    with _connect() as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_messages_conversation
            ON messages(conversation_id, id);
            """
        )


def ensure_conversation(conversation_id: str | None = None) -> str:
    conversation_id = conversation_id or str(uuid4())
    with _connect() as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        exists = connection.execute(
            "SELECT 1 FROM conversations WHERE id = ?",
            (conversation_id,),
        ).fetchone()
        if not exists:
            connection.execute(
                "INSERT INTO conversations (id) VALUES (?)",
                (conversation_id,),
            )
    return conversation_id


def get_history(conversation_id: str, limit: int = 24) -> list[dict[str, str]]:
    limit = max(2, min(int(limit), 50))
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT role, content
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (conversation_id, limit),
        ).fetchall()
    return [dict(row) for row in reversed(rows)]


def save_turn(conversation_id: str, user_message: str, assistant_message: str) -> None:
    with _connect() as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(
            "INSERT OR IGNORE INTO conversations (id) VALUES (?)",
            (conversation_id,),
        )
        connection.executemany(
            "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
            [
                (conversation_id, "user", user_message),
                (conversation_id, "assistant", assistant_message),
            ],
        )
        connection.execute(
            "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (conversation_id,),
        )


def get_conversation(conversation_id: str) -> dict[str, Any] | None:
    with _connect() as connection:
        conversation = connection.execute(
            "SELECT id, created_at, updated_at FROM conversations WHERE id = ?",
            (conversation_id,),
        ).fetchone()
    if not conversation:
        return None
    return {
        **dict(conversation),
        "messages": get_history(conversation_id, limit=50),
    }


def delete_conversation(conversation_id: str) -> bool:
    with _connect() as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        cursor = connection.execute(
            "DELETE FROM conversations WHERE id = ?",
            (conversation_id,),
        )
    return cursor.rowcount > 0
