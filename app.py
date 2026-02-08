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
from utils.database import BotDatabase
import sys
import asyncio


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

        # Enforce database enabled and prepare defaults
        db_cfg = config.get('database', {})
        if not db_cfg.get('db_enabled', True):
            logger.error("Database is disabled in configuration. This application requires DB enabled.")
            sys.exit(1)

        default_settings = {
            'questions_count': config['base_settings']['questions_count'][0],
            'timer_enabled': config['base_settings']['timer_enabled'],
            'timer_limit': config['base_settings']['timer_limit'][0],
            'questions_random_enabled': config['base_settings']['questions_random_enabled'],
        }
        db_path = db_cfg.get('db_source', 'data/db/qbb.db')
        success_rate = config['base_settings']['success_rate']
        bot_db = BotDatabase(db_path=db_path, success_rate=success_rate, default_settings=default_settings)

        async def _post_init(app: Application) -> None:
            # Fail-fast on DB init errors
            await bot_db.init()
            app.bot_data['db'] = bot_db

        async def _post_shutdown(app: Application) -> None:
            await bot_db.close()

        # Initialize the Telegram application with the bot token
        application = (
            Application
            .builder()
            .token(telegram_token)
            .post_init(_post_init)
            .post_shutdown(_post_shutdown)
            .build()
        )

        # Add command and callback handlers
        application.add_handler(CommandHandler("start", bot_handler.start))
        application.add_handler(CallbackQueryHandler(bot_handler.button))

        # Pass configuration, logger, and default localization to bot_data for global access
        application.bot_data['config'] = config
        application.bot_data['logger'] = logger
        application.bot_data['localization'] = localization  # default fallback
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
