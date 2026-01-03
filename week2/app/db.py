"""Database layer with improved error handling and type safety."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Optional

from .config import settings
from .exceptions import DatabaseError, NotFoundError
from .schemas import ActionItemResponse, NoteResponse


def ensure_data_directory_exists() -> None:
    """Ensure the data directory exists."""
    settings.data_dir.mkdir(parents=True, exist_ok=True)


@contextmanager
def get_connection():
    """Context manager for database connections with proper error handling."""
    ensure_data_directory_exists()
    connection = None
    try:
        connection = sqlite3.connect(str(settings.db_path))
        connection.row_factory = sqlite3.Row
        yield connection
        connection.commit()
    except sqlite3.Error as e:
        if connection:
            connection.rollback()
        raise DatabaseError(f"Database error: {e}") from e
    finally:
        if connection:
            connection.close()


def init_db() -> None:
    """Initialize the database schema."""
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now'))
                );
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS action_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    note_id INTEGER,
                    text TEXT NOT NULL,
                    done INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (note_id) REFERENCES notes(id)
                );
                """
            )
            connection.commit()
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to initialize database: {e}") from e


def insert_note(content: str) -> int:
    """Insert a new note and return its ID."""
    if not content or not content.strip():
        raise ValueError("Note content cannot be empty")
    
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO notes (content) VALUES (?)", (content,))
            connection.commit()
            note_id = int(cursor.lastrowid)
            if note_id is None:
                raise DatabaseError("Failed to get note ID after insertion")
            return note_id
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to insert note: {e}") from e


def list_notes() -> list[NoteResponse]:
    """List all notes."""
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id, content, created_at FROM notes ORDER BY id DESC")
            rows = cursor.fetchall()
            return [
                NoteResponse(
                    id=row["id"],
                    content=row["content"],
                    created_at=row["created_at"],
                )
                for row in rows
            ]
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to list notes: {e}") from e


def get_note(note_id: int) -> NoteResponse:
    """Get a note by ID."""
    if note_id <= 0:
        raise ValueError("Note ID must be positive")
    
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id, content, created_at FROM notes WHERE id = ?",
                (note_id,),
            )
            row = cursor.fetchone()
            if row is None:
                raise NotFoundError(f"Note with id {note_id} not found")
            return NoteResponse(
                id=row["id"],
                content=row["content"],
                created_at=row["created_at"],
            )
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to get note: {e}") from e
    except NotFoundError:
        raise


def insert_action_items(items: list[str], note_id: Optional[int] = None) -> list[ActionItemResponse]:
    """Insert action items and return their full data."""
    if not items:
        return []
    
    if note_id is not None and note_id <= 0:
        raise ValueError("Note ID must be positive if provided")
    
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            inserted_items: list[ActionItemResponse] = []
            for item in items:
                if not item or not item.strip():
                    continue
                cursor.execute(
                    "INSERT INTO action_items (note_id, text) VALUES (?, ?)",
                    (note_id, item.strip()),
                )
                item_id = int(cursor.lastrowid)
                if item_id is None:
                    raise DatabaseError("Failed to get action item ID after insertion")
                
                # Fetch the inserted row to get created_at
                cursor.execute(
                    "SELECT id, note_id, text, done, created_at FROM action_items WHERE id = ?",
                    (item_id,),
                )
                row = cursor.fetchone()
                if row:
                    inserted_items.append(
                        ActionItemResponse(
                            id=row["id"],
                            note_id=row["note_id"],
                            text=row["text"],
                            done=bool(row["done"]),
                            created_at=row["created_at"],
                        )
                    )
            connection.commit()
            return inserted_items
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to insert action items: {e}") from e


def list_action_items(note_id: Optional[int] = None) -> list[ActionItemResponse]:
    """List action items, optionally filtered by note_id."""
    if note_id is not None and note_id <= 0:
        raise ValueError("Note ID must be positive if provided")
    
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            if note_id is None:
                cursor.execute(
                    "SELECT id, note_id, text, done, created_at FROM action_items ORDER BY id DESC"
                )
            else:
                cursor.execute(
                    "SELECT id, note_id, text, done, created_at FROM action_items WHERE note_id = ? ORDER BY id DESC",
                    (note_id,),
                )
            rows = cursor.fetchall()
            return [
                ActionItemResponse(
                    id=row["id"],
                    note_id=row["note_id"],
                    text=row["text"],
                    done=bool(row["done"]),
                    created_at=row["created_at"],
                )
                for row in rows
            ]
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to list action items: {e}") from e


def mark_action_item_done(action_item_id: int, done: bool) -> None:
    """Mark an action item as done or not done."""
    if action_item_id <= 0:
        raise ValueError("Action item ID must be positive")
    
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE action_items SET done = ? WHERE id = ?",
                (1 if done else 0, action_item_id),
            )
            if cursor.rowcount == 0:
                raise NotFoundError(f"Action item with id {action_item_id} not found")
            connection.commit()
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to update action item: {e}") from e
    except NotFoundError:
        raise


