# MIT License
# Copyright (c) 2024 skysoulkeeper
# See LICENSE file for more details.

"""
Module: modules/telegram/settings.py

Description:
This module manages the settings configuration for the Telegram bot, including
options for quiz question count, timer settings, randomization, and language selection.
It provides handlers for user inputs and functions to display the respective menus.
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext


async def handle_questions_count_selection(update: Update, context: CallbackContext,
                                           questions_count: str):
    """
    Handles the selection of the number of questions in a quiz.

    Args:
        update (Update): The incoming update from Telegram.
        context (CallbackContext): The context containing bot and user data.
        questions_count (str): The selected number of questions as a string.
    """
    localization = context.user_data.get('localization', context.bot_data['localization'])
    user_id = context.user_data.get('user_id')
    context.user_data['questions_count'] = int(questions_count)

    # Persist to DB
    db = context.application.bot_data.get('db')
    if user_id:
        await db.update_user_settings(user_id, questions_count=int(questions_count))

    message_text = localization.get("questions_count_set", questions_count=questions_count)
    await update.callback_query.message.edit_text(message_text,
                                                  reply_markup=show_settings_menu(
                                                      context))


async def handle_timer_selection(update: Update, context: CallbackContext,
                                 timer_status: str):
    """
    Handles enabling or disabling the quiz timer.

    Args:
        update (Update): The incoming update from Telegram.
        context (CallbackContext): The context containing bot and user data.
        timer_status (str): The selected timer status ('enable' or 'disable').
    """
    localization = context.user_data.get('localization', context.bot_data['localization'])
    is_enabled = timer_status == "enable"
    context.user_data['timer_enabled'] = is_enabled

    # Persist to DB
    db = context.application.bot_data.get('db')
    user_id = context.user_data.get('user_id')
    if user_id:
        await db.update_user_settings(user_id, timer_enabled=int(is_enabled))

    status = localization.get("enabled") if is_enabled else localization.get("disabled")
    message_text = localization.get("timer_status_set", status=status)
    await update.callback_query.message.edit_text(message_text,
                                                  reply_markup=show_settings_menu(
                                                      context))


async def handle_timer_limit_selection(update: Update, context: CallbackContext,
                                       timer_limit: str):
    """
    Handles the selection of the quiz timer limit.

    Args:
        update (Update): The incoming update from Telegram.
        context (CallbackContext): The context containing bot and user data.
        timer_limit (str): The selected timer limit in minutes as a string.
    """
    localization = context.user_data.get('localization', context.bot_data['localization'])
    context.user_data['timer_limit'] = int(timer_limit)

    # Persist to DB
    db = context.application.bot_data.get('db')
    user_id = context.user_data.get('user_id')
    if user_id:
        await db.update_user_settings(user_id, timer_limit=int(timer_limit))

    message_text = localization.get("timer_limit_set", timer_limit=timer_limit)
    await update.callback_query.message.edit_text(message_text,
                                                  reply_markup=show_settings_menu(
                                                      context))


async def handle_questions_random_selection(update: Update, context: CallbackContext,
                                            questions_random_status: str):
    """
    Handles enabling or disabling randomization of quiz questions.

    Args:
        update (Update): The incoming update from Telegram.
        context (CallbackContext): The context containing bot and user data.
        questions_random_status (str): The selected randomization status ('enable' or 'disable').
    """
    localization = context.user_data.get('localization', context.bot_data['localization'])
    is_enabled = questions_random_status == "enable"
    context.user_data['questions_random_enabled'] = is_enabled

    # Persist to DB
    db = context.application.bot_data.get('db')
    user_id = context.user_data.get('user_id')
    if user_id:
        await db.update_user_settings(user_id, questions_random_enabled=int(is_enabled))

    status = localization.get("enabled") if is_enabled else localization.get("disabled")
    message_text = localization.get("questions_random_set", status=status)
    await update.callback_query.message.edit_text(message_text,
                                                  reply_markup=show_settings_menu(
                                                      context))


async def show_questions_random_menu(update: Update, context: CallbackContext):
    """
    Displays the menu for enabling or disabling randomization of quiz questions.

    Args:
        update (Update): The incoming update from Telegram.
        context (CallbackContext): The context containing bot and user data.
    """
    localization = context.user_data.get('localization', context.bot_data['localization'])
    config = context.bot_data['config']
    emoji = config['emoji']
    keyboard = [
        [InlineKeyboardButton(f"{emoji['enabled']} {localization.get('enable_random')}",
                              callback_data="set_questions_random_enable")],
        [InlineKeyboardButton(
            f"{emoji['disabled']} {localization.get('disable_random')}",
            callback_data="set_questions_random_disable")],
        [InlineKeyboardButton(
            f"{emoji['back_button']} {localization.get('back_button')}",
            callback_data="settings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.edit_text(localization.get("random_settings"),
                                                  reply_markup=reply_markup)


def show_settings_menu(context: CallbackContext):
    """
    Constructs the settings menu keyboard.

    Args:
        context (CallbackContext): The context containing bot and user data.

    Returns:
        InlineKeyboardMarkup: The reply markup for the settings menu.
    """
    localization = context.user_data.get('localization', context.bot_data['localization'])
    config = context.bot_data['config']
    emoji = config['emoji']
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
    return InlineKeyboardMarkup(keyboard)


async def show_questions_count_menu(update: Update, context: CallbackContext) -> None:
    """
    Displays the menu for selecting the number of questions in a quiz.

    Args:
        update (Update): The incoming update from Telegram.
        context (CallbackContext): The context containing bot and user data.
    """
    localization = context.user_data.get('localization', context.bot_data['localization'])
    config = context.bot_data['config']
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
        localization.get("choose_questions_count"), reply_markup=reply_markup)


async def show_timer_menu(update: Update, context: CallbackContext):
    """
    Displays the timer settings menu to enable or disable the quiz timer.

    Args:
        update (Update): The incoming update from Telegram.
        context (CallbackContext): The context containing bot and user data.
    """
    localization = context.user_data.get('localization', context.bot_data['localization'])
    config = context.bot_data['config']
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
                                                  reply_markup=reply_markup)


async def show_timer_limit_menu(update: Update, context: CallbackContext):
    """
    Displays the menu for selecting the quiz timer limit.

    Args:
        update (Update): The incoming update from Telegram.
        context (CallbackContext): The context containing bot and user data.
    """
    localization = context.user_data.get('localization', context.bot_data['localization'])
    config = context.bot_data['config']
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
                                                  reply_markup=reply_markup)
