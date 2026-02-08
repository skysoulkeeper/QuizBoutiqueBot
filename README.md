
# QuizBoutiqueBot
[![Buy Me a Coffee](https://img.shields.io/badge/Donate-Buy%20Me%20a%20Coffee-yellow.svg)](https://www.buymeacoffee.com/skysoulkeeper)
[![Docker Image](https://img.shields.io/badge/Docker-ghcr.io-blue?logo=docker)](https://github.com/skysoulkeeper/QuizBoutiqueBot/pkgs/container/quizboutiquebot)

## Overview
QuizBoutiqueBot is a versatile Telegram bot designed for conducting quizzes with various settings and customizations. It offers a comprehensive user experience with features like timer support, question randomization, and localization in multiple languages.

- **Latest Stable Version:** [Main Branch](https://github.com/skysoulkeeper/QuizBoutiqueBot/tree/main)
- **Latest Changes:** [Develop Branch](https://github.com/skysoulkeeper/QuizBoutiqueBot/tree/develop)
- **Docker Images:** [GitHub Container Registry](https://github.com/skysoulkeeper/QuizBoutiqueBot/pkgs/container/quizboutiquebot)
- **Test Question Pools:**
  - [Boating License EN (NJ)](data/questions/Boat%20Exams/NJ%20Boat%20Exam%20Answers%20EN.json)
  - [Boating License RU+EN (NJ)](data/questions/Boat%20Exams/NJ%20Boat%20Exam%20Answers%20RU+EN.json)
  - [BSIS EN (CA Powers to Arrest)](data/questions/BSIS/CA%20Powers%20to%20Arrest%20EN.json)
  - [CDL RU (General Knowledge)](data/questions/CDL/General%20Knowledge%20RU.json)


## Table of Contents
1. [Overview](#overview)
2. [Visual Demo](#visual-demo)
3. [Features](#features)
4. [Installation](#installation)
   - [Docker Deployment (Recommended)](#docker-deployment-recommended)
   - [Manual Installation](#manual-installation)
5. [Creating Your Telegram Bot and Adding to a Group](#creating-your-telegram-bot-and-adding-to-a-group)
6. [Usage](#usage)
7. [How It Works](#how-it-works)
8. [Adding Your Own Quizzes](#adding-your-own-quizzes)
9. [Customization](#customization)
10. [Advanced Configuration](#advanced-configuration)
11. [Detailed Description of Files and Functionality](#detailed-description-of-files-and-functionality)
12. [To Do or Not To Do](#to-do-or-not-to-do)
13. [Development and Contribution](#development-and-contribution)
14. [Acknowledgments](#acknowledgments)
15. [License](#license)
16. [Contact](#contact)
17. [Support](#support)
18. [Disclaimer](#disclaimer)

## Visual Demo
| ![img1](img/main_menu.png) | ![img2](img/settings.png) | ![img3](img/question_pool.png) |
|------------------------|------------------------|------------------------|
| ![img4](img/language.png) | ![img5](img/tests.png) | ![img6](img/test_exmp.png) |

## Features
- **Quiz Timer Functionality:**
  - Enable or disable a timer for quizzes.
  - Customizable timer limits (in minutes).
  - Automatic submission of the quiz when time runs out, displaying results.

- **Randomization of Questions:**
  - Option to randomize the order of questions.
  - Provides a unique experience each time the quiz is taken.

- **Question Categories and Management:**
  - Support for multiple quiz categories for better organization.
  - Easy navigation through categories to select specific quizzes.

- **Detailed Results and Explanations:**
  - Users receive detailed results showing correct and incorrect answers.
  - Explanations for answers are provided when available to enhance learning.

- **User Settings and Preferences:**
  - Customize settings such as:
    - Number of questions per quiz.
    - Timer status (enabled/disabled).
    - Timer limits.
    - Randomization of questions.
  - Settings are saved per user, providing a personalized experience.

- **Localization Support:**
  - Multi-language interface with easy language switching.
  - Currently supports languages: [🇺🇸 English](locales/en.yml), [🇪🇸 Spanish](locales/es.yml), [🇷🇺 Russian](locales/ru.yml), and [🇺🇦 Ukrainian](locales/ua.yml).
  - Easy to add additional languages via localization files.

- **Persistent Data Handling:**
  - Remembers user settings and the last quiz taken.
  - Users can restart the last quiz with a single command.

- **Interactive Menus with Inline Keyboards:**
  - Intuitive navigation using inline keyboard buttons.
  - Users can easily navigate menus and select options without typing commands.

- **Error Handling and User Feedback:**
  - Informative error messages guide users in case of unexpected inputs.
  - Robust handling of exceptions ensures a smooth user experience.

- **Proxy Support:**
  - Configure and use proxy settings for secure and anonymous connections.

- **Docker Support:**
  - Pre-built multi-platform images for easy deployment.
  - Supports Intel/AMD (amd64) and ARM (arm64) architectures.

## Installation

Choose your deployment method based on your needs:

### Docker Deployment (Recommended)

🐳 **Quick start with pre-built images**

**Supported Platforms:**
- Intel/AMD (amd64) - Standard PCs, servers, NAS devices (Synology, QNAP, TerraMaster)
- ARM (arm64) - Apple Silicon (M1/M2/M3), Raspberry Pi 4/5

**Quick Start:**
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

📘 **For detailed Docker documentation, see [Docker Deployment Guide](docker/DOCKER.md)**

---

### Manual Installation

💻 **Run locally without Docker** - Best for development

Get your computer ready to run the bot. Simple step-by-step instructions for Windows, macOS, and Linux.

#### 1) Install Python (version 3.8 or later)
- **Windows:**
  - Go to https://www.python.org/downloads/windows/ and download the latest Python 3.x.
  - In the installer, check "Add Python to PATH", then click Install Now.
  - How to open a terminal: press Win and type "Command Prompt" (or "PowerShell"), then open it.
  - Verify installation: run `python --version` or `py --version`.

- **macOS:**
  - Go to https://www.python.org/downloads/macos/ and download the pkg installer for Python 3.x. Install it.
  - Alternative for advanced users: Homebrew - `brew install python`.
  - How to open a terminal: open Spotlight (Cmd+Space), type "Terminal", then open the Terminal app.
  - Verify: `python3 --version`.

- **Linux:**
  - How to open a terminal: usually Ctrl+Alt+T or find "Terminal" in the menu.
  - Install Python and pip (choose your distro):
    - Ubuntu/Debian: `sudo apt update && sudo apt install -y python3 python3-pip`
    - Fedora: `sudo dnf install -y python3 python3-pip`
    - Arch: `sudo pacman -S python python-pip`
  - Verify: `python3 --version`, `pip3 --version`.

#### 2) Get the project

Install Git (only if you choose Option A):
- **Windows:** download and install Git for Windows from https://git-scm.com/download/win. During setup, choose "Use Git from the command line and also from 3rd-party software". Open Git Bash or Command Prompt.
- **macOS:** install Xcode Command Line Tools: `xcode-select --install`, or use Homebrew: `brew install git`.
- **Linux:**
  - Ubuntu/Debian: `sudo apt update && sudo apt install -y git`
  - Fedora: `sudo dnf install -y git`
  - Arch: `sudo pacman -S git`

Verify: `git --version` should print a version number.

- **Option A (git):**
```bash
git clone https://github.com/skysoulkeeper/QuizBoutiqueBot.git
cd QuizBoutiqueBot
```
- **Option B (ZIP):** click "Code" -> "Download ZIP" on the repository page, unzip it and open the unzipped folder in your terminal.
- **Important:** from now on, run all commands in the project folder that contains `app.py` and `requirements.txt`.

#### 3) (Optional but recommended) Create a virtual environment
- **Windows:**
  ```bash
  py -3 -m venv .venv
  .venv\Scripts\activate
  ```
- **macOS/Linux:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```
If you see `(.venv)` at the start of your terminal line, it's active.

#### 4) Install dependencies
```bash
pip install -r requirements.txt
# if pip is not found:
python -m pip install -r requirements.txt
# or on Linux/macOS:
pip3 install -r requirements.txt
```
If you see permission errors - add `--user` (Linux/macOS) or make sure the virtual environment is activated.

## Creating Your Telegram Bot and Adding to a Group
Step-by-step guide to create your Telegram bot and use it in DMs or groups.

#### 1) Create a bot with BotFather
- Open Telegram and find the official @BotFather.
- Send `/newbot` and follow the prompts:
  - Choose a display name.
  - Choose a unique username ending in `bot` (e.g., `MyQuizBoutiqueBot`).
- BotFather will give you a token like `123456789:ABC...`. Save it.

**For Docker:** Add token to `.env` file as `TELEGRAM_BOT_TOKEN=your_token`
**For Manual:** Add token to `configs/config.yml` as `telegram.token: 'your_token'`

#### 2) (Optional) Turn off "Group Privacy" for group usage
- In @BotFather open `/mybots` -> choose your bot -> Bot Settings -> Group Privacy -> Turn Off.
- Why: with privacy off, the bot can see commands and button presses in groups, which is useful for quizzes.

#### 3) Add the bot to your group
- Open your group -> Add member -> search your bot by username -> add.
- Grant admin rights only if you know you need them. The quiz UI works with inline buttons and /start.

#### 4) Find your group chat_id (optional)
- If you want to save the group chat_id in config, the easiest way is to add @getidsbot or @RawDataBot to the group. They will show the chat ID.
- **For Docker:** Optionally set `TELEGRAM_CHAT_ID` in `.env`.
- **For Manual:** Optionally set `telegram.chat_id` in `configs/config.yml`.

## Usage

### Docker Usage

```bash
# Start the bot
docker compose up -d

# View logs
docker compose logs -f

# Stop the bot
docker compose down

# Update to latest version
docker compose pull
docker compose up -d --force-recreate
```

### Manual Usage

#### 1) Configure the bot (configs/config.yml)
- Open `configs/config.yml` with any text editor.
- Find the `telegram` section and set:
  - `token`: paste your bot token from BotFather.
  - `language`: interface language - `en`, `es`, `ru`, `ua`.
  - `proxy_settings`: if Telegram is restricted in your region, enable and configure a proxy.

#### 2) Start the bot
- **Windows:**
  ```bash
  py app.py
  # if that doesn't work, try:
  python app.py
  ```
- **macOS/Linux:**
  ```bash
  python3 app.py
  # with an active virtual environment this also works:
  python app.py
  ```

#### 3) Open Telegram and try it
- Find your bot by its username and press "Start" (/start).
- Main menu:
  - "Tests" - choose a category and a quiz.
  - "Settings" - adjust quiz settings and language.
  - "Help" - quick help.

#### 4) Stop the bot
- Go back to the terminal and press Ctrl+C.

## How It Works
- **Configuration Loading:**
  - Docker: Merges environment variables with [config.yml](configs/config.yml) via [entrypoint.py](docker/entrypoint.py)
  - Manual: Loads configurations from [config.yml](configs/config.yml)

- **Initialization:**
  - Initializes directories, sets up logging, proxy settings, and loads localization files.

- **Command Handlers:**
  - Handles various commands like /start, and button presses using command handlers.

- **Quizzes:**
  - Users can select categories and quizzes loaded from JSON files. Questions can be randomized if enabled.

- **Timer:**
  - If enabled, users must complete the quiz within the specified time limit.

- **Question Pools:**
  - Question pools are located in the `data/questions` directory.

## Adding Your Own Quizzes
The bot reads files from `data/questions` and automatically shows them under "Tests".

### Structure and format
- Each quiz is a JSON file (UTF-8) placed inside a category subfolder, e.g., `data/questions/Boat Exams/NJ Boat Exam Answers EN.json`.
- Structure per quiz:
  - Array of objects, where each object represents one question.
  - Required fields per question:
    - `question` - question text (string).
    - `answers` - list of answer options (strings). Recommended to start each option with a short key and a separator, e.g., `A. ...`, `B. ...` or `A: ...`, `B: ...`. Numbers like `1. ...` also work.
    - `correct_answer` - the exact string from `answers` that is correct (the key and text must match exactly).
    - `explanation` (optional) - an explanation that is shown after answering.
- Telegram button labels have a length limit. In code `MAX_BUTTON_LENGTH` is 64. Keep a short key at the start (`A.`, `B.` etc.) and the long text after it.

**Example:**
```json
[
  {
    "question": "What is the capital of France?",
    "answers": ["A. Berlin", "B. Paris", "C. Rome", "D. Madrid"],
    "correct_answer": "B. Paris",
    "explanation": "Paris is the capital and most populous city of France."
  },
  {
    "question": "Which planet is known as the Red Planet?",
    "answers": ["A. Earth", "B. Mars", "C. Jupiter", "D. Venus"],
    "correct_answer": "B. Mars",
    "explanation": "Mars is often called the 'Red Planet' because of its reddish appearance."
  }
]
```

### Tips
- Categories are subfolders in `data/questions` (e.g., `CDL`, `Boat Exams`, `BSIS`). Folder names appear in the menu.
- Use clear filenames ending with `.json`.
- You can mix languages in one file (see `NJ Boat Exam Answers RU+EN.json`). The structure must remain valid.
- Validate your JSON in any online validator if the bot reports a format error.

### Add/update quizzes
- Copy your JSON file into the appropriate subfolder inside `data/questions`.
- **Docker:** No restart needed for question files mounted as volumes.
- **Manual:** No restart needed - the list is read dynamically.

## Customization

### Emojis and Icons
- The bot uses emojis and icons for a better user experience.
- Emojis can be customized in the [config.yml](configs/config.yml) file under the emoji section.

**Example:**
```yaml
emoji:
  test: "📝"
  timer: "⏱️"
  enabled: "✅"
  disabled: "❌"
  back_button: "🔙"
  settings: "⚙️"
  help: "❓"
  language: "🌐"
```

### Localization Files

- **Adding New Languages:**
  - Localization files are stored in the `locales` directory as YAML files.
  - To add a new language, create a new YAML file with the language code, e.g., `fr.yml` for French.

- **Translating Strings:**
  - Provide translations for each key present in other localization files.
  - Ensure that all required keys are included to prevent missing text in the bot.

## Advanced Configuration

### Configuration Methods

**Docker (Recommended):**
- All settings configured via environment variables in `.env` file
- See [.env.example](.env.example) for all available options
- See [Docker Deployment Guide](docker/DOCKER.md) for details

**Manual:**
- All settings in [configs/config.yml](configs/config.yml)
- Direct YAML editing for full control

### Proxy Support

**Docker:**
```bash
# In .env file
QBB_PROXY_ENABLED=true
QBB_PROXY_HOST=proxy.example.com
QBB_PROXY_PORT=1080
QBB_PROXY_PROTOCOL=socks
QBB_PROXY_USERNAME=username
QBB_PROXY_PASSWORD=password
```

**Manual:**
```yaml
# In configs/config.yml
proxy_settings:
  proxy_enabled: true
  proxy_host: "proxy.example.com"
  proxy_port: 1080
  proxy_protocol: "socks"  # http, https, or socks
  proxy_username: "username"
  proxy_password: "password"
```

Supported proxy types: HTTP, HTTPS, SOCKS4, and SOCKS5.

## Detailed Description of Files and Functionality

### Core Files
- **[app.py](app.py)** - Entry point of the application
- **[docker/entrypoint.py](docker/entrypoint.py)** - Docker container entrypoint, merges ENV with config
- **[utils/initializer.py](utils/initializer.py)** - Application initialization
- **[utils/logger.py](utils/logger.py)** - Logging configuration (loguru/default)
- **[utils/proxy.py](utils/proxy.py)** - Proxy settings management
- **[utils/localization.py](utils/localization.py)** - Multi-language support
- **[modules/telegram/handlers.py](modules/telegram/handlers.py)** - Bot command handlers
- **[modules/telegram/settings.py](modules/telegram/settings.py)** - Settings management
- **[modules/telegram/menus.py](modules/telegram/menus.py)** - Menu displays
- **[modules/telegram/quizzes.py](modules/telegram/quizzes.py)** - Quiz operations

### Configuration Files
- **[configs/config.yml](configs/config.yml)** - Main configuration file
- **[.env.example](.env.example)** - Environment variables template (for Docker)
- **[locales/*.yml](locales/)** - Language files (en, es, ru, ua)

### Docker Files
- **[Dockerfile](Dockerfile)** - Multi-stage Docker build configuration
- **[docker-compose.yml](docker-compose.yml)** - Production deployment
- **[docker-compose.dev.yml](docker-compose.dev.yml)** - Development deployment
- **[.dockerignore](.dockerignore)** - Docker build exclusions
- **[Makefile](Makefile)** - Build automation for multi-platform images

## Building and Publishing (For Contributors)

For contributors who want to build and publish Docker images:

### Prerequisites
- Docker with buildx support
- GitHub Personal Access Token with `write:packages` scope

### Build Multi-Platform Images

```bash
# First time setup
make setup-builder

# Login to GitHub Container Registry
make login

# Build and push to GHCR
make build-push
```

**Available Make targets:**
- `make help` - Show all available commands
- `make setup-builder` - Setup Docker buildx (run once)
- `make login` - Login to GHCR
- `make build-push` - Build and push production image (`:latest`)
- `make build-push-dev` - Build and push development image (`:dev`)
- `make clean` - Remove local images

## To Do or Not To Do
- Implement cflags functionality.
- Process lists from CSV, XLS, DOC.
- Add tests.
- Code and project structure optimization.
- Implement asynchronous processing for faster results.
- Develop a WebUI.
- Database support with import and export.

However, these enhancements might be considered in the future or perhaps in another lifetime.

## Development and Contribution

### Development
- **Testing Environments:**
  - Tested on Windows, macOS, and Linux with Python version 3.11+
  - Docker images tested on Intel/AMD and ARM architectures
- **Purpose:**
  - Created in free time to make studying tests more convenient.

### Contributing
We welcome contributions! Here's how you can help:

- **Reporting Issues:**
  - Open an issue on GitHub if you find bugs or have feature requests.

- **Pull Requests:**
  - Fork the repository, make your changes, and submit a pull request.
  - Ensure your code follows the existing style and includes docstrings and comments.

- **Adding Quizzes:**
  - You can contribute by adding new quiz files in the appropriate category.

- **Translations:**
  - Add new language files in the `locales` directory.

## Acknowledgments
- **Libraries Used:**
  - **python-telegram-bot** for interacting with the Telegram Bot API.
  - **requests** for making HTTP requests.
  - **loguru** for advanced logging capabilities.
  - **PyYAML** for parsing YAML files (used in configuration and localization).
  - **watchdog** for monitoring file system events.

- **Inspiration:**
  - Inspired by the need for an interactive and customizable quiz platform on Telegram.

- **Special Thanks:**
  - Thanks to the [python-telegram-bot](https://python-telegram-bot.org/) community for their support.
  - Thanks to all contributors and users who provide feedback.

## License
This project is licensed under the [MIT License](LICENSE). See the `LICENSE` file for details.

## Contact
For any questions or support, please contact:
- **Email:** [skysoulkeeper@gmail.com](mailto:skysoulkeeper@gmail.com)
- **GitHub:** [Issues](https://github.com/skysoulkeeper/QuizBoutiqueBot/issues)

## Support
If you like this project and want to support its development, consider buying me a coffee:

[![Buy Me a Coffee](https://img.shields.io/badge/Donate-Buy%20Me%20a%20Coffee-yellow.svg)](https://www.buymeacoffee.com/skysoulkeeper)

You can also support via:
- **PayPal 💸:** [Donate via PayPal](https://www.paypal.com/donate/?business=RC5EDUDFBPNCJ&no_recurring=0&currency_code=USD)
- **USDT (ERC20) 🪙:** `0xE157B1Ae65ee66B0c98D87829dC03f84DcfDed2d`
- **USDT (BEP20) 🪙:** `0xE157B1Ae65ee66B0c98D87829dC03f84DcfDed2d`
- **USDT (TRC20) 🪙:** `TAa9C6i8XYapJ1YsUZDxM5kyYiQ8YbL1TU`
- **BTC ₿:** `bc1qmkxklzc66tj0s3qzyww2jl9h5ul3a5mttlvylt`
- **ETH Ξ:** `0xE157B1Ae65ee66B0c98D87829dC03f84DcfDed2d`
- **DOGE 🐕:** `D5bsqM2dCSJpvS5XWy8RLHCmymwBYFZcan`

## Disclaimer
This bot is provided as-is. Feel free to download, modify, and use it as you see fit.
