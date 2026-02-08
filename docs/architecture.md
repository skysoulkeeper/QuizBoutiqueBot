# Project Architecture

Complete guide to QuizBoutiqueBot's file structure, modules, and architecture.

---

## Table of Contents

- [Project Structure](#project-structure)
- [Core Components](#core-components)
- [Module Breakdown](#module-breakdown)
- [Data Flow](#data-flow)
- [Configuration System](#configuration-system)
- [Extending the Bot](#extending-the-bot)

---

## Project Structure

```
QuizBoutiqueBot/
├── app.py                      # Application entry point
├── entrypoint.py               # Docker container entrypoint
├── requirements.txt            # Python dependencies
│
├── configs/                    # Configuration files
│   ├── config.yml              # Main configuration (production)
│   └── config.dev.yml          # Development config (auto-generated)
│
├── modules/                    # Bot modules
│   ├── categories.py           # Quiz category handling
│   └── telegram/               # Telegram bot components
│       ├── handlers.py         # Command and callback handlers
│       ├── menus.py            # Menu displays and keyboards
│       ├── quizzes.py          # Quiz logic and flow
│       └── settings.py         # User settings management
│
├── utils/                      # Utility modules
│   ├── configs.py              # Configuration loader
│   ├── database.py             # SQLite database layer
│   ├── directories.py          # Directory initialization
│   ├── initializer.py          # Application initialization
│   ├── localization.py         # Multi-language support
│   ├── logger.py               # Logging system
│   └── proxy.py                # Proxy configuration
│
├── locales/                    # Localization files
│   ├── en.yml                  # English
│   ├── es.yml                  # Spanish
│   ├── ru.yml                  # Russian
│   └── ua.yml                  # Ukrainian
│
├── data/                       # Runtime data
│   ├── db/                     # SQLite database files
│   │   ├── qbb.db              # Main database
│   │   ├── qbb.db-wal          # Write-ahead log
│   │   └── qbb.db-shm          # Shared memory
│   ├── logs/                   # Application logs
│   ├── questions/              # Quiz question pools
│   │   ├── Category1/          # Quiz category
│   │   │   └── quiz1.json      # Quiz file
│   │   └── Category2/
│   │       └── quiz2.json
│   └── recognition/            # Reserved for future use
│
├── docs/                       # Documentation
│   ├── installation.md         # Installation guide
│   ├── bot-setup.md            # Bot configuration guide
│   ├── database.md             # Database documentation
│   ├── docker.md               # Docker deployment guide
│   └── architecture.md         # This file
│
├── docker/                     # Docker-related files (if separate)
│   └── ...
│
├── Dockerfile                  # Docker image definition
├── docker-compose.yml          # Docker Compose (production)
├── docker-compose.dev.yml      # Docker Compose (development)
├── .dockerignore               # Docker build exclusions
├── Makefile                    # Build automation
│
├── .env.example                # Environment variables template
├── .gitignore                  # Git exclusions
│
└── README.md                   # Main documentation
```

---

## Core Components

### 1. Application Entry Point

**File:** `app.py`

**Purpose:** Initializes and starts the Telegram bot

**Responsibilities:**
- Load configuration
- Initialize database
- Set up logging
- Register handlers
- Start polling loop

**Flow:**
```python
main()
  ├─> Loader.initialize()           # Load config, setup logging
  ├─> BotHandler(...)                # Create handler instance
  ├─> BotDatabase.init()             # Initialize database
  ├─> Application.builder()         # Setup Telegram bot
  ├─> Add handlers                   # Register commands/callbacks
  └─> run_polling()                  # Start bot
```

---

### 2. Docker Entrypoint

**File:** `entrypoint.py`

**Purpose:** Container startup script for Docker deployment

**Responsibilities:**
- Read environment variables
- Merge ENV with base configuration
- Generate `config.dev.yml`
- Execute `app.py`

**Docker flow:**
```
Container starts
  ├─> entrypoint.py
  │     ├─> Read ENV vars (TELEGRAM_BOT_TOKEN, QBB_*)
  │     ├─> Load configs/config.yml
  │     ├─> Merge and write configs/config.dev.yml
  │     └─> exec python app.py
  └─> Bot runs
```

---

## Module Breakdown

### Telegram Modules (`modules/telegram/`)

#### `handlers.py`

**Purpose:** Main bot handler class

**Key Components:**
- `BotHandler` - Main handler class
- `ensure_user_context()` - Load per-user settings from DB
- `start()` - Handle `/start` command
- `button()` - Route callback queries to appropriate handlers

**Handler routing:**
```python
{
  "tests": show_tests_menu,
  "settings": show_settings_menu,
  "help": show_help_section,
  "questions_count": show_questions_count_menu,
  "timer_status": show_timer_menu,
  "timer_limit": show_timer_limit_menu,
  "choose_language": show_language_menu,
  "restart": restart_last_quiz,
  "next_question": send_question,
  "main_menu": go_to_main_menu
}
```

---

#### `menus.py`

**Purpose:** Menu display functions

**Functions:**
- `show_main_menu()` - Display main menu
- `show_tests_menu()` - Display quiz categories
- `show_settings_menu()` - Display settings options
- `show_questions_count_menu()` - Question count selection
- `show_timer_menu()` - Timer enable/disable
- `show_timer_limit_menu()` - Timer duration selection
- `show_language_menu()` - Language selection

**Pattern:**
```python
async def show_menu(update, context):
    localization = context.user_data.get('localization')
    keyboard = [[InlineKeyboardButton(text, callback_data)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.edit_text(text, reply_markup)
```

---

#### `quizzes.py`

**Purpose:** Quiz logic and flow control

**Key Functions:**
- `handle_category_selection()` - User selects category
- `handle_quiz_selection()` - User starts a quiz
- `send_question()` - Display quiz question
- `handle_quiz_response()` - Process user answer
- `send_results()` - Display quiz results
- `start_timer()` - Countdown timer
- `end_quiz_due_to_time_limit()` - Timer expiry

**Quiz flow:**
```
User clicks category
  └─> handle_category_selection()
        └─> Display quiz list

User clicks quiz
  └─> handle_quiz_selection()
        ├─> Load questions from JSON
        ├─> Initialize user context
        ├─> Save to database (last_quiz)
        ├─> Start timer (if enabled)
        └─> send_question()

User answers
  └─> handle_quiz_response()
        ├─> Check answer
        ├─> Update score
        ├─> Next question OR results
        └─> send_results() (if done)
              └─> Save attempt to database
```

---

#### `settings.py`

**Purpose:** User settings management

**Functions:**
- `handle_questions_count_selection()` - Update question count
- `handle_timer_selection()` - Toggle timer
- `handle_timer_limit_selection()` - Update timer duration
- `handle_questions_random_selection()` - Toggle randomization

**Pattern:**
```python
async def handle_setting(update, context, value):
    context.user_data['setting'] = value
    db = context.application.bot_data.get('db')
    await db.update_user_settings(user_id, setting=value)
    await show_confirmation(update, context)
```

---

### Utility Modules (`utils/`)

#### `database.py`

**Purpose:** SQLite database layer

**Key Class:** `BotDatabase`

**Methods:**
- `init()` - Initialize database and run migrations
- `get_or_create_user()` - Get user or create new
- `get_user_language()` - Get user's language
- `update_user_language()` - Update language
- `get_user_settings()` - Load user settings
- `update_user_settings()` - Save settings
- `save_quiz_attempt()` - Record quiz completion
- `get_user_stats()` - Get user statistics

See [Database Documentation](database.md) for details.

---

#### `localization.py`

**Purpose:** Multi-language support

**Key Class:** `Localization`

**Usage:**
```python
loc = Localization('en')
text = loc.get('welcome_message', username='John')
# Result: "Welcome, John!"
```

**Translation files:** `locales/{language}.yml`

---

#### `logger.py`

**Purpose:** Logging system

**Supported frameworks:**
- **loguru** (default, recommended)
- **Python logging** (fallback)

**Features:**
- Structured JSON logging
- File rotation
- Configurable log levels
- Custom formatters

---

#### `configs.py`

**Purpose:** Configuration file loader

**Key Class:** `ConfigLoader`

**Methods:**
- `load_config()` - Load YAML configuration
- `ConfigFileHandler` - Watch for config changes (optional)

**Configuration priority:**
1. `config.dev.yml` (if exists, from Docker ENV)
2. `config.yml` (base configuration)

---

#### `initializer.py`

**Purpose:** Application initialization

**Key Class:** `Loader`

**Responsibilities:**
- Load configuration
- Setup logging
- Setup proxy (if enabled)
- Initialize directories
- Watch config file (if enabled)

**Returns:**
```python
config, logger, proxy_handler, localization, 
telegram_token, telegram_chat_id, questions_directory, parse_mode
```

---

#### `proxy.py`

**Purpose:** Proxy configuration and testing

**Key Class:** `ProxyHandler`

**Supported protocols:**
- HTTP/HTTPS
- SOCKS4/SOCKS5

**Methods:**
- `set_proxy()` - Configure proxy
- `test_proxy_access()` - Verify connectivity
- `make_request_through_proxy()` - Make proxied request

---

#### `directories.py`

**Purpose:** Directory initialization

**Function:** `initialize_directories()`

**Creates:**
- `data/logs/` (if logging to file)
- `data/db/` (if database enabled)
- `data/questions/`
- `data/recognition/`

---

### Category Module (`modules/categories.py`)

**Purpose:** Quiz category management

**Key Class:** `CategoryHandler`

**Methods:**
- `get_categories()` - List all quiz categories
- Validates category directories
- Scans `data/questions/` for subdirectories

---

## Data Flow

### User Interaction Flow

```
1. User opens bot
   └─> /start command
       └─> handlers.py: start()
           └─> ensure_user_context()
               ├─> Check database for user
               ├─> Load user settings
               ├─> Set user language
               └─> Initialize context.user_data
           └─> menus.py: show_main_menu()

2. User clicks "Tests"
   └─> handlers.py: button()
       └─> show_tests_menu()
           └─> categories.py: get_categories()
               └─> Scan data/questions/
           └─> Display category buttons

3. User selects category
   └─> quizzes.py: handle_category_selection()
       └─> List JSON files in category/
       └─> Display quiz buttons

4. User starts quiz
   └─> quizzes.py: handle_quiz_selection()
       ├─> Load JSON questions
       ├─> Apply randomization (if enabled)
       ├─> Save to database (last_quiz)
       ├─> Start timer (if enabled)
       └─> send_question()

5. User answers question
   └─> quizzes.py: handle_quiz_response()
       ├─> Check answer
       ├─> Update score
       └─> Next question or results

6. Quiz completes
   └─> quizzes.py: send_results()
       ├─> Calculate success rate
       ├─> database.py: save_quiz_attempt()
       └─> Show restart/menu options
```

---

### Configuration Flow

```
Docker Deployment:
  .env file
    └─> entrypoint.py
        ├─> Read environment variables
        ├─> Load configs/config.yml
        ├─> Merge ENV overrides
        └─> Write configs/config.dev.yml
            └─> app.py loads config.dev.yml

Manual Deployment:
  configs/config.yml
    └─> app.py
        └─> ConfigLoader.load_config()
            └─> Returns config dict
```

---

### Database Flow

```
App Startup:
  app.py
    └─> BotDatabase.init()
        ├─> Connect to SQLite
        ├─> Set PRAGMA (WAL, foreign keys)
        └─> Run migrations
            └─> Check migrations table
                └─> Run new migrations if needed

User Interaction:
  handlers.py: ensure_user_context()
    └─> database.get_or_create_user()
        ├─> Check if user exists
        ├─> Create if new (with default settings)
        └─> Return user_id
    └─> database.get_user_settings()
        └─> Load from user_settings table

Settings Change:
  settings.py: handle_*_selection()
    └─> database.update_user_settings()
        └─> UPDATE user_settings WHERE user_id = ?

Quiz Completion:
  quizzes.py: send_results()
    └─> database.save_quiz_attempt()
        ├─> Calculate success_rate
        ├─> Determine passed (≥80%)
        └─> INSERT INTO quiz_attempts
```

---

## Configuration System

### Configuration Hierarchy

```
Priority (highest to lowest):
1. Environment Variables (Docker)
   └─> QBB_LOG_LEVEL=DEBUG
2. config.dev.yml (generated from ENV)
3. config.yml (base configuration)
```

### Configuration Sections

**Base Settings:**
```yaml
base_settings:
  env: "prod"                    # Environment
  questions_count: [5, 10, 15]   # Question pool options
  success_rate: 80                # Pass threshold
  timer_enabled: True             # Timer default
  timer_limit: [5, 10, 15]       # Timer options
  questions_random_enabled: True  # Randomization default
```

**Telegram:**
```yaml
telegram:
  token: ''                      # Bot token
  chat_id: ''                    # Optional group ID
  language: "en"                 # Default language
  bot_enabled: True              # Allow DMs
  parse_mode: "HTML"             # Message formatting
```

**Database:**
```yaml
database:
  db_enabled: True               # Enable SQLite
  db_source: "data/db/qbb.db"   # Database path
```

**Logging:**
```yaml
logging:
  log_framework: "loguru"        # Logger
  log_level: "INFO"              # Level
  log_to_file: False             # File logging
```

**Proxy:**
```yaml
proxy_settings:
  proxy_enabled: False           # Enable proxy
  proxy_host: ""                 # Proxy server
  proxy_port: 1080               # Port
  proxy_protocol: "socks"        # Protocol
```

---

## Extending the Bot

### Adding a New Quiz Category

1. Create directory: `data/questions/NewCategory/`
2. Add quiz JSON files: `data/questions/NewCategory/quiz1.json`
3. Bot will auto-detect on next menu display

**Quiz JSON format:**
```json
[
  {
    "question": "What is 2+2?",
    "answers": ["A: 3", "B: 4", "C: 5", "D: 6"],
    "correct_answer": "B: 4",
    "explanation": "2+2 equals 4"
  }
]
```

---

### Adding a New Language

1. Create file: `locales/fr.yml` (for French)
2. Copy structure from `locales/en.yml`
3. Translate all strings
4. Add flag emoji to `config.yml`:
   ```yaml
   emoji:
     language_flags:
       fr: "🇫🇷"
   ```
5. Restart bot

---

### Adding a New Setting

1. **Add to database** (`utils/database.py`):
   ```python
   # In _migration_001_init():
   CREATE TABLE user_settings (
       ...
       new_setting INTEGER,
       ...
   )
   
   # Add to _ALLOWED_SETTINGS_KEYS:
   _ALLOWED_SETTINGS_KEYS = {
       ...,
       "new_setting",
   }
   ```

2. **Add menu** (`modules/telegram/menus.py`):
   ```python
   async def show_new_setting_menu(update, context):
       keyboard = [
           [InlineKeyboardButton("Option 1", callback_data="set_new_setting_1")],
           [InlineKeyboardButton("Option 2", callback_data="set_new_setting_2")]
       ]
       ...
   ```

3. **Add handler** (`modules/telegram/settings.py`):
   ```python
   async def handle_new_setting_selection(update, context, value):
       context.user_data['new_setting'] = value
       db = context.application.bot_data.get('db')
       await db.update_user_settings(user_id, new_setting=value)
       ...
   ```

4. **Add translations** (`locales/*.yml`):
   ```yaml
   new_setting_menu: "Choose new setting:"
   new_setting_option: "New Setting ({value})"
   ```

5. **Register in handlers** (`modules/telegram/handlers.py`):
   ```python
   handlers = {
       ...
       "new_setting": show_new_setting_menu,
   }
   ```

---

### Adding a New Command

1. **Create handler** (`modules/telegram/handlers.py`):
   ```python
   async def stats(self, update, context):
       await self.ensure_user_context(update, context)
       db = context.application.bot_data.get('db')
       stats = await db.get_user_stats(context.user_data['user_id'])
       await update.message.reply_text(f"Stats: {stats}")
   ```

2. **Register handler** (`app.py`):
   ```python
   application.add_handler(CommandHandler("stats", bot_handler.stats))
   ```

3. **Add to BotFather** (optional):
   - @BotFather → `/setcommands`
   - Add: `stats - View your quiz statistics`

---

## File Dependencies

```
app.py
  ├─> utils/initializer.py
  │     ├─> utils/configs.py
  │     ├─> utils/logger.py
  │     ├─> utils/proxy.py
  │     ├─> utils/localization.py
  │     └─> utils/directories.py
  ├─> utils/database.py
  └─> modules/telegram/handlers.py
        ├─> modules/telegram/menus.py
        │     └─> modules/categories.py
        ├─> modules/telegram/quizzes.py
        └─> modules/telegram/settings.py
```

---

## Testing

### Manual Testing

```bash
# Run locally
python app.py

# Test specific functionality
# - Send /start
# - Click through menus
# - Take a quiz
# - Change settings
```

### Database Testing

```python
# Test database operations
python << EOF
import asyncio
from utils.database import BotDatabase

async def test():
    db = BotDatabase("test.db", success_rate=80)
    await db.init()
    
    # Test user creation
    class FakeUser:
        id = 123456789
        username = "testuser"
        first_name = "Test"
        last_name = "User"
    
    user_id = await db.get_or_create_user(FakeUser(), "en")
    print(f"Created user: {user_id}")
    
    await db.close()

asyncio.run(test())
EOF
```

---

## Performance Considerations

### Database

- **WAL mode** enabled for concurrent reads
- **Indexes** on frequently queried columns
- **Connection pooling** not needed (single-file SQLite)

### Memory

- Quiz questions loaded per-user, not globally
- User context isolated in `context.user_data`
- No persistent in-memory cache

### Scalability

- **Vertical**: Single bot instance handles ~1000 concurrent users
- **Horizontal**: Not supported (SQLite limitations)
- **Solution for high load**: Use PostgreSQL instead of SQLite

---

## Security

### Bot Token

- Stored in `.env` (Docker) or `config.yml` (Manual)
- Never committed to git (`.gitignore` includes `.env` and `config.yml`)
- Passed via environment variables in Docker

### Database

- SQLite file permissions: User-readable only
- No SQL injection (parameterized queries)
- Foreign keys enforce referential integrity

### User Data

- User IDs and settings only (no passwords)
- No sensitive data stored
- Quiz history includes scores only

---

## Related Documentation

- [Installation Guide](installation.md) - How to install
- [Bot Setup Guide](bot-setup.md) - Configure bot and token
- [Database Documentation](database.md) - Database schema
- [Docker Guide](docker.md) - Container deployment
- [README](../README.md) - Main documentation

---

## Need Help?

- **Issues:** https://github.com/skysoulkeeper/QuizBoutiqueBot/issues
- **Email:** skysoulkeeper@gmail.com
