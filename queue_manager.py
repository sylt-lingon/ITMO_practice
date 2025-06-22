from datetime import datetime
from typing import Optional
import sqlite3


class User:
    def __init__(self, user_id: int, name: str):
        self.id = user_id
        self.name = name
        self.joined_at = datetime.now()


class QueueManager:
    def __init__(self, db_path: str = "queue.db"):
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        """Создает таблицу для очереди"""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def add_user(self, name: str) -> User:
        """Добавляет пользователя в очередь и возвращает его данные"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO users (name) VALUES (?)",
            (name,)
        )
        self.conn.commit()
        user_id = cursor.lastrowid
        return User(user_id, name)

    def get_position(self, user_id: int) -> Optional[int]:
        """Возвращает позицию пользователя"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM users 
            WHERE joined_at <= (SELECT joined_at FROM users WHERE id = ?)
        """, (user_id,))
        return cursor.fetchone()[0]

    def get_next(self) -> Optional[User]:
        """Возвращает следующего пользователя и удаляет его из очереди"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name FROM users ORDER BY joined_at LIMIT 1")
        row = cursor.fetchone()
        if row:
            user = User(row[0], row[1])
            cursor.execute("DELETE FROM users WHERE id = ?", (user.id,))
            self.conn.commit()
            return user
        return None

    def get_all_users(self):
        """Возвращает список всех пользователей в очереди"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name FROM users ORDER BY joined_at")
        return [{"user_id": row[0], "name": row[1]} for row in cursor.fetchall()]

    def remove_user(self, user_id: int) -> bool:
        """Удаляет пользователя из очереди по ID"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        self.conn.commit()
        return cursor.rowcount > 0
