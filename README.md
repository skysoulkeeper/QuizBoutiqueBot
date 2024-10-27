
# QuizBoutiqueBot
[![Buy Me a Coffee](https://img.shields.io/badge/Donate-Buy%20Me%20a%20Coffee-yellow.svg)](https://www.buymeacoffee.com/skysoulkeeper)

## Overview
QuizBoutiqueBot is a versatile Telegram bot designed for conducting quizzes with various settings and customizations. It offers a comprehensive user experience with features like timer support, question randomization, and localization in multiple languages.

- **Latest Stable Version:** [Main Branch](https://github.com/skysoulkeeper/QuizBoutiqueBot/tree/main)
- **Latest Changes:** [Develop Branch](https://github.com/skysoulkeeper/QuizBoutiqueBot/tree/develop)
- **Test Question Pools:**
  - [Boating License EN(NJ)](data/questions/Boat%20Exams/NJ%20Boat%20Exam%20Answers%20EN.json)
  - [CDL RU(FL)](data/questions/CDL/General%20Knowledge%20RU.json)

## Table of Contents
1. [Overview](#overview)
2. [Visual Demo](#visual-demo)
3. [Features](#features)
4. [Installation](#installation)
5. [Usage](#usage)
6. [How It Works](#how-it-works)
7. [Adding Your Own Quizzes](#adding-your-own-quizzes)
8. [Customization](#customization)
9. [Detailed Description of Files and Functionality](#detailed-description-of-files-and-functionality)
10. [To Do or Not To Do](#to-do-or-not-to-do)
11. [Development and Contribution](#development-and-contribution)
12. [Acknowledgments](#acknowledgments)
13. [License](#license)
14. [Contact](#contact)
15. [Support](#support)
16. [Disclaimer](#disclaimer)

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
  - Currently supports four languages: [🇺🇸 English](locales/en.yml), [🇪🇸 Spanish](locales/es.yml), [🇷🇺 Russian](locales/ru.yml), and [🇺🇦 Ukrainian](locales/ua.yml).
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

## Installation
To run this bot, you need to have Python installed on your system along with the necessary packages.

Ensure you have **Python 3.8** or higher installed on your system.

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/skysoulkeeper/QuizBoutiqueBot.git
   cd QuizBoutiqueBot
   ```

2. **Install Dependencies:**
   ```bash
    pip install -r requirements.txt
   ```

## Usage
1. **Prepare the Configuration File:**

   • Modify the [`config.yml`](configs/config.yml) file in the `configs` directory to set up your desired settings, including the Telegram bot token, proxy settings, and localization.


2. **Run the Bot:**

   • Execute the `app.py` script to start the bot:
    ```bash
        python app.py
    ```

3. **Interact with the Bot:**

    • Use Telegram to interact with the bot by sending commands like /start to begin.

## How It Works
- **Configuration Loading:**
  - On startup, the bot loads configurations from [config.yml](configs/config.yml), including settings for logging, proxies, directories, and Telegram.

- **Initialization:**
  - Initializes directories, sets up logging, proxy settings, and loads localization files.

- **Command Handlers:**
  - Handles various commands like /start, and button presses using command handlers defined in the code.

- **Quizzes:**
  - Users can select categories and quizzes, which are loaded from JSON files in the specified directories. Questions can be randomized if enabled.

- **Timer:**
  - If the timer is enabled, users must complete the quiz within the specified time limit.

- **Question Pools:**
  - The question pools are located in the data/questions directory.

## Adding Your Own Quizzes
### Creating Quiz Files
**Format:**
- Quizzes are stored in JSON format.
- Each quiz file contains a list of question objects with the following keys:
  - question: The quiz question.
  - answers: A list of possible answers.
  - correct_answer: The correct answer to the question.
  - explanation (optional): An explanation for the correct answer.

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

**Organizing Quizzes**
- Categories:
  - Organize quizzes into categories by creating subdirectories within the data/questions directory.
  - Each category should contain quiz files related to that topic.
- Naming Conventions:
  - Use clear and descriptive names for quiz files and categories.
  - Quiz file names should end with .json.

**Updating the Questions Directory**

- Adding Quizzes:
  - Place your quiz JSON files into the appropriate category directory.
  - No need to restart the bot; it dynamically reads the quiz files.
- Refreshing Quizzes:
  - Ensure that the JSON files are correctly formatted to avoid errors.

## Customization
**Emojis and Icons**
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

**Localization Files**

- Adding New Languages:
  - Localization files are stored in the locales directory as YAML files.
  - To add a new language, create a new YAML file with the language code, e.g., fr.yml for French.
- Translating Strings:
  - Provide translations for each key present in other localization files.
  - Ensure that all required keys are included to prevent missing text in the bot.

## Advanced Configuration
- Proxy Support

  - If you need to use a proxy:

      1.	Enable Proxy in [config.yml](configs/config.yml):
    ```yaml
    proxy_settings:
      proxy_enabled: False                              # Enable or disable proxy usage
      proxy_host: ""                                    # Proxy server IP address or hostname
      proxy_port: 1080                                  # Proxy server port number
      proxy_protocol: "socks"                           # Proxy protocol (e.g., "http", "https", "socks")
      proxy_username: ""                                # Username for proxy authentication
      proxy_password: ""                                # Password for proxy authentication
    ```

    2.	Supported Proxy Types:
    - HTTP, HTTPS, SOCKS4, and SOCKS5 proxies are supported.

## Detailed Description of Files and Functionality
### 1. [app.py](app.py)
- Entry point of the application.
- Initializes the bot by loading configurations, setting up logging, proxies, and starting the Telegram bot.

### 2. [utils/initializer.py](utils/initializer.py)
- Contains the `Loader` class, which initializes the application by loading configurations, setting up logging, directories, and proxy settings.

### 3. [utils/logger.py](utils/logger.py)
- Manages logging configurations using either the `loguru` or Python's built-in logging module.

### 4. [utils/proxy.py](utils/proxy.py)
- Manages proxy settings and handles setting up and testing proxy connections.

### 5. [utils/localization.py](utils/localization.py)
- Manages localization by loading translations from YAML files and providing translated strings.

### 6. [modules/telegram/handlers.py](modules/telegram/handlers.py)
- Defines the `BotHandler` class, which manages bot interactions and handles commands and button presses.

### 7. [modules/telegram/settings.py](modules/telegram/settings.py)
- Handles settings management including the number of questions, timer settings, and random question order.

### 8. [modules/telegram/menus.py](modules/telegram/menus.py)
- Defines functions to show various menus to the user, such as the main menu, settings menu, and quiz categories.

### 9. [modules/telegram/quizzes.py](modules/telegram/quizzes.py)
- Manages quiz operations including loading quiz files, sending questions, and handling quiz responses.

### 10. [configs/config.yml](configs/config.yml)
- Configuration file containing settings for the bot including environment, directories, logging, proxy, and Telegram settings.

### 11. [locales/en.yml](locales/en.yml)
- Localization file for English, containing translated strings for bot interactions.

## To Do or Not To Do
- Implement cflags functionality.
- Process lists from CSV, XLS, DOC.
- Add tests.
- Code and project structure optimization.
- Docker support.
- Implement asynchronous processing for faster results.
- Develop a WebUI.
- Database support with import and export.

However, these enhancements might be considered in the future or perhaps in another lifetime.

## Development and Contribution
### Development
- **Testing Environments:**
  - Tested on Windows and macOS with Python version 3.11.
- **Purpose:**
  - Created in free time to make studying tests more convenient.

### Contributing
We welcome contributions! Here’s how you can help:

- **Reporting Issues:**
  - Open an issue on GitHub if you find bugs or have feature requests.
- **Pull Requests:**
  - Fork the repository, make your changes, and submit a pull request.
  - Ensure your code follows the existing style and includes docstrings and comments.
- **Adding Quizzes:**
  - You can contribute by adding new quiz files in the appropriate category.

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

## License
This project is licensed under the [MIT License](LICENSE). See the `LICENSE` file for details.

## Contact
For any questions or support, please contact:
- **Email:** [skysoulkeeper@gmail.com](mailto:skysoulkeeper@gmail.com)

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

---
