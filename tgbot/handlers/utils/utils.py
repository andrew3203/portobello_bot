import imp
from re import M
import redis
from tgbot.models import User, Message, Poll, MessageType
import datetime
import logging

from flashtext import KeywordProcessor
from django.utils import timezone
from tgbot.handlers.broadcast_message.utils import _send_message
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Poll, ParseMode,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
import requests


def get_inline_marckup(markup):
    keyboard = []
    for row in markup:
        keyboard.append([])
        for col in row:
            if len(col) == 2 and col[1]:
                print(f'get_inline_marckup: URL BTN: {col[0]} {col[1]}')
                btn = InlineKeyboardButton(text=col[0], url=col[1])
            else:
                print(f'get_inline_marckup: callback BTN: {col[0]} {col[0].lower().replace(" ", "")}')
                btn = InlineKeyboardButton(
                    text=col[0], callback_data=col[0].lower().replace(' ', ''))
            keyboard[-1].append(btn)
    print(f'get_inline_marckup: result {keyboard}')
    return InlineKeyboardMarkup(keyboard)


def get_keyboard_marckup(markup):
    keyboard = []
    for row in markup:
        keyboard.append([])
        for col in row:
            print(f'get_keyboard_marckup: text BTN: {col[0]}')
            btn = KeyboardButton(text=col[0])
            keyboard[-1].append(btn)
    print(f'get_keyboard_marckup: result {keyboard}')
    return ReplyKeyboardMarkup(keyboard)


def get_message_text(text, user_keywords):
    keyword_processor = KeywordProcessor()
    keyword_processor.add_keywords_from_dict(user_keywords)
    text = keyword_processor.replace_keywords(text)
    return text


def send_poll(context, update, text, markup):
    questions = ["Good", "Really good", "Fantastic", "Great"]
    message = context.bot.send_poll(
        update.effective_chat.id,
        "How are you?",
        questions,
        is_anonymous=False,
        allows_multiple_answers=False,
    )
    # Save some info about the poll the bot_data for later use in receive_poll_answer
    payload = {
        message.poll.id: {
            "questions": questions,
            "message_id": message.message_id,
            "chat_id": update.effective_chat.id,
            "answers": 0,
        }
    }
    context.bot_data.update(payload)


def send_message(prev_state, next_state, user_id, update):
    prev_msg_type = prev_state["message_type"] if prev_state else None
    next_msg_type = next_state["message_type"]

    markup = next_state["markup"]
    message_text = get_message_text(next_state["text"], next_state['user_keywords'])

    if next_msg_type == MessageType.POLL:

        if prev_msg_type == MessageType.KEYBOORD_BTN:
            reply_markup = ReplyKeyboardRemove() if prev_msg_type == MessageType.KEYBOORD_BTN else None
            _send_message(
                user_id=user_id,
                text=message_text,
                reply_markup=reply_markup
            )
        send_poll(
            text='Опрос',
            markup=markup
        )
    elif next_msg_type == MessageType.KEYBOORD_BTN:
        markup = get_keyboard_marckup(markup)
        _send_message(
            user_id=user_id,
            text=message_text,
            reply_markup=markup,
        )
    elif next_msg_type == MessageType.FLY_BTN:
        markup = get_inline_marckup(markup)
        _send_message(
            user_id=user_id,
            text=message_text,
            reply_markup=markup,
        )
    else:
        if prev_msg_type == MessageType.FLY_BTN:
            update.message.edit_message_text(
                text=message_text,
                parse_mode=ParseMode.HTML
            )
        else:
            _send_message(
                user_id=user_id,
                text=message_text
            )

def edit_message(next_state, user_id, update):
    markup = next_state['markup']
    message_text = get_message_text(next_state['text'], next_state['user_keywords'])

    next_msg_type = next_state['message_type']

    if next_msg_type == MessageType.POLL:
        update.callback_query.edit_message_text(
            text=message_text,
            parse_mode=ParseMode.HTML
        )
        send_poll(
            text='Опрос',
            markup=markup
        )

    elif next_msg_type == MessageType.KEYBOORD_BTN:
        markup = get_keyboard_marckup(markup)
        update.callback_query.delete_message()
        _send_message(
            user_id=user_id,
            text=message_text,
            reply_markup=markup,
        )

    elif next_msg_type == MessageType.FLY_BTN:
        markup = get_inline_marckup(markup)
        update.callback_query.edit_message_text(
            text=message_text,
            reply_markup=markup,
            parse_mode=ParseMode.HTML
        )

    else:
        update.callback_query.edit_message_text(
            text=message_text,
            parse_mode=ParseMode.HTML
        )


def send_registration(user_id, user_code):
    pass

def get_user_info(user_id, user_code):
    return {}

def send_broadcast_message(next_state, user_id):
    next_msg_type = next_state["message_type"]

    markup = next_state["markup"]
    message_text = get_message_text(next_state["text"], next_state['user_keywords'])

    if next_msg_type == MessageType.POLL:
        send_poll(text='Опрос', markup=markup)
        reply_markup = None
    elif next_msg_type == MessageType.KEYBOORD_BTN:
        reply_markup = get_keyboard_marckup(markup)
    elif next_msg_type == MessageType.FLY_BTN:
        reply_markup = get_inline_marckup(markup)
    else:
        reply_markup = None

    _send_message(
        user_id=user_id,
        text=message_text,
        reply_markup=reply_markup
    )
