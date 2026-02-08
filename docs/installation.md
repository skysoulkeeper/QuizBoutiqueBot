# Installation Guide

Complete installation instructions for QuizBoutiqueBot on Windows, macOS, and Linux.

---

## Table of Contents

- [Docker Installation (Recommended)](#docker-installation-recommended)
- [Manual Installation](#manual-installation)
  - [Prerequisites](#prerequisites)
  - [Installation Steps](#installation-steps)
- [Troubleshooting](#troubleshooting)

---

## Docker Installation (Recommended)

🐳 **Easiest and fastest way to run the bot**

### Supported Platforms

- **Intel/AMD (amd64)** - Standard PCs, servers, NAS devices (Synology, QNAP, TerraMaster)
- **ARM (arm64)** - Apple Silicon (M1/M2/M3/M4), Raspberry Pi 4/5

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/skysoulkeeper/QuizBoutiqueBot.git
cd QuizBoutiqueBot

# 2. Configure environment
cp .env.example .env
nano .env  # Add your TELEGRAM_BOT_TOKEN

# 3. Launch (pulls pre-built image from GitHub Container Registry)
docker compose up -d

# 4. View logs
docker compose logs -f
```

📘 **For detailed Docker documentation, see [Docker Deployment Guide](docker.md)**

---

## Manual Installation

💻 **Run locally without Docker** - Best for development

---

### Prerequisites

#### Required Software

- **Python 3.8 or later** (3.11+ recommended)
- **pip** (Python package manager, usually included with Python)
- **Git** (optional, for cloning repository)

---

### Installation Steps

#### 1. Install Python

Get Python installed on your operating system:

##### Windows

1. Go to https://www.python.org/downloads/windows/
2. Download the latest Python 3.x installer (3.11+ recommended)
3. **Important:** During installation, check ✅ **"Add Python to PATH"**
4. Click "Install Now"

**Verify installation:**
```cmd
python --version
# or
py --version
```

**How to open terminal:**
- Press `Win` key
- Type "Command Prompt" or "PowerShell"
- Press Enter

##### macOS

**Option A: Official Installer (Recommended for beginners)**
1. Go to https://www.python.org/downloads/macos/
2. Download the `.pkg` installer for Python 3.x (3.11+ recommended)
3. Run the installer and follow prompts

**Option B: Homebrew (For advanced users)**
```bash
brew install python
```

**Verify installation:**
```bash
python3 --version
pip3 --version
```

**How to open terminal:**
- Press `Cmd + Space` (Spotlight)
- Type "Terminal"
- Press Enter

##### Linux

**How to open terminal:**
- Usually: `Ctrl + Alt + T`
- Or find "Terminal" in your applications menu

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
```

**Fedora:**
```bash
sudo dnf install -y python3 python3-pip
```

**Arch Linux:**
```bash
sudo pacman -S python python-pip
```

**Verify installation:**
```bash
python3 --version
pip3 --version
```

---

#### 2. Install Git (Optional)

Git is needed if you want to clone the repository. Alternatively, you can download a ZIP archive.

##### Windows

1. Download from https://git-scm.com/download/win
2. Run installer
3. **Important:** Choose "Use Git from the command line and also from 3rd-party software"
4. Accept other defaults

**Verify:**
```cmd
git --version
```

##### macOS

**Option A: Xcode Command Line Tools (Recommended)**
```bash
xcode-select --install
```

**Option B: Homebrew**
```bash
brew install git
```

**Verify:**
```bash
git --version
```

##### Linux

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y git
```

**Fedora:**
```bash
sudo dnf install -y git
```

**Arch Linux:**
```bash
sudo pacman -S git
```

**Verify:**
```bash
git --version
```

---

#### 3. Get the Project

Choose one of the following methods:

##### Option A: Clone with Git (Recommended)

```bash
git clone https://github.com/skysoulkeeper/QuizBoutiqueBot.git
cd QuizBoutiqueBot
```

##### Option B: Download ZIP

1. Go to https://github.com/skysoulkeeper/QuizBoutiqueBot
2. Click green **"Code"** button
3. Click **"Download ZIP"**
4. Unzip the archive
5. Open terminal in the unzipped folder

**Important:** All following commands must be run from the project directory (the folder containing `app.py` and `requirements.txt`).

---

#### 4. Create Virtual Environment (Optional but Recommended)

A virtual environment isolates project dependencies from your system Python.

##### Windows

```cmd
py -3 -m venv .venv
.venv\Scripts\activate
```

##### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Success indicator:**
- You should see `(.venv)` at the beginning of your terminal prompt

**To deactivate later:**
```bash
deactivate
```

---

#### 5. Install Dependencies

Install all required Python packages:

```bash
pip install -r requirements.txt
```

**If `pip` is not found, try:**

```bash
# Windows
python -m pip install -r requirements.txt

# macOS/Linux
pip3 install -r requirements.txt
```

**If you get permission errors (Linux/macOS):**

**Option A:** Use virtual environment (recommended, see step 4)

**Option B:** Install for current user only
```bash
pip install --user -r requirements.txt
```

**Option C:** Use sudo (not recommended)
```bash
sudo pip3 install -r requirements.txt
```

---

#### 6. Configure the Bot

Copy the example configuration file:

```bash
cp configs/config.yml.example configs/config.yml
```

**If that doesn't work (Windows):**
```cmd
copy configs\config.yml.example configs\config.yml
```

Edit `configs/config.yml`:

```bash
# Linux/macOS
nano configs/config.yml

# Windows
notepad configs\config.yml
```

**Minimum required configuration:**

```yaml
telegram:
  token: 'YOUR_BOT_TOKEN_HERE'  # From @BotFather
  language: "en"                 # en, es, ru, or ua
```

📘 See [Bot Setup Guide](bot-setup.md) for getting your bot token

---

#### 7. Run the Bot

**With virtual environment activated:**
```bash
python app.py
```

**Without virtual environment:**
```bash
# Windows
py app.py

# macOS/Linux
python3 app.py
```

**Success indicators:**
- You should see: `"Application started"`
- No error messages
- The terminal stays running (don't close it)

**To stop the bot:**
- Press `Ctrl + C`

---

## Post-Installation

### Running on Startup

#### Linux (systemd)

Create service file:
```bash
sudo nano /etc/systemd/system/quizboutiquebot.service
```

Content:
```ini
[Unit]
Description=QuizBoutiqueBot
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/path/to/QuizBoutiqueBot
ExecStart=/path/to/QuizBoutiqueBot/.venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable quizboutiquebot
sudo systemctl start quizboutiquebot

# Check status
sudo systemctl status quizboutiquebot

# View logs
sudo journalctl -u quizboutiquebot -f
```

#### macOS (launchd)

Create plist file:
```bash
nano ~/Library/LaunchAgents/com.quizboutiquebot.plist
```

Content:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.quizboutiquebot</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/QuizBoutiqueBot/.venv/bin/python</string>
        <string>/path/to/QuizBoutiqueBot/app.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/path/to/QuizBoutiqueBot</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Load service:
```bash
launchctl load ~/Library/LaunchAgents/com.quizboutiquebot.plist
launchctl start com.quizboutiquebot
```

#### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task
3. Name: "QuizBoutiqueBot"
4. Trigger: "When the computer starts"
5. Action: "Start a program"
6. Program: `C:\Users\YourUser\QuizBoutiqueBot\.venv\Scripts\python.exe`
7. Arguments: `app.py`
8. Start in: `C:\Users\YourUser\QuizBoutiqueBot`

---

## Updating

### Docker

```bash
docker compose pull
docker compose up -d --force-recreate
```

### Manual

```bash
# Navigate to project directory
cd QuizBoutiqueBot

# Pull latest changes
git pull

# Activate virtual environment (if using)
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart the bot
python app.py
```

---

## Troubleshooting

### Python not found

**Error:** `python: command not found`

**Solution:**
- **Windows:** Try `py` instead of `python`
- **macOS/Linux:** Try `python3` instead of `python`
- Ensure Python is in PATH (reinstall and check "Add to PATH")

---

### pip not found

**Error:** `pip: command not found`

**Solution:**
```bash
# Windows
python -m pip install -r requirements.txt

# macOS/Linux
python3 -m pip install -r requirements.txt
```

---

### Permission Denied (Linux/macOS)

**Error:** `PermissionError: [Errno 13] Permission denied`

**Solution:**
1. Use virtual environment (recommended)
2. Or install with `--user` flag:
   ```bash
   pip install --user -r requirements.txt
   ```

---

### Module Not Found

**Error:** `ModuleNotFoundError: No module named 'telegram'`

**Solution:**
```bash
# Ensure virtual environment is activated
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

---

### Bot Token Invalid

**Error:** `telegram.error.InvalidToken: Invalid token`

**Solution:**
1. Check `configs/config.yml` → `telegram.token`
2. Ensure token is in quotes: `'123456789:ABC...'`
3. Get new token from @BotFather if needed

---

### Port Already in Use

**Error:** `Address already in use`

**Solution:**
- Another instance of the bot is already running
- Kill the existing process:
  ```bash
  # Linux/macOS
  pkill -f "python.*app.py"
  
  # Windows
  taskkill /F /IM python.exe
  ```

---

### Virtual Environment Issues

**Can't activate venv:**

**Windows PowerShell execution policy:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Delete and recreate:**
```bash
# Delete
rm -rf .venv  # Linux/macOS
rmdir /s .venv  # Windows

# Recreate
python3 -m venv .venv  # Linux/macOS
py -3 -m venv .venv    # Windows
```

---

## Next Steps

- 📘 [Bot Setup Guide](bot-setup.md) - Create and configure your bot
- 📘 [Configuration Guide](configuration.md) - Advanced settings
- 📘 [Database Documentation](database.md) - Database schema and management
- 📘 [Docker Deployment](docker.md) - Container deployment

---

## Need Help?

- **Issues:** https://github.com/skysoulkeeper/QuizBoutiqueBot/issues
- **Email:** skysoulkeeper@gmail.com
