"""
    Telegram event handlers
"""
import logging
import sys
from typing import Dict

import telegram.error
from dtb.celery import app  # event processing in async mode
from dtb.settings import DEBUG, TELEGRAM_SUPPORT_CHAT, TELEGRAM_TOKEN
from telegram import Bot, BotCommand, Update
from telegram.ext import (CallbackQueryHandler, CommandHandler, Dispatcher,
                          MessageHandler, PollAnswerHandler, Updater)
from telegram.ext.filters import Filters

from tgbot.handlers.admin import handlers as admin_handlers
from tgbot.handlers.broadcast_message import handlers as broadcast_handlers
from tgbot.handlers.broadcast_message.manage_data import \
    CONFIRM_DECLINE_BROADCAST
from tgbot.handlers.broadcast_message.static_text import broadcast_command
from tgbot.handlers.chat import handlers as chat
from tgbot.handlers.onboarding import handlers as onboarding_handlers
from tgbot.handlers.onboarding.manage_data import SECRET_LEVEL_BUTTON
from tgbot.handlers.utils import error, files


def setup_dispatcher(dp):
    """
    Adding handlers for events from Telegram
    """
    # onboarding
    dp.add_handler(CommandHandler("start", chat.command_start))

    # recive all messages
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, chat.recive_message))

    # recive all callback
    dp.add_handler(CallbackQueryHandler(chat.recive_calback))

    # recive all pools
    dp.add_handler(PollAnswerHandler(chat.receive_poll_answer))


    # admin commands
    dp.add_handler(CommandHandler("admin", admin_handlers.admin, filters=~Filters.chat(chat_id=int(TELEGRAM_SUPPORT_CHAT))))
    dp.add_handler(CommandHandler(
        "stats",
        admin_handlers.stats,
        filters=~Filters.chat(chat_id=int(TELEGRAM_SUPPORT_CHAT))
    ))
    dp.add_handler(CommandHandler(
        'export_users',
        admin_handlers.export_users, 
        filters=~Filters.chat(chat_id=int(TELEGRAM_SUPPORT_CHAT))
    ))

    # files
    dp.add_handler(MessageHandler(Filters.animation, files.show_file_id))

    # handling errors
    dp.add_error_handler(error.send_stacktrace_to_tg_chat)

    # recive answers from admin in support chat
    dp.add_handler(MessageHandler(
        Filters.chat(chat_id=int(TELEGRAM_SUPPORT_CHAT)) & Filters.forwarded & (Filters.photo | Filters.video | Filters.animation),
        chat.forward_from_support,
    ))

    return dp


def run_pooling():
    """ Run bot in pooling mode """
    updater = Updater(TELEGRAM_TOKEN, use_context=True)

    dp = updater.dispatcher
    dp = setup_dispatcher(dp)

    bot_info = Bot(TELEGRAM_TOKEN).get_me()
    bot_link = f"https://t.me/" + bot_info["username"]

    print(f"Pooling of '{bot_link}' started")
    # it is really useful to send '👋' emoji to developer
    # when you run local test
    # bot.send_message(text='👋', chat_id=<YOUR TELEGRAM ID>)

    updater.start_polling()
    updater.idle()


# Global variable - best way I found to init Telegram bot
bot = Bot(TELEGRAM_TOKEN)
try:
    TELEGRAM_BOT_USERNAME = bot.get_me()["username"]
except telegram.error.Unauthorized:
    logging.error(f"Invalid TELEGRAM_TOKEN.")
    sys.exit(1)


@app.task(ignore_result=True)
def process_telegram_event(update_json):
    update = Update.de_json(update_json, bot)
    dispatcher.process_update(update)


def set_up_commands(bot_instance: Bot) -> None:
    langs_with_commands: Dict[str, Dict[str, str]] = {
        'en': {
            'start': 'Start django bot 🚀',
            'support': 'Send message to Pavel 👥',
        },
        'ru': {
            'start': 'Запустить django бота 🚀',
            'support': 'Написать Павлу 👥',
        }
    }

    bot_instance.delete_my_commands()
    for language_code in langs_with_commands:
        bot_instance.set_my_commands(
            language_code=language_code,
            commands=[
                BotCommand(command, description) for command, description in langs_with_commands[language_code].items()
            ]
        )


# WARNING: it's better to comment the line below in DEBUG mode.
# Likely, you'll get a flood limit control error, when restarting bot too often
# set_up_commands(bot)

n_workers = 0 if DEBUG else 4
dispatcher = setup_dispatcher(Dispatcher(
    bot, update_queue=None, workers=n_workers, use_context=True))
