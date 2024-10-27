# MIT License
# Copyright (c) 2024 skysoulkeeper
# See LICENSE file for more details.

"""
Module: modules/telegram/handlers.py

Description:
This module provides the BotHandler class for managing interactions with the
Telegram bot. It includes methods for handling commands, callback queries,
language settings, and quiz management. It also manages user actions and
context initialization.
"""

from telegram import Update
from telegram.ext import CallbackContext
from pathlib import Path
from modules.categories import CategoryHandler
from .menus import (
    show_main_menu, show_tests_menu, show_settings_menu,
    show_questions_count_menu, show_timer_menu,
    show_timer_limit_menu, show_language_menu
)
from .quizzes import (
    get_questions_directory, handle_category_selection,
    handle_quiz_selection, send_question, handle_quiz_response, stop_timer
)
from .settings import (
    handle_questions_count_selection, handle_timer_selection,
    handle_timer_limit_selection, handle_questions_random_selection, show_questions_random_menu
)
from utils.localization import Localization
from typing import Dict, Any, Callable, Awaitable


class BotHandler:
    """
    Class to handle Telegram bot interactions.
    """
    def __init__(self, config: Dict[str, Any], logger, localization: Localization, questions_directory: Path):
        """
        Initializes the BotHandler with configuration, logger, localization, and questions directory.

        Args:
            config (Dict[str, Any]): Bot configuration.
            logger: Logger instance for logging information and errors.
            localization (Localization): Localization instance for managing translations.
            questions_directory (Path): Path to the questions directory.
        """
        self.config = config
        self.logger = logger
        self.localization = localization
        self.questions_directory = questions_directory
        self.category_handler = CategoryHandler(self.questions_directory, logger)
        self.parse_mode = config['telegram'].get('parse_mode', 'HTML')  # Default to HTML if not specified

    async def start(self, update: Update, context: CallbackContext) -> None:
        """
        Handles the /start command.

        Args:
            update (Update): The update object from Telegram.
            context (CallbackContext): The context object from Telegram.
        """
        try:
            self.initialize_context(context)
            await show_main_menu(update, context)
            self.log_user_action(update.effective_user.id, "started bot")
        except KeyError as e:
            self.logger.error(f"KeyError in start handler: {e}", exc_info=True)
        except Exception as e:
            self.logger.error(f"Unexpected error in start handler: {e}", exc_info=True)

    def initialize_context(self, context: CallbackContext) -> None:
        """
        Initializes the context with default values.

        Args:
            context (CallbackContext): The context object from Telegram.
        """
        context.bot_data.update({
            'config': self.config,
            'questions_count': self.config['base_settings']['questions_count'][0],
            'timer_enabled': self.config['base_settings']['timer_enabled'],
            'timer_limit': self.config['base_settings']['timer_limit'][0],
            'questions_random_enabled': self.config['base_settings']['questions_random_enabled'],
            'localization': self.localization,
            'questions_directory': self.questions_directory,
            'logger': self.logger,
            'parse_mode': self.parse_mode
        })

    async def button(self, update: Update, context: CallbackContext) -> None:
        """
        Handles callback queries (button presses) from the user.

        Args:
            update (Update): The update object from Telegram.
            context (CallbackContext): The context object from Telegram.
        """
        query = update.callback_query
        await query.answer()

        handlers: Dict[str, Callable[[Update, CallbackContext], Awaitable[None]]] = {
            "tests": self.show_tests_menu,
            "settings": show_settings_menu,
            "help": self.show_help_section,
            "questions_count": show_questions_count_menu,
            "timer_status": show_timer_menu,
            "timer_limit": show_timer_limit_menu,
            "choose_language": show_language_menu,
            "restart": self.restart_last_quiz,
            "list_tests": self.list_tests,
            "next_question": lambda u, c: send_question(u, c, self.config),
            "main_menu": self.go_to_main_menu,
            "questions_random": show_questions_random_menu
        }

        try:
            handler = handlers.get(query.data)
            if handler:
                await handler(update, context)
            elif query.data.startswith("set_questions_count_"):
                await handle_questions_count_selection(update, context, self.extract_option_key(query.data))
            elif query.data.startswith("set_timer_"):
                await self.handle_timer_selection(update, context, query.data)
            elif query.data.startswith('cat_'):
                await handle_category_selection(update, context, query, self.questions_directory, self.logger)
            elif query.data.startswith('quiz_'):
                await handle_quiz_selection(update, context, query, self.questions_directory, self.logger)
            elif query.data.startswith("set_language_"):
                await self.set_language(update, context, self.extract_option_key(query.data))
            elif query.data.startswith("set_questions_random_"):
                await handle_questions_random_selection(update, context, self.extract_option_key(query.data))
            else:
                await handle_quiz_response(update, context, query.data)
        except KeyError as e:
            self.logger.error(f"KeyError in button handler: {e}", exc_info=True)
        except Exception as e:
            self.logger.error(f"Unexpected error in button handler: {e}", exc_info=True)

    async def show_help_section(self, update: Update, context: CallbackContext) -> None:
        """
        Shows the help section to the user.

        Args:
            update (Update): The update object from Telegram.
            context (CallbackContext): The context object from Telegram.
        """
        localization = context.bot_data['localization']
        parse_mode = context.bot_data['parse_mode']
        if update.callback_query and update.callback_query.message:
            await update.callback_query.message.edit_text(localization.get("help_section"), parse_mode=parse_mode)

    async def list_tests(self, update: Update, context: CallbackContext) -> None:
        """
        Stops the timer and displays the list of available tests to the user.

        Args:
            update (Update): The update object from Telegram.
            context (CallbackContext): The context object from Telegram.
        """
        await stop_timer(context)
        await show_tests_menu(update, context, self.questions_directory, self.logger)

    async def show_tests_menu(self, update: Update, context: CallbackContext) -> None:
        """
        Displays the tests menu to the user.

        Args:
            update (Update): The update object from Telegram.
            context (CallbackContext): The context object from Telegram.
        """
        await show_tests_menu(update, context, self.questions_directory, self.logger)

    async def go_to_main_menu(self, update: Update, context: CallbackContext) -> None:
        """
        Stops the timer and returns the user to the main menu.

        Args:
            update (Update): The update object from Telegram.
            context (CallbackContext): The context object from Telegram.
        """
        await stop_timer(context)
        await show_main_menu(update, context)

    async def handle_timer_selection(self, update: Update, context: CallbackContext, data: str) -> None:
        """
        Handles the selection of timer settings by the user.

        Args:
            update (Update): The update object from Telegram.
            context (CallbackContext): The context object from Telegram.
            data (str): The callback data containing the timer setting selected.
        """
        if "limit" in data:
            await handle_timer_limit_selection(update, context, self.extract_option_key(data))
        else:
            await handle_timer_selection(update, context, self.extract_option_key(data))

    async def restart_last_quiz(self, update: Update, context: CallbackContext) -> None:
        """
        Restarts the last quiz that the user took.

        Args:
            update (Update): The update object from Telegram.
            context (CallbackContext): The context object from Telegram.
        """
        last_quiz = context.user_data.get('last_quiz')
        last_category = context.user_data.get('last_category')
        localization = context.bot_data['localization']
        parse_mode = context.bot_data['parse_mode']
        if last_quiz and last_category and update.callback_query:
            query_data = f"quiz_{last_quiz}_{last_category}"
            fake_query = type('obj', (object,), {'data': query_data, 'from_user': update.callback_query.from_user})
            await handle_quiz_selection(update, context, fake_query, self.questions_directory, self.logger)
        elif update.callback_query and update.callback_query.message:
            await update.callback_query.message.edit_text(localization.get("restart_quiz_failed"), parse_mode=parse_mode)

    async def set_language(self, update: Update, context: CallbackContext, language: str) -> None:
        """
        Sets the language for the bot's messages.

        Args:
            update (Update): The update object from Telegram.
            context (CallbackContext): The context object from Telegram.
            language (str): The language code selected by the user.
        """
        self.localization = Localization(language)
        context.bot_data['localization'] = self.localization
        parse_mode = context.bot_data['parse_mode']
        if update.callback_query and update.callback_query.message:
            await update.callback_query.message.edit_text(self.localization.get("language_changed"), parse_mode=parse_mode)
        await show_main_menu(update, context)

    @staticmethod
    def extract_option_key(data: str) -> str:
        """
        Extracts the option key from the callback data.

        Args:
            data (str): The callback data string.

        Returns:
            str: The extracted option key.
        """
        return data.split('_')[-1]

    def log_user_action(self, user_id: int, action: str) -> None:
        """
        Logs an action taken by the user.

        Args:
            user_id (int): The Telegram user ID.
            action (str): The action description.
        """
        self.logger.info(f"User {user_id} {action}")
