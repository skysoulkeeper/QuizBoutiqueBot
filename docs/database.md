# Database Documentation

QuizBoutiqueBot uses **SQLite 3** with async operations via `aiosqlite` for persistent storage of user data, settings, and quiz history.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Database Files](#database-files)
- [Database Schema](#database-schema)
  - [users](#table-users)
  - [user_settings](#table-user_settings)
  - [quiz_attempts](#table-quiz_attempts)
  - [migrations](#table-migrations)
- [Indexes](#indexes)
- [Database Configuration](#database-configuration)
- [Migrations](#migrations)
- [Code Examples](#code-examples)
- [Backup & Maintenance](#backup--maintenance)

---

## Overview

**Database Type:** SQLite 3
**Driver:** `aiosqlite` (async wrapper)
**Location:** `data/db/qbb.db`
**Journal Mode:** WAL (Write-Ahead Logging)
**Foreign Keys:** Enabled

### Key Features

- ✅ **Per-user isolation**: Each user has separate settings and history
- ✅ **Async operations**: Non-blocking database access
- ✅ **Automatic migrations**: Schema versioning system
- ✅ **WAL mode**: Better concurrency and crash resistance
- ✅ **Foreign key constraints**: Data integrity enforcement
- ✅ **Indexed queries**: Fast lookups on common queries

---

## Database Files

SQLite in WAL mode creates **3 files**:

```
data/db/
├── qbb.db          # Main database file (schema + data)
├── qbb.db-wal      # Write-Ahead Log (transaction journal)
└── qbb.db-shm      # Shared Memory (inter-process coordination)
```

### File Descriptions

| File | Purpose | Can Delete? |
|------|---------|-------------|
| `qbb.db` | Primary database file containing all tables and data | ❌ Never |
| `qbb.db-wal` | Transaction log for pending writes | ⚠️ Only when DB is closed |
| `qbb.db-shm` | Shared memory index for WAL mode | ⚠️ Only when DB is closed |

**Important:** Always backup all 3 files together, or close the database before backup.

---

## Database Schema

### ER Diagram

```
┌─────────────────┐
│     users       │
├─────────────────┤
│ id (PK)         │
│ telegram_id (U) │◄─────┐
│ username        │      │
│ first_name      │      │
│ last_name       │      │
│ language        │      │
│ is_active       │      │
│ created_at      │      │
│ updated_at      │      │
│ last_seen_at    │      │
└─────────────────┘      │
                         │
         ┌───────────────┴───────────────┐
         │                               │
         │                               │
┌────────▼─────────┐          ┌─────────▼────────┐
│ user_settings    │          │  quiz_attempts   │
├──────────────────┤          ├──────────────────┤
│ user_id (PK, FK) │          │ id (PK)          │
│ questions_count  │          │ user_id (FK)     │
│ timer_enabled    │          │ category         │
│ timer_limit      │          │ quiz_name        │
│ questions_random │          │ total_questions  │
│ last_quiz        │          │ correct_count    │
│ last_category    │          │ success_rate     │
│ updated_at       │          │ passed           │
└──────────────────┘          │ started_at       │
                              │ finished_at      │
                              │ duration_seconds │
                              └──────────────────┘
```

---

## Table: `users`

Stores Telegram user information and account settings.

### Schema

```sql
CREATE TABLE users (
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

CREATE INDEX ix_users_telegram_id ON users(telegram_id);
```

### Columns

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | INTEGER | NO | AUTO | Internal user ID (primary key) |
| `telegram_id` | INTEGER | NO | - | Telegram user ID (unique) |
| `username` | TEXT | YES | NULL | Telegram @username |
| `first_name` | TEXT | YES | NULL | User's first name |
| `last_name` | TEXT | YES | NULL | User's last name |
| `language` | TEXT | YES | `'en'` | Interface language (`en`, `ru`, `ua`, `es`) |
| `is_active` | INTEGER | YES | `1` | Account status (1=active, 0=inactive) |
| `created_at` | TIMESTAMP | YES | CURRENT | When user first interacted with bot |
| `updated_at` | TIMESTAMP | YES | CURRENT | Last profile update |
| `last_seen_at` | TIMESTAMP | YES | NULL | Last bot interaction |

### Example Data

```sql
id | telegram_id | username        | first_name | language | created_at
---+-------------+-----------------+------------+----------+-------------------
1  | 881322156   | skysoulkeeper   | RVI        | ru       | 2026-02-08 18:35:04
2  | 123456789   | friend          | John       | en       | 2026-02-08 19:10:22
```

---

## Table: `user_settings`

Stores per-user quiz preferences and state.

### Schema

```sql
CREATE TABLE user_settings (
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
```

### Columns

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `user_id` | INTEGER | NO | References `users.id` (CASCADE delete) |
| `questions_count` | INTEGER | YES | Number of questions per quiz (5-100) |
| `timer_enabled` | INTEGER | YES | Timer on/off (1=enabled, 0=disabled) |
| `timer_limit` | INTEGER | YES | Timer duration in minutes (1-120) |
| `questions_random_enabled` | INTEGER | YES | Randomize questions (1=yes, 0=no) |
| `last_quiz` | TEXT | YES | Name of last quiz taken |
| `last_category` | TEXT | YES | Category of last quiz taken |
| `updated_at` | TIMESTAMP | YES | Last settings modification |

### Example Data

```sql
user_id | questions_count | timer_enabled | timer_limit | questions_random | last_quiz           | last_category
--------+-----------------+---------------+-------------+------------------+---------------------+--------------
1       | 5               | 1             | 15          | 1                | CA Powers to Arrest | BSIS
2       | 30              | 0             | NULL        | 1                | Python Basics       | Programming
```

### Notes

- **One-to-One relationship** with `users` table
- Settings created with default values on user's first interaction
- `ON DELETE CASCADE`: Settings deleted when user is deleted

---

## Table: `quiz_attempts`

Complete history of all quiz attempts by all users.

### Schema

```sql
CREATE TABLE quiz_attempts (
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

CREATE INDEX ix_quiz_attempts_user ON quiz_attempts(user_id, finished_at DESC);
```

### Columns

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | INTEGER | NO | Primary key |
| `user_id` | INTEGER | NO | References `users.id` (CASCADE delete) |
| `category` | TEXT | YES | Quiz category (e.g., "BSIS", "Programming") |
| `quiz_name` | TEXT | YES | Quiz file name (e.g., "CA Powers to Arrest EN") |
| `total_questions` | INTEGER | YES | Number of questions in this attempt |
| `correct_count` | INTEGER | YES | Number of correct answers |
| `success_rate` | REAL | YES | Percentage (0.0 - 100.0) |
| `passed` | INTEGER | YES | 1 if passed (≥80%), 0 if failed |
| `started_at` | TIMESTAMP | YES | When quiz started (ISO 8601 UTC) |
| `finished_at` | TIMESTAMP | YES | When quiz ended (ISO 8601 UTC) |
| `duration_seconds` | INTEGER | YES | Total time taken in seconds |

### Example Data

```sql
id | user_id | category | quiz_name                | total | correct | rate  | passed | finished_at
---+---------+----------+--------------------------+-------+---------+-------+--------+-------------------
1  | 1       | BSIS     | CA Powers to Arrest EN   | 5     | 0       | 0.0   | 0      | 2026-02-08T18:36:03Z
2  | 1       | BSIS     | CA Powers to Arrest EN   | 5     | 4       | 80.0  | 1      | 2026-02-08T19:15:22Z
3  | 2       | Python   | Python Basics            | 30    | 27      | 90.0  | 1      | 2026-02-08T20:01:45Z
```

### Notes

- **One-to-Many relationship** with `users` table (user can have many attempts)
- Indexed on `(user_id, finished_at DESC)` for fast "recent attempts" queries
- `ON DELETE CASCADE`: Attempts deleted when user is deleted
- Timestamps stored in ISO 8601 UTC format: `YYYY-MM-DDTHH:MM:SSZ`

---

## Table: `migrations`

Tracks applied database schema migrations.

### Schema

```sql
CREATE TABLE migrations (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Example Data

```sql
version | applied_at
--------+-------------------
1       | 2026-02-08 18:34:42
```

### Notes

- Managed automatically by `BotDatabase._run_migrations()`
- Current migration version: **1**
- Each migration runs exactly once

---

## Indexes

### `ix_users_telegram_id`

```sql
CREATE INDEX ix_users_telegram_id ON users(telegram_id);
```

**Purpose:** Fast lookup of users by Telegram ID
**Used in:** `get_or_create_user()` - every user interaction
**Benefit:** O(log n) instead of O(n) for user lookups

---

### `ix_quiz_attempts_user`

```sql
CREATE INDEX ix_quiz_attempts_user ON quiz_attempts(user_id, finished_at DESC);
```

**Purpose:** Fast retrieval of recent quiz attempts per user
**Used in:** Statistics queries, leaderboards, user history
**Benefit:** Composite index optimized for "user's recent attempts" queries

**Example optimized query:**
```sql
SELECT * FROM quiz_attempts
WHERE user_id = 1
ORDER BY finished_at DESC
LIMIT 10;
```

---

## Database Configuration

### In `config.yml`

```yaml
database:
  db_enabled: True                  # Must be True
  db_source: "data/db/qbb.db"       # Database file path
```

### In `app.py`

```python
db_path = db_cfg.get('db_source', 'data/db/qbb.db')
success_rate = config['base_settings']['success_rate']  # Default: 80

bot_db = BotDatabase(
    db_path=db_path,
    success_rate=success_rate,
    default_settings={
        'questions_count': 5,
        'timer_enabled': True,
        'timer_limit': 5,
        'questions_random_enabled': True
    }
)
```

### PRAGMA Settings

Applied on every connection in `database.py`:

```python
await self.conn.execute("PRAGMA journal_mode=WAL")       # WAL mode
await self.conn.execute("PRAGMA foreign_keys=ON")        # Foreign keys
await self.conn.execute("PRAGMA busy_timeout=5000")      # 5 second timeout
await self.conn.execute("PRAGMA synchronous=NORMAL")     # Balanced safety/speed
```

---

## Migrations

### How Migrations Work

1. **Version tracking**: `migrations` table stores applied versions
2. **Sequential execution**: Migrations run in order (1, 2, 3, ...)
3. **Idempotent**: Each migration runs exactly once
4. **Automatic**: Runs on bot startup in `app.py`

### Current Migration: v1

**File:** `utils/database.py`
**Function:** `BotDatabase._migration_001_init()`

Creates:
- `users` table
- `user_settings` table
- `quiz_attempts` table
- Indexes: `ix_users_telegram_id`, `ix_quiz_attempts_user`

### Adding New Migrations

```python
# In database.py
async def _run_migrations(self):
    # ...existing code...
    migrations = {
        1: self._migration_001_init,
        2: self._migration_002_add_statistics,  # ← Add new migration
    }
    # ...

async def _migration_002_add_statistics(self) -> None:
    """Add statistics tracking."""
    await self.conn.executescript(
        """
        CREATE TABLE user_statistics (
            user_id INTEGER PRIMARY KEY,
            total_attempts INTEGER DEFAULT 0,
            total_passed INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
    )
    await self.conn.commit()
```

---

## Code Examples

### Initialize Database

```python
from utils.database import BotDatabase

db = BotDatabase(
    db_path="data/db/qbb.db",
    success_rate=80,
    default_settings={'questions_count': 5}
)

await db.init()  # Creates tables, runs migrations
```

---

### Get or Create User

```python
# From handlers.py
user_id = await db.get_or_create_user(
    tg_user=update.effective_user,
    default_language='en'
)
# Returns internal user_id (e.g., 1, 2, 3...)
```

**What it does:**
1. Checks if `telegram_id` exists in `users`
2. If yes: updates `last_seen_at`, returns `user_id`
3. If no: creates new user, creates default settings, returns `user_id`

---

### Update User Settings

```python
# From settings.py
await db.update_user_settings(
    user_id=1,
    questions_count=30,
    timer_enabled=True,
    timer_limit=15
)
```

**Allowed fields:**
- `questions_count`
- `timer_enabled`
- `timer_limit`
- `questions_random_enabled`
- `last_quiz`
- `last_category`

---

### Save Quiz Attempt

```python
# From quizzes.py
await db.save_quiz_attempt(
    user_id=1,
    category="BSIS",
    quiz_name="CA Powers to Arrest EN",
    total_questions=5,
    correct_count=4,
    started_at="2026-02-08T18:35:00Z",
    finished_at="2026-02-08T18:36:03Z"
)
```

**Auto-calculated:**
- `success_rate` = (correct_count / total_questions) × 100
- `passed` = 1 if success_rate ≥ 80%, else 0
- `duration_seconds` = finished_at - started_at

---

### Get User Statistics

```python
stats = await db.get_user_stats(user_id=1)
# Returns:
# {
#     'total_attempts': 15,
#     'passed_count': 12,
#     'avg_success_rate': 85.33
# }
```

---

## Backup & Maintenance

### Manual Backup

```bash
# Stop bot first to close WAL
docker compose stop

# Backup all 3 files
tar -czf qbb-backup-$(date +%Y%m%d).tar.gz data/db/qbb.db*

# Restart bot
docker compose start
```

### Restore from Backup

```bash
# Stop bot
docker compose stop

# Extract backup
tar -xzf qbb-backup-20260208.tar.gz

# Restart bot
docker compose start
```

### Database Integrity Check

```bash
# Enter container
docker compose exec quizboutiquebot bash

# Check integrity
python3 << EOF
import sqlite3
conn = sqlite3.connect('/app/data/db/qbb.db')
result = conn.execute('PRAGMA integrity_check').fetchone()
print(result[0])  # Should print 'ok'
conn.close()
EOF
```

### Vacuum (Reclaim Space)

```bash
# Enter container
docker compose exec quizboutiquebot bash

# Vacuum database (reclaim deleted space)
python3 << EOF
import sqlite3
conn = sqlite3.connect('/app/data/db/qbb.db')
conn.execute('VACUUM')
conn.close()
EOF
```

### WAL Checkpoint (Merge WAL into main DB)

```bash
python3 << EOF
import sqlite3
conn = sqlite3.connect('/app/data/db/qbb.db')
conn.execute('PRAGMA wal_checkpoint(TRUNCATE)')
conn.close()
EOF
```

---

## Common Queries

### Get User's Recent Attempts

```sql
SELECT
    category,
    quiz_name,
    correct_count || '/' || total_questions as score,
    ROUND(success_rate, 1) || '%' as rate,
    CASE WHEN passed = 1 THEN 'PASS' ELSE 'FAIL' END as result,
    finished_at
FROM quiz_attempts
WHERE user_id = 1
ORDER BY finished_at DESC
LIMIT 10;
```

### Leaderboard (Top Users by Success Rate)

```sql
SELECT
    u.username,
    COUNT(qa.id) as attempts,
    SUM(CASE WHEN qa.passed = 1 THEN 1 ELSE 0 END) as passed,
    ROUND(AVG(qa.success_rate), 1) as avg_rate
FROM users u
JOIN quiz_attempts qa ON u.id = qa.user_id
GROUP BY u.id
HAVING attempts >= 5
ORDER BY avg_rate DESC
LIMIT 10;
```

### Popular Quizzes

```sql
SELECT
    category,
    quiz_name,
    COUNT(*) as times_taken,
    ROUND(AVG(success_rate), 1) as avg_success
FROM quiz_attempts
GROUP BY category, quiz_name
ORDER BY times_taken DESC
LIMIT 10;
```

---

## Troubleshooting

### "Database is locked" Error

**Cause:** Multiple processes trying to write simultaneously
**Solution:**
- WAL mode already enabled (helps with concurrency)
- Increase `busy_timeout` in `database.py`
- Check for zombie processes holding locks

### Missing Tables

**Cause:** Migration failed or DB file deleted
**Solution:**
```bash
# Delete corrupted DB
rm data/db/qbb.db*

# Restart bot (will recreate DB)
docker compose restart
```

### Foreign Key Violations

**Cause:** Trying to insert `user_settings` or `quiz_attempts` without valid `user_id`
**Solution:** Always call `get_or_create_user()` first

---

## Performance Tips

1. **Use indexes**: Already optimized for common queries
2. **Batch inserts**: For bulk data, use transactions
3. **WAL mode**: Already enabled for better concurrency
4. **Connection pooling**: Not needed (SQLite is single-file)
5. **Vacuum regularly**: Reclaim space from deleted records

---

## Security Considerations

1. **No SQL injection**: Using parameterized queries everywhere
2. **Foreign keys**: Prevent orphaned records
3. **Whitelisted updates**: `_ALLOWED_SETTINGS_KEYS` prevents arbitrary column updates
4. **No passwords stored**: Authentication via Telegram only
5. **Volume persistence**: DB survives container restarts (Docker volume)

---

## Related Files

- **Database class**: `utils/database.py`
- **Configuration**: `config.yml` (section `database:`)
- **Initialization**: `app.py` (lines 29-35, 47-49)
- **Usage in handlers**: `modules/telegram/handlers.py`
- **Usage in quizzes**: `modules/telegram/quizzes.py`
- **Usage in settings**: `modules/telegram/settings.py`

---

## Documentation
- [Main README](../README.md) - General project documentation
- [Docker Deployment Guide](docs/docker.md)
- [GitHub Issues](https://github.com/skysoulkeeper/QuizBoutiqueBot/issues)
