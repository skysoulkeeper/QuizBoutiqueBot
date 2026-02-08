# MIT License
# Copyright (c) 2024 skysoulkeeper
# See LICENSE file for more details.

"""
Module: modules/telegram/menus.py

Description:
This module provides functions to display various Telegram bot menus,
including the main menu, tests menu, settings menu, language selection menu,
and options for configuring quiz settings like question count, timer, and timer limit.
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from pathlib import Path
import os
from typing import Dict, Any
from modules.categories import CategoryHandler


def get_available_languages(config):
    """
    Retrieves the list of available language codes from the 'locales' directory.

    Args:
        config (dict): The bot's configuration dictionary.

    Returns:
        list: A list of available language codes.
    """
    languages = []
    for file in os.listdir('locales'):
        if file.endswith('.yml'):
            language_code = file.split('.')[0]
            languages.append(language_code)
    return languages


async def show_language_menu(update: Update, context: CallbackContext) -> None:
    """
    Displays the language selection menu to the user.

    Args:
        update (Update): The incoming update from Telegram.
        context (CallbackContext): The context containing bot and user data.
    """
    localization = context.user_data.get('localization', context.bot_data['localization'])
    config = context.bot_data['config']
    parse_mode = context.bot_data['parse_mode']
    languages = get_available_languages(config)

    keyboard = [
        [InlineKeyboardButton(
            f"{config['emoji']['language_flags'].get(lang, '')} {lang.upper()}",
            callback_data=f'set_language_{lang}')]
        for lang in languages
    ]
    keyboard.append([InlineKeyboardButton(
        f"{config['emoji']['back_button']} {localization.get('back_button')}",
        callback_data="settings")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    message_text = localization.get("choose_language")
    context.bot_data['logger'].info(
        f"Sending message: '{message_text}' in mode: {parse_mode}")
    await update.callback_query.message.edit_text(message_text,
                                                  reply_markup=reply_markup,
                                                  parse_mode=parse_mode)


async def show_main_menu(update: Update, context: CallbackContext) -> None:
    """
    Displays the main menu to the user.

    Args:
        update (Update): The incoming update from Telegram.
        context (CallbackContext): The context containing bot and user data.
    """
    localization = context.user_data.get('localization', context.bot_data['localization'])
    config = context.bot_data['config']
    emoji = config['emoji']
    parse_mode = context.bot_data['parse_mode']

    keyboard = [
        [InlineKeyboardButton(f"{emoji['test']} {localization.get('tests_button')}",
                              callback_data="tests")],
        [InlineKeyboardButton(
            f"{emoji['settings']} {localization.get('settings_button')}",
            callback_data="settings")],
        [InlineKeyboardButton(f"{emoji['help']} {localization.get('help_button')}",
                              callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message_text = localization.get("main_menu")
    context.bot_data['logger'].info(
        f"Sending message: '{message_text}' in mode: {parse_mode}")
    if update.message:
        await update.message.reply_text(message_text, reply_markup=reply_markup,
                                        parse_mode=parse_mode)
    elif update.callback_query:
        await update.callback_query.message.edit_text(message_text,
                                                      reply_markup=reply_markup,
                                                      parse_mode=parse_mode)
    context.bot_data['logger'].info("Displayed main menu")


async def show_tests_menu(update: Update, context: CallbackContext,
                          questions_directory: Path, logger) -> None:
    """
    Displays the tests menu with available quiz categories.

    Args:
        update (Update): The incoming update from Telegram.
        context (CallbackContext): The context containing bot and user data.
        questions_directory (Path): Path to the directory containing quiz questions.
        logger: Logger for logging information and errors.
    """
    localization = context.user_data.get('localization', context.bot_data['localization'])
    config = context.bot_data['config']
    parse_mode = context.bot_data['parse_mode']
    category_handler = CategoryHandler(questions_directory, logger)
    categories = category_handler.get_categories()

    if categories:
        keyboard = [[InlineKeyboardButton(f"{config['emoji']['test']} {category}",
                                          callback_data=f"cat_{category}")] for category
                    in categories]
        keyboard.append([InlineKeyboardButton(
            f"{config['emoji']['back_button']} {localization.get('back_button')}",
            callback_data="main_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.message.edit_text(
            localization.get("choose_category"), reply_markup=reply_markup,
            parse_mode=parse_mode)
    else:
        await update.callback_query.message.edit_text(
            localization.get("empty_question_catalog"), parse_mode=parse_mode)


async def show_settings_menu(update: Update, context: CallbackContext) -> None:
    """
    Displays the settings menu to the user.

    Args:
        update (Update): The incoming update from Telegram.
        context (CallbackContext): The context containing bot and user data.
    """
    localization = context.user_data.get('localization', context.bot_data['localization'])
    config = context.bot_data['config']
    emoji = config['emoji']
    parse_mode = context.bot_data['parse_mode']

    current_count = context.user_data.get('questions_count',
                                          config['base_settings']['questions_count'][0])
    timer_status = localization.get("enabled") if context.user_data.get('timer_enabled',
                                                                         config['base_settings']['timer_enabled']) else localization.get("disabled")
    current_timer = context.user_data.get('timer_limit',
                                          config['base_settings']['timer_limit'][0])
    questions_random_status = localization.get("enabled") if context.user_data.get(
        'questions_random_enabled',
        config['base_settings']['questions_random_enabled']) else localization.get("disabled")

    keyboard = [
        [InlineKeyboardButton(
            f"{emoji['question_number']} {localization.get('questions_count_option', current_count=current_count)}",
            callback_data='questions_count')],
        [InlineKeyboardButton(
            f"{emoji['timer']} {localization.get('timer_status_option', timer_status=timer_status)}",
            callback_data='timer_status')],
        [InlineKeyboardButton(
            f"{emoji['timer_limit']} {localization.get('timer_limit_option', current_timer=current_timer)}",
            callback_data='timer_limit')],
        [InlineKeyboardButton(
            f"{emoji['random']} {localization.get('questions_random_option', questions_random_status=questions_random_status)}",
            callback_data='questions_random')],
        [InlineKeyboardButton(
            f"{emoji['language']} {localization.get('choose_language')}",
            callback_data='choose_language')],
        [InlineKeyboardButton(
            f"{emoji['back_button']} {localization.get('back_button')}",
            callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.edit_text(localization.get("settings_menu"),
                                                  reply_markup=reply_markup,
                                                  parse_mode=parse_mode)
    context.bot_data['logger'].info("Displayed settings menu")


async def show_questions_count_menu(update: Update, context: CallbackContext) -> None:
    """
    Displays the menu for selecting the number of questions in a quiz.

    Args:
        update (Update): The incoming update from Telegram.
        context (CallbackContext): The context containing bot and user data.
    """
    localization = context.user_data.get('localization', context.bot_data['localization'])
    config = context.bot_data['config']
    parse_mode = context.bot_data['parse_mode']
    questions_counts = config['base_settings']['questions_count']
    emoji = config['emoji']
    keyboard = [[InlineKeyboardButton(
        f"{emoji['question_number']} {localization.get('questions_count_option', current_count=count)}",
        callback_data=f"set_questions_count_{count}")] for count in questions_counts]
    keyboard.append([InlineKeyboardButton(
        f"{emoji['back_button']} {localization.get('back_button')}",
        callback_data="settings")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.edit_text(
        localization.get("choose_questions_count"), reply_markup=reply_markup,
        parse_mode=parse_mode)
    context.bot_data['logger'].info("Displayed questions count menu")


async def show_timer_menu(update: Update, context: CallbackContext) -> None:
    """
    Displays the timer settings menu to enable or disable the quiz timer.

    Args:
        update (Update): The incoming update from Telegram.
        context (CallbackContext): The context containing bot and user data.
    """
    localization = context.user_data.get('localization', context.bot_data['localization'])
    config = context.bot_data['config']
    parse_mode = context.bot_data['parse_mode']
    emoji = config['emoji']
    keyboard = [
        [InlineKeyboardButton(f"{emoji['enabled']} {localization.get('enable_timer')}",
                              callback_data="set_timer_enable")],
        [InlineKeyboardButton(f"{emoji['disabled']} {localization.get('disable_timer')}",
                              callback_data="set_timer_disable")],
        [InlineKeyboardButton(
            f"{emoji['back_button']} {localization.get('back_button')}",
            callback_data="settings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.edit_text(localization.get("timer_settings"),
                                                  reply_markup=reply_markup,
                                                  parse_mode=parse_mode)
    context.bot_data['logger'].info("Displayed timer menu")


async def show_timer_limit_menu(update: Update, context: CallbackContext) -> None:
    """
    Displays the menu for selecting the quiz timer limit.

    Args:
        update (Update): The incoming update from Telegram.
        context (CallbackContext): The context containing bot and user data.
    """
    localization = context.user_data.get('localization', context.bot_data['localization'])
    config = context.bot_data['config']
    parse_mode = context.bot_data['parse_mode']
    timer_limits = config['base_settings']['timer_limit']
    emoji = config['emoji']
    keyboard = [[InlineKeyboardButton(
        f"{emoji['timer_limit']} {localization.get('timer_limit_option_minutes', limit=limit)}",
        callback_data=f"set_timer_limit_{limit}")] for limit in timer_limits]
    keyboard.append([InlineKeyboardButton(
        f"{emoji['back_button']} {localization.get('back_button')}",
        callback_data="settings")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.edit_text(localization.get("choose_timer_limit"),
                                                  reply_markup=reply_markup,
                                                  parse_mode=parse_mode)
    context.bot_data['logger'].info("Displayed timer limit menu")
