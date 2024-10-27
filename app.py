# MIT License
# Copyright (c) 2024 skysoulkeeper
# See LICENSE file for more details.

"""
Module: app.py

Description:
This module serves as the entry point for the QuizBoutiqueBot application.
"""

from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from utils.initializer import Loader
from modules.telegram.handlers import BotHandler
import sys


def main() -> None:
    """
    Main function to initialize and start the Telegram bot application.
    """
    logger = None  # Initialize logger to ensure it's always defined
    try:
        # Initialize the loader to set up configuration, logging, proxy, and localization
        loader = Loader()
        config, logger, proxy_handler, localization, telegram_token, telegram_chat_id, questions_directory, parse_mode = loader.initialize()

        # Create an instance of the BotHandler with the necessary components
        bot_handler = BotHandler(config, logger, localization, questions_directory)

        # Initialize the Telegram application with the bot token
        application = Application.builder().token(telegram_token).build()

        # Add command and callback handlers
        application.add_handler(CommandHandler("start", bot_handler.start))
        application.add_handler(CallbackQueryHandler(bot_handler.button))

        # Pass configuration, logger, and localization to bot_data for global access
        application.bot_data['config'] = config
        application.bot_data['logger'] = logger
        application.bot_data['localization'] = localization
        application.bot_data['parse_mode'] = parse_mode

        logger.info("Application started")
        application.run_polling()
        logger.info("Polling started")

    except Exception as e:
        # Log any exception that occurs during the initialization and starting process
        if logger:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            sys.stderr.write(f"An error occurred: {e}\n")


if __name__ == "__main__":
    main()
