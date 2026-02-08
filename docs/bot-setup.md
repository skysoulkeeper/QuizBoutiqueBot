# Bot Setup Guide

Step-by-step instructions for creating your Telegram bot and configuring it for use in groups or direct messages.

---

## Table of Contents

- [Creating Your Bot](#creating-your-bot)
- [Getting Your Bot Token](#getting-your-bot-token)
- [Configuring the Bot](#configuring-the-bot)
- [Group Setup (Optional)](#group-setup-optional)
- [Testing Your Bot](#testing-your-bot)
- [Troubleshooting](#troubleshooting)

---

## Creating Your Bot

### Step 1: Open BotFather

1. Open Telegram on any device (mobile, desktop, or web)
2. Search for **@BotFather** (official Telegram bot for creating bots)
3. Start a conversation by clicking **"Start"** or sending `/start`

⚠️ **Important:** Make sure it's the official @BotFather with a ✅ verified badge

---

### Step 2: Create New Bot

1. Send the command: `/newbot`
2. BotFather will ask for a **display name** (can be anything):
   ```
   Example: My Quiz Bot
   ```

3. BotFather will ask for a **username** (must end with 'bot'):
   ```
   Rules:
   - Must end with 'bot' (e.g., my_quiz_bot, MyQuizBot)
   - Must be unique across all Telegram bots
   - Can only contain letters, numbers, and underscores
   
   Examples:
   ✅ MyQuizBoutiqueBot
   ✅ quiz_master_bot
   ✅ CompanyQuizBot
   ❌ myquiz (doesn't end with 'bot')
   ❌ my-quiz-bot (contains hyphen)
   ```

---

### Step 3: Save Your Bot Token

BotFather will respond with a message containing your **bot token**:

```
Done! Congratulations on your new bot. You will find it at t.me/YourBotName.

Use this token to access the HTTP API:
123456789:ABCdefGHIjklMNOpqrsTUVwxyz1234567890

For a description of the Bot API, see this page:
https://core.telegram.org/bots/api
```

**⚠️ IMPORTANT:**
- **Copy and save this token** - you'll need it for configuration
- **Keep it secret** - anyone with this token can control your bot
- Never commit the token to public repositories

**Example token format:**
```
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz1234567890
           ↑
           The colon separates bot ID from secret key
```

---

## Getting Your Bot Token

### If You Lost Your Token

1. Open @BotFather
2. Send `/token`
3. Select your bot from the list
4. BotFather will show your token again

### Generating a New Token (Revoke Old)

If your token was compromised:

1. Open @BotFather
2. Send `/revoke`
3. Select your bot
4. Confirm token revocation
5. BotFather will generate a new token

⚠️ **Warning:** Old token will stop working immediately!

---

## Configuring the Bot

### Docker Configuration

**Recommended method** - Uses environment variables

1. Create `.env` file from example:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` file:
   ```bash
   nano .env  # or use any text editor
   ```

3. Add your token:
   ```bash
   # Required
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz1234567890
   
   # Optional
   TELEGRAM_CHAT_ID=              # Leave empty for now
   QBB_LANGUAGE=en                # en, es, ru, or ua
   QBB_LOG_LEVEL=INFO
   ```

4. Save and start:
   ```bash
   docker compose up -d
   ```

---

### Manual Configuration

**For local Python installation**

1. Copy example config:
   ```bash
   cp configs/config.yml.example configs/config.yml
   ```

2. Edit configuration file:
   ```bash
   nano configs/config.yml  # or use any text editor
   ```

3. Find the `telegram` section and update:
   ```yaml
   telegram:
     token: '123456789:ABCdefGHIjklMNOpqrsTUVwxyz1234567890'  # Your token here
     chat_id: ''                                                # Leave empty for now
     language: "en"                                             # en, es, ru, or ua
     bot_enabled: True                                          # True for DMs, False for groups only
   ```

4. Save and run:
   ```bash
   python app.py
   ```

---

## Group Setup (Optional)

If you want to use the bot in a Telegram group:

### Step 1: Disable Privacy Mode

By default, bots in groups can only see messages that:
- Start with `/` (commands)
- @mention the bot
- Are replies to the bot's messages

To let the bot see all messages (needed for quiz buttons):

1. Open @BotFather
2. Send `/mybots`
3. Select your bot
4. Click **"Bot Settings"**
5. Click **"Group Privacy"**
6. Click **"Turn Off"**

**What this does:**
- ✅ Bot can see all messages in the group
- ✅ Bot can respond to inline button clicks
- ✅ Necessary for quiz functionality in groups

**Privacy note:**
- The bot only processes quiz-related interactions
- Your bot's code is open-source and auditable
- No messages are stored or sent elsewhere

---

### Step 2: Add Bot to Group

1. Open your Telegram group
2. Click group name → **"Add Members"**
3. Search for your bot by username (e.g., @MyQuizBoutiqueBot)
4. Click **"Add"**

---

### Step 3: Grant Permissions (Optional)

The bot **does not require** admin rights for basic quiz functionality.

However, if you want to grant admin rights:

1. Open group → Group name → **"Administrators"**
2. Click **"Add Administrator"**
3. Select your bot
4. **Recommended permissions:**
   - ✅ Delete Messages (to clean up old quiz messages)
   - ❌ All other permissions can stay OFF

---

### Step 4: Get Group Chat ID (Optional)

If you want to save the group chat ID in configuration:

**Method 1: Using a Helper Bot**

1. Add @getidsbot to your group
2. It will automatically send the group chat ID
3. Copy the number (e.g., `-1001234567890`)
4. Remove @getidsbot from the group

**Method 2: Using @RawDataBot**

1. Add @RawDataBot to your group
2. Send any message
3. Look for `"chat": {"id": -1001234567890}`
4. Copy the ID
5. Remove @RawDataBot

**Method 3: From Bot Logs**

1. Start your bot
2. Send any message in the group
3. Check bot logs - you'll see the chat ID

**Save the Chat ID:**

**Docker:**
```bash
# In .env file
TELEGRAM_CHAT_ID=-1001234567890
```

**Manual:**
```yaml
# In configs/config.yml
telegram:
  chat_id: '-1001234567890'
```

⚠️ **Note:** Group chat IDs always start with a minus sign `-`

---

## Testing Your Bot

### Test in Direct Message (DM)

1. Open Telegram
2. Search for your bot by username (e.g., @MyQuizBoutiqueBot)
3. Click **"Start"** or send `/start`
4. You should see the main menu with buttons

**Expected response:**
```
Main menu:
[Tests] [Settings] [Help]
```

If you see this - **success!** ✅

---

### Test in Group

1. Go to your group where the bot was added
2. Send `/start`
3. Bot should respond with the main menu

**Multiple users:**
- Each user gets their own quiz session
- Settings are saved per user
- Users don't interfere with each other

---

### Verify Bot is Running

**Docker:**
```bash
# Check if container is running
docker compose ps

# View logs
docker compose logs -f quizboutiquebot
```

**Manual:**
```bash
# Terminal should show:
# "Application started"
# "Polling started"

# No error messages
```

---

## Troubleshooting

### Bot Doesn't Respond

**Possible causes:**

1. **Invalid Token**
   - Error: `telegram.error.InvalidToken`
   - Solution: Double-check token from @BotFather
   - Ensure token is in quotes in config: `'123456789:ABC...'`

2. **Bot Not Running**
   - Check if bot process/container is running
   - Docker: `docker compose ps`
   - Manual: Terminal should still be open

3. **Network Issues**
   - Bot can't reach Telegram servers
   - Check internet connection
   - Try enabling proxy if needed (see [Configuration](configuration.md))

4. **Group Privacy Mode**
   - Bot can't see messages in group
   - Solution: Disable privacy mode in @BotFather (see above)

---

### "Forbidden: bot was blocked by the user"

**Cause:** User blocked your bot

**Solution:**
- User must unblock the bot in Telegram
- Search bot → Click "Start" or "Restart"

---

### Bot Responds Slowly in Groups

**Cause:** Too many users using bot simultaneously

**Solutions:**
1. Increase bot resources (if using Docker)
2. Use bot in Direct Messages instead of groups
3. Configure `bot_enabled: True` to allow DM usage

---

### Multiple Users See Each Other's Quiz

This **should not happen** - the bot isolates each user's session.

If this occurs:
1. Check you're using the latest version
2. Report bug: https://github.com/skysoulkeeper/QuizBoutiqueBot/issues

---

### Can't Find Bot by Username

**Causes:**
1. **Username taken** - Choose a different username
2. **Typo in username** - Check spelling
3. **Bot not created yet** - Complete BotFather process first

**Solution:**
- Go to direct link: `https://t.me/YourBotUsername`
- Replace `YourBotUsername` with your actual bot username

---

### Token Leaked/Compromised

If you accidentally exposed your token:

1. **Immediately revoke it:**
   - @BotFather → `/revoke` → Select bot → Confirm
   
2. **Update configuration with new token:**
   - Docker: Update `.env`
   - Manual: Update `configs/config.yml`
   
3. **Restart bot:**
   - Docker: `docker compose restart`
   - Manual: Stop (`Ctrl+C`) and run `python app.py`

4. **Change any secrets** that might have been exposed

---

## Bot Settings in BotFather

Access additional bot settings via @BotFather → `/mybots` → Select your bot

### Useful Settings

**Edit Name**
- Change display name (doesn't affect username)
- Command: `/setname`

**Edit Description**
- Short description shown in search
- Command: `/setdescription`
- Example: "Interactive quiz bot with timer support"

**Edit About Text**
- Longer description shown in bot profile
- Command: `/setabouttext`

**Edit Profile Picture**
- Set bot avatar
- Command: `/setuserpic`

**Edit Commands**
- Set command hints shown to users
- Command: `/setcommands`
- Example:
  ```
  start - Start the bot and show main menu
  help - Show help information
  settings - Configure quiz settings
  ```

**Bot Settings Menu**
- Group Privacy - See [Group Setup](#step-1-disable-privacy-mode)
- Allow Groups - Enable/disable adding bot to groups
- Inline Mode - Not used by QuizBoutiqueBot
- Payments - Not used by QuizBoutiqueBot

---

## Advanced Configuration

### Enable/Disable Direct Messages

**In configuration:**

```yaml
# configs/config.yml
telegram:
  bot_enabled: True   # True = works in DMs, False = groups only
```

**Use cases:**
- `True` - Users can quiz in private (recommended for privacy)
- `False` - Force users to use bot in groups only

---

### Language Configuration

**Docker:**
```bash
# .env
QBB_LANGUAGE=en  # en, es, ru, ua
```

**Manual:**
```yaml
# configs/config.yml
telegram:
  language: "en"  # Default language for new users
```

**Supported languages:**
- 🇺🇸 English (`en`)
- 🇪🇸 Spanish (`es`)
- 🇷🇺 Russian (`ru`)
- 🇺🇦 Ukrainian (`ua`)

Users can change language in bot settings menu.

---

### User Authentication (Optional)

Restrict bot to specific Telegram users:

```yaml
# configs/config.yml
telegram:
  auth_enabled: True
  allowed_users:
    - 123456789   # Your Telegram user ID
    - 987654321   # Another user ID
```

**Get your Telegram ID:**
- Message @userinfobot
- Or @getidsbot

---

## Next Steps

- 📘 [Installation Guide](installation.md) - Install the bot
- 📘 [Configuration Guide](configuration.md) - Advanced settings
- 📘 [Adding Quizzes](../README.md#adding-your-own-quizzes) - Create custom quizzes
- 📘 [Database Documentation](database.md) - Database management

---

## Need Help?

- **Issues:** https://github.com/skysoulkeeper/QuizBoutiqueBot/issues
- **Email:** skysoulkeeper@gmail.com
- **Telegram:** Contact via bot issues if applicable
