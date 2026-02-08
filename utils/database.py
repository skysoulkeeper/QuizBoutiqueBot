# MIT License
# Copyright (c) 2024 skysoulkeeper
# See LICENSE file for more details.

"""
utils/database.py

Lightweight async SQLite persistence for per-user settings and stats.
- aiosqlite connection with WAL, foreign keys, busy timeout.
- Simple in-code migrations table with versioning.
- Minimal repository-style methods used by Telegram handlers.

NOTE: Keep comments and identifiers in English only.
"""

import aiosqlite
from pathlib import Path
from typing import Optional, Dict, Any
import datetime as dt


_ALLOWED_SETTINGS_KEYS = {
    "questions_count",
    "timer_enabled",
    "timer_limit",
    "questions_random_enabled",
    "last_quiz",
    "last_category",
}


class BotDatabase:
    def __init__(
        self,
        db_path: str = "data/db/qbb.db",
        success_rate: int = 80,
        default_settings: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn: Optional[aiosqlite.Connection] = None
        self.success_rate = int(success_rate)
        self.default_settings = default_settings or {}

    async def init(self) -> None:
        """Initialize database and run migrations."""
        # Use a small timeout and busy_timeout to reduce 'database is locked' errors
        self.conn = await aiosqlite.connect(self.db_path.as_posix(), timeout=5)
        self.conn.row_factory = aiosqlite.Row

        # Pragmas for better reliability
        await self.conn.execute("PRAGMA journal_mode=WAL")
        await self.conn.execute("PRAGMA foreign_keys=ON")
        await self.conn.execute("PRAGMA busy_timeout=5000")
        await self.conn.execute("PRAGMA synchronous=NORMAL")
        await self.conn.commit()

        await self._run_migrations()

    async def close(self) -> None:
        if self.conn:
            await self.conn.close()
            self.conn = None

    async def _run_migrations(self) -> None:
        assert self.conn is not None
        # Migrations table
        await self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS migrations (
                version INTEGER PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        await self.conn.commit()

        # Current version
        cur = await self.conn.execute("SELECT IFNULL(MAX(version), 0) FROM migrations")
        row = await cur.fetchone()
        current = int(row[0]) if row and row[0] is not None else 0

        # Available migrations
        migrations = {
            1: self._migration_001_init,
        }

        for version, mig in sorted(migrations.items()):
            if version > current:
                await mig()
                await self.conn.execute(
                    "INSERT INTO migrations (version) VALUES (?)", (version,)
                )
                await self.conn.commit()

    async def _migration_001_init(self) -> None:
        assert self.conn is not None
        await self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                language TEXT DEFAULT 'en',
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen_at TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS user_settings (
                user_id INTEGER PRIMARY KEY,
                questions_count INTEGER,
                timer_enabled INTEGER,
                timer_limit INTEGER,
                questions_random_enabled INTEGER,
                last_quiz TEXT,
                last_category TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS quiz_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                category TEXT,
                quiz_name TEXT,
                total_questions INTEGER,
                correct_count INTEGER,
                success_rate REAL,
                passed INTEGER,
                started_at TIMESTAMP,
                finished_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                duration_seconds INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS ix_users_telegram_id ON users(telegram_id);
            CREATE INDEX IF NOT EXISTS ix_quiz_attempts_user ON quiz_attempts(user_id, finished_at DESC);
            """
        )
        await self.conn.commit()

    # Utilities
    @staticmethod
    def _to_bool_int(val: Any) -> int:
        return 1 if bool(val) else 0

    @staticmethod
    def _now_utc() -> str:
        return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    # Users
    async def get_or_create_user(self, tg_user, default_language: str) -> int:
        """Return internal user_id for given Telegram user, creating as needed."""
        assert self.conn is not None

        cur = await self.conn.execute(
            "SELECT id FROM users WHERE telegram_id = ?", (tg_user.id,)
        )
        row = await cur.fetchone()
        if row:
            user_id = int(row[0])
            await self.conn.execute(
                "UPDATE users SET updated_at = CURRENT_TIMESTAMP, last_seen_at = ? WHERE id = ?",
                (self._now_utc(), user_id),
            )
            await self.conn.commit()
            return user_id

        # Determine initial language
        lang = (getattr(tg_user, "language_code", None) or default_language or "en").lower()
        if lang == "uk":  # normalize
            lang = "ua"

        cur = await self.conn.execute(
            """
            INSERT INTO users(telegram_id, username, first_name, last_name, language, last_seen_at)
            VALUES(?, ?, ?, ?, ?, ?)
            """,
            (
                tg_user.id,
                getattr(tg_user, "username", None),
                getattr(tg_user, "first_name", None),
                getattr(tg_user, "last_name", None),
                lang,
                self._now_utc(),
            ),
        )
        await self.conn.commit()
        user_id = int(cur.lastrowid)

        # Create default settings based on defaults passed in constructor
        await self.conn.execute(
            """
            INSERT INTO user_settings(user_id, questions_count, timer_enabled, timer_limit, questions_random_enabled)
            VALUES(?, ?, ?, ?, ?)
            """,
            (
                user_id,
                int(self.default_settings.get("questions_count", 5)),
                self._to_bool_int(self.default_settings.get("timer_enabled", True)),
                int(self.default_settings.get("timer_limit", 5)),
                self._to_bool_int(self.default_settings.get("questions_random_enabled", True)),
            ),
        )
        await self.conn.commit()
        return user_id

    async def get_user_language(self, user_id: int) -> str:
        assert self.conn is not None
        cur = await self.conn.execute("SELECT language FROM users WHERE id = ?", (user_id,))
        row = await cur.fetchone()
        return (row[0] if row and row[0] else "en")

    async def update_user_language(self, user_id: int, language: str) -> None:
        assert self.conn is not None
        await self.conn.execute(
            "UPDATE users SET language = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (language, user_id),
        )
        await self.conn.commit()

    # Settings
    async def get_user_settings(self, user_id: int) -> Dict[str, Any]:
        assert self.conn is not None
        cur = await self.conn.execute(
            """
            SELECT questions_count, timer_enabled, timer_limit, questions_random_enabled, last_quiz, last_category
            FROM user_settings WHERE user_id = ?
            """,
            (user_id,),
        )
        row = await cur.fetchone()
        if not row:
            return {}
        return {
            "questions_count": int(row[0]) if row[0] is not None else self.default_settings.get("questions_count"),
            "timer_enabled": bool(row[1]) if row[1] is not None else self.default_settings.get("timer_enabled"),
            "timer_limit": int(row[2]) if row[2] is not None else self.default_settings.get("timer_limit"),
            "questions_random_enabled": bool(row[3]) if row[3] is not None else self.default_settings.get("questions_random_enabled"),
            "last_quiz": row[4],
            "last_category": row[5],
        }

    async def update_user_settings(self, user_id: int, **kwargs: Any) -> None:
        assert self.conn is not None
        # Whitelist fields to prevent unintended updates
        updates = {k: v for k, v in kwargs.items() if k in _ALLOWED_SETTINGS_KEYS}
        if not updates:
            return

        set_parts = [f"{k} = ?" for k in updates.keys()]
        values = list(updates.values())
        values.append(user_id)

        await self.conn.execute(
            f"UPDATE user_settings SET {', '.join(set_parts)}, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
            values,
        )
        await self.conn.commit()

    # Stats
    async def save_quiz_attempt(
        self,
        user_id: int,
        category: Optional[str],
        quiz_name: Optional[str],
        total_questions: int,
        correct_count: int,
        started_at: Optional[str] = None,
        finished_at: Optional[str] = None,
        duration_seconds: Optional[int] = None,
    ) -> None:
        assert self.conn is not None
        finished = finished_at or self._now_utc()
        start = started_at or finished
        duration = duration_seconds
        if duration is None:
            try:
                dt_start = dt.datetime.fromisoformat(start.replace("Z", "+00:00"))
                dt_finish = dt.datetime.fromisoformat(finished.replace("Z", "+00:00"))
                duration = int((dt_finish - dt_start).total_seconds())
            except Exception:
                duration = 0

        rate = (correct_count / total_questions * 100.0) if total_questions > 0 else 0.0
        passed = 1 if rate >= float(self.success_rate) else 0

        await self.conn.execute(
            """
            INSERT INTO quiz_attempts(user_id, category, quiz_name, total_questions, correct_count, success_rate, passed, started_at, finished_at, duration_seconds)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                category,
                quiz_name,
                int(total_questions),
                int(correct_count),
                float(rate),
                int(passed),
                start,
                finished,
                int(duration),
            ),
        )
        await self.conn.commit()

    async def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        assert self.conn is not None
        cur = await self.conn.execute(
            """
            SELECT 
                COUNT(*) as total_attempts,
                SUM(CASE WHEN passed = 1 THEN 1 ELSE 0 END) as passed_count,
                AVG(success_rate) as avg_success_rate
            FROM quiz_attempts WHERE user_id = ?
            """,
            (user_id,),
        )
        row = await cur.fetchone()
        return {
            "total_attempts": int(row[0] or 0),
            "passed_count": int(row[1] or 0),
            "avg_success_rate": round(float(row[2] or 0.0), 2),
        }
