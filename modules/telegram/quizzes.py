# MIT License
# Copyright (c) 2024 skysoulkeeper
# See LICENSE file for more details.

"""
Module: modules/telegram/quizzes.py

Description:
This module handles quiz-related operations for the Telegram bot, including
loading questions, managing user responses, handling quiz timing, and sending
results. It provides functions for question selection, randomization, and
timer-based quiz control.
"""

import os
import json
import random
import asyncio
from typing import Optional, Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

MAX_BUTTON_LENGTH = 64


def get_questions_directory(config: dict) -> Optional[str]:
    """
    Retrieves the directory containing the quiz questions from the configuration.
    Args:
        config (dict): The configuration dictionary.
    Returns:
        Optional[str]: The path to the questions directory or None if not found.
    """
    return next((d for d in config['directories_to_create'] if 'questions' in d), None)


def get_quiz_files(category_directory, logger):
    """
    Retrieves quiz files from a given category directory.
    Args:
        category_directory (str): The path to the category directory.
        logger (Logger): Logger for logging errors and info messages.
    Returns:
        list: A list of tuples containing the quiz file name and question count.
    """
    if not os.path.exists(category_directory):
        logger.error(f"Category directory {category_directory} does not exist.")
        return []

    logger.info(f"Checking files in category directory: {category_directory}")
    quiz_files = []
    for f in os.listdir(category_directory):
        if f.endswith('.json'):
            file_path = os.path.join(category_directory, f)
            with open(file_path, 'r', encoding='utf-8') as file:
                questions = json.load(file)
                question_count = len(questions)
            quiz_files.append((f[:-5], question_count))
    return quiz_files


def load_random_questions(file_path, questions_count, random_enabled):
    """
    Loads questions from a file, either randomly or sequentially based on settings.
    Args:
        file_path (str): The path to the quiz file.
        questions_count (int): The number of questions to load.
        random_enabled (bool): Flag to determine if questions should be randomized.
    Returns:
        list: A list of quiz questions.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        questions = json.load(file)
    if random_enabled:
        return random.sample(questions, min(questions_count, len(questions)))
    return questions[:questions_count]


async def delete_last_message(context: CallbackContext):
    """
    Asynchronously deletes the last message sent by the bot to the user.
    Args:
        context (CallbackContext): The context object from Telegram.
    """
    last_message = context.user_data.get('last_message')
    if last_message:
        try:
            await last_message.delete()
        except Exception as e:
            logger = context.bot_data['logger']
            logger.error(f"Error deleting last message: {e}")


async def send_question(update: Update, context: CallbackContext,
                        config: Dict[str, Any]) -> None:
    """
    Sends a quiz question to the user.
    Args:
        update (Update): The update object from Telegram.
        context (CallbackContext): The context object from Telegram.
        config (Dict[str, Any]): The bot's configuration dictionary.
    """
    localization = context.bot_data['localization']
    emoji = config['emoji']
    parse_mode = context.bot_data['parse_mode']
    current_index = context.user_data.get('current_index', 0)
    total_questions = len(context.user_data.get('quiz_data', []))
    current_question = context.user_data['quiz_data'][current_index]
    query = update.callback_query

    remaining_seconds = context.user_data.get('remaining_time', 0)
    remaining_minutes = remaining_seconds // 60
    remaining_seconds %= 60
    remaining_time_text = f"{emoji['timer_limit']} " + localization.get("time_remaining",
                                                                        minutes=remaining_minutes,
                                                                        seconds=remaining_seconds) + "\n\n"

    question_text = f"{emoji['test']} Q{current_index + 1}. {current_question['question']}\n\n"
    options = current_question['answers']

    message_text = f"{remaining_time_text}{question_text}\n"
    for option in options:
        message_text += f"{option}\n\n"

    keyboard = [[InlineKeyboardButton(
        option.split(':')[0].strip() if ':' in option else option.split('.')[0].strip(),
        callback_data=option.split(':')[0].strip() if ':' in option else
        option.split('.')[0].strip()[:MAX_BUTTON_LENGTH])] for option in options]
    keyboard.append([InlineKeyboardButton(
        f"{emoji['back_button']} {localization.get('back_button')}",
        callback_data="list_tests")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot_data['logger'].info(
        f"Sending message: '{message_text}' in mode: {parse_mode}")

    try:
        if query:
            sent_message = await query.edit_message_text(text=message_text,
                                                         reply_markup=reply_markup,
                                                         parse_mode=parse_mode)
        else:
            sent_message = await context.bot.send_message(
                chat_id=update.effective_chat.id, text=message_text,
                reply_markup=reply_markup, parse_mode=parse_mode)
        context.user_data['last_message'] = sent_message
    except Exception as e:
        logger = context.bot_data['logger']
        logger.error(f"Error sending question message: {e}")
        sent_message = await context.bot.send_message(chat_id=update.effective_chat.id,
                                                      text=message_text,
                                                      reply_markup=reply_markup,
                                                      parse_mode=parse_mode)
        context.user_data['last_message'] = sent_message


async def send_results(update, context, config):
    """
    Sends quiz results to the user after the quiz is completed.
    Args:
        update (Update): The update object from Telegram.
        context (CallbackContext): The context object from Telegram.
        config (Dict[str, Any]): The bot's configuration dictionary.
    """
    localization = context.bot_data['localization']
    emoji = config['emoji']
    correct_count = context.user_data.get('correct_count', 0)
    total_questions = len(context.user_data['quiz_data'])
    success_rate = (correct_count / total_questions) * 100
    required_success_rate = config['base_settings']['success_rate']

    result_text = localization.get("quiz_answered_correctly",
                                   correct_count=correct_count,
                                   total_questions=total_questions) + "\n"
    result_text += localization.get("quiz_success_rate",
                                    success_rate=success_rate) + "\n"
    if success_rate >= required_success_rate:
        result_text += localization.get("quiz_passed")
    else:
        result_text += f"{emoji['failed']} " + localization.get("quiz_failed")

    keyboard = [
        [InlineKeyboardButton(
            f"{emoji['restart_button']} {localization.get('restart_button')}",
            callback_data="restart")],
        [InlineKeyboardButton(
            f"{emoji['back_button']} {localization.get('list_tests_button')}",
            callback_data="list_tests")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        await update.callback_query.edit_message_text(text=result_text,
                                                      reply_markup=reply_markup)
    except Exception as e:
        logger = context.bot_data['logger']
        logger.error(f"Error editing the results message: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=result_text, reply_markup=reply_markup)


async def handle_category_selection(update: Update, context: CallbackContext, query,
                                    questions_directory, logger):
    """
    Handles the selection of a quiz category by the user.
    Args:
        update (Update): The update object from Telegram.
        context (CallbackContext): The context object from Telegram.
        query (CallbackQuery): The callback query containing the selected category.
        questions_directory (str): Path to the questions directory.
        logger (Logger): Logger for logging errors and info messages.
    """
    localization = context.bot_data['localization']
    config = context.bot_data['config']
    emoji = config['emoji']
    category = query.data.split('_', 1)[1]
    category_directory = os.path.join(questions_directory, category)
    quiz_files = get_quiz_files(category_directory, logger)
    if quiz_files:
        keyboard = [
            [InlineKeyboardButton(
                f"{emoji['test']} {file} ({count} {localization.get('questions_count_suffix')})",
                callback_data=f"quiz_{file}_{category}")]
            for file, count in quiz_files]
        keyboard.append([InlineKeyboardButton(
            f"{emoji['back_button']} {localization.get('back_button')}",
            callback_data="main_menu")])  # Adding "Back" button
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = localization.get("choose_category")
        await query.message.edit_text(text, reply_markup=reply_markup)
    else:
        await query.message.edit_text(
            localization.get("category_empty", category=category))


async def handle_quiz_selection(update: Update, context: CallbackContext, query,
                                questions_directory, logger):
    """
    Handles the selection of a quiz and starts it.
    Args:
        update (Update): The update object from Telegram.
        context (CallbackContext): The context object from Telegram.
        query (CallbackQuery): The callback query containing the selected quiz.
        questions_directory (str): Path to the questions directory.
        logger (Logger): Logger for logging errors and info messages.
    """
    localization = context.bot_data['localization']
    await delete_last_message(context)  # Deleting the last message
    questions_count = context.bot_data.get('questions_count',
                                           context.bot_data['config']['base_settings'][
                                               'questions_count'][0])
    questions_random_enabled = context.bot_data.get('questions_random_enabled',
                                                    context.bot_data['config'][
                                                        'base_settings'][
                                                        'questions_random_enabled'])
    logger.info(f"Selected questions count: {questions_count}")

    _, quiz_name, category = query.data.split('_', 2)
    category_directory = os.path.join(questions_directory, category)
    quiz_file_path = os.path.join(category_directory, quiz_name + '.json')
    logger.info(f"Trying to open file: {quiz_file_path}")

    if os.path.exists(quiz_file_path):
        config = context.bot_data['config']
        quiz_data = load_random_questions(quiz_file_path, questions_count,
                                          questions_random_enabled)
        context.user_data['quiz_data'] = quiz_data
        context.user_data['current_index'] = 0
        context.user_data['correct_count'] = 0
        context.user_data['last_quiz'] = quiz_name
        context.user_data['last_category'] = category  # Saving the last category
        context.user_data['query'] = query

        # Start the timer if enabled
        if config['base_settings']['timer_enabled']:
            timer_limit = context.bot_data.get('timer_limit',
                                               config['base_settings']['timer_limit'][0])
            context.user_data[
                'remaining_time'] = timer_limit * 60  # Convert minutes to seconds
            context.user_data['timer_task'] = asyncio.create_task(
                start_timer(update, context, timer_limit))

        await send_question(update, context, config)
    else:
        await query.message.edit_text(localization.get("quiz_not_found"))
    user_id = query.from_user.id
    logger.info(f"User {user_id} selected quiz: {quiz_name}")


async def handle_quiz_response(update: Update, context: CallbackContext, answer: str):
    """
    Handles the user's answer to a quiz question.
    Args:
        update (Update): The update object from Telegram.
        context (CallbackContext): The context object from Telegram.
        answer (str): The user's selected answer.
    """
    localization = context.bot_data['localization']
    emoji = context.bot_data['config']['emoji']
    try:
        config = context.bot_data['config']
        logger = context.bot_data['logger']

        current_index = context.user_data.get('current_index', 0)
        quiz_data = context.user_data['quiz_data']
        current_question = quiz_data[current_index]

        message_text = format_question_message(current_question, answer, emoji,
                                               localization)

        if extract_key(answer) == extract_key(current_question['correct_answer']):
            context.user_data['correct_count'] += 1

        log_quiz_response(logger, update.effective_user.id, current_question, answer)

        query = update.callback_query

        if current_index >= len(quiz_data) - 1:
            # Cancel the timer task if the quiz is completed
            if 'timer_task' in context.user_data:
                context.user_data['timer_task'].cancel()
            await query.edit_message_text(text=message_text, reply_markup=None)
            await send_results(update, context, config)
        else:
            context.user_data['current_index'] += 1
            next_question_index = context.user_data['current_index'] + 1
            remaining_seconds = context.user_data.get('remaining_time', 0)
            remaining_minutes = remaining_seconds // 60
            remaining_seconds %= 60
            keyboard = [
                [InlineKeyboardButton(
                    f"{emoji['next_button']} {localization.get('next_question_button', next_question_index=next_question_index, total_questions=len(quiz_data))}",
                    callback_data='next_question')],
                [InlineKeyboardButton(
                    f"{emoji['back_button']} {localization.get('back_button')}",
                    callback_data="list_tests")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            sent_message = await query.edit_message_text(text=message_text,
                                                         reply_markup=reply_markup)
            context.user_data['last_message'] = sent_message
    except KeyError as e:
        logger.error(f"KeyError: {e}")
        await update.callback_query.message.edit_text(
            localization.get("error_finding_quiz_data"))
    except Exception as e:
        logger.error(f"Unexpected error in handle_quiz_response: {e}")
        await update.callback_query.message.edit_text(
            localization.get("unexpected_error"))


async def start_timer(update: Update, context: CallbackContext, timer_limit):
    """
    Starts a timer for the quiz duration.
    Args:
        update (Update): The update object from Telegram.
        context (CallbackContext): The context object from Telegram.
        timer_limit (int): The time limit for the quiz in minutes.
    """
    total_seconds = timer_limit * 60
    try:
        while total_seconds > 0:
            await asyncio.sleep(1)  # 1 second
            total_seconds -= 1
            context.user_data['remaining_time'] = total_seconds
        await end_quiz_due_to_time_limit(update, context)
    except asyncio.CancelledError:
        # Timer was cancelled
        pass


async def end_quiz_due_to_time_limit(update: Update, context: CallbackContext):
    """
    Ends the quiz when the time limit is reached and sends the results to the user.
    Args:
        update (Update): The update object from Telegram.
        context (CallbackContext): The context object from Telegram.
    """
    localization = context.bot_data['localization']
    config = context.bot_data['config']
    emoji = config['emoji']
    correct_count = context.user_data.get('correct_count', 0)
    total_questions = len(context.user_data['quiz_data'])
    success_rate = (correct_count / total_questions) * 100
    required_success_rate = config['base_settings']['success_rate']

    result_text = f"{emoji['timer']} " + localization.get("time_up",
                                                          correct_count=correct_count,
                                                          total_questions=total_questions,
                                                          success_rate=success_rate) + "\n"
    if success_rate >= required_success_rate:
        result_text += localization.get("quiz_passed")
    else:
        result_text += f"{emoji['failed']} " + localization.get("quiz_failed")

    keyboard = [
        [InlineKeyboardButton(
            f"{emoji['restart_button']} {localization.get('restart_button')}",
            callback_data="restart")],
        [InlineKeyboardButton(
            f"{emoji['back_button']} {localization.get('list_tests_button')}",
            callback_data="list_tests")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=result_text,
                                   reply_markup=reply_markup)


def format_question_message(current_question: dict, answer: str, emoji: dict,
                            localization) -> str:
    """
    Formats the question message with the user's answer and correct answer.
    Args:
        current_question (dict): The current quiz question.
        answer (str): The user's selected answer.
        emoji (dict): Emoji configurations.
        localization (dict): Localization strings.
    Returns:
        str: The formatted message text.
    """
    message_text = f"{emoji['test']} {current_question['question']}\n\n"
    for option in current_question['answers']:
        option_key = extract_key(option)

        if extract_key(answer) == option_key and option_key == extract_key(
                current_question['correct_answer']):
            message_text += f"{option} ✅\n\n"
        elif option_key == extract_key(current_question['correct_answer']):
            message_text += f"{option} ✅\n\n"
        elif option_key == extract_key(answer):
            message_text += f"{option} ❌\n\n"
        else:
            message_text += f"{option}\n\n"

    if 'explanation' in current_question and current_question['explanation'].strip():
        message_text += f"\n{current_question['explanation']}"

    return message_text


def extract_key(option: str) -> str:
    """
    Extracts the key from an option string.
    Args:
        option (str): The option string.
    Returns:
        str: The extracted key.
    """
    if ':' in option:
        return option.split(':', 1)[0].strip()
    elif '.' in option:
        return option.split('.', 1)[0].strip()
    return option.strip()


def log_quiz_response(logger, user_id: int, current_question: dict, answer: str) -> None:
    """
    Logs the user's response to a quiz question.
    Args:
        logger (Logger): Logger for logging errors and info messages.
        user_id (int): The user's Telegram ID.
        current_question (dict): The current quiz question.
        answer (str): The user's selected answer.
    """
    logger.info(f"Question: {current_question['question']}")
    logger.info(f"Given Answer: {answer}")
    logger.info(f"Correct Answer: {current_question['correct_answer']}")
    logger.info(
        f"Is Correct: {extract_key(answer) == extract_key(current_question['correct_answer'])}")


async def stop_timer(context: CallbackContext) -> None:
    """
    Stops the timer task if it is running.
    Args:
        context (CallbackContext): The context object from Telegram.
    """
    if 'timer_task' in context.user_data:
        context.user_data['timer_task'].cancel()
