"""
FARADAY AI - User Database
SQLite user database (placeholder)
"""

from typing import Optional, Dict, Any
from pathlib import Path
import sqlite3

from config.settings import settings
from utils.logger import logger


class UserDatabase:
    """
    User Database Manager.

    Note: This is a basic placeholder using SQLite.
    For production, use proper ORM like SQLAlchemy.
    """

    def __init__(self):
        """Initialize database"""
        self.db_path = settings.data_dir / "users.db"
        self._init_database()
        logger.info(f"💾 User database initialized: {self.db_path}")

    def _init_database(self):
        """Initialize database schema"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            """)

            conn.commit()
            conn.close()

            logger.info("✅ Database schema initialized")

        except Exception as e:
            logger.error(f"❌ Database initialization error: {e}")

    def create_user(self, username: str, password_hash: str, email: Optional[str] = None) -> Dict[str, Any]:
        """Create new user"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
                (username, password_hash, email)
            )

            conn.commit()
            user_id = cursor.lastrowid
            conn.close()

            logger.info(f"✅ User created: {username}")

            return {
                "success": True,
                "user_id": user_id,
                "username": username
            }

        except sqlite3.IntegrityError:
            logger.warning(f"⚠️  User already exists: {username}")
            return {"success": False, "error": "User already exists"}
        except Exception as e:
            logger.error(f"❌ Error creating user: {e}")
            return {"success": False, "error": str(e)}

    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()

            conn.close()

            if row:
                return dict(row)
            return None

        except Exception as e:
            logger.error(f"❌ Error getting user: {e}")
            return None


# Singleton
_user_database_instance = None


def get_user_database() -> UserDatabase:
    """Get or create user database singleton"""
    global _user_database_instance
    if _user_database_instance is None:
        _user_database_instance = UserDatabase()
    return _user_database_instance


__all__ = ['UserDatabase', 'get_user_database']
