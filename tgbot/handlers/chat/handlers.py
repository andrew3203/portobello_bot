import datetime
import logging

from django.utils import timezone
from telegram import ParseMode, Update
from telegram.ext import CallbackContext

from tgbot.handlers.onboarding import static_text
from tgbot.models import Message, User
from tgbot.handlers.onboarding.keyboards import make_keyboard_for_start_command
from tgbot.handlers.utils import utils
from tgbot.handlers.utils.info import extract_user_data_from_update
from telegram import ReplyKeyboardRemove


def command_start(update: Update, context: CallbackContext) -> None:
    u, created = User.get_user_and_created(update, context)
    user_balance = utils.get_user_info(u.user_id, u.deep_link)
    u.update_info(user_balance)
    if u.deep_link:
        if created:
            utils.send_registration(user_code=u.deep_link, user_id=u.user_id)
            update.message.reply_text('Вы успешно зарегистрированы в программе лояльности!')
        else:
            recive_command(update, context)

    else:
        recive_command(update, context)
    


def command_balance(update: Update, context: CallbackContext) -> None:
    u, _ = User.get_user_and_created(update, context)
    user_balance = utils.get_user_info(u.user_id, u.deep_link)
    u.update_info(user_balance)

    recive_command(update, context)


def recive_command(update: Update, context: CallbackContext) -> None:
    user_id = extract_user_data_from_update(update)["user_id"]
    msg_text = update.message.text.replace('/', '') 
    print(f'recive command {msg_text} from {user_id}')
    prev_state, next_state = User.get_prev_next_states(user_id, msg_text)

    print('message_id', context.user_data.get('prev_msg_id', None))
    prev_msg_id = utils.send_message(
        prev_state=prev_state,
        next_state=next_state,
        user_id=user_id,
        context=context,
        prev_message_id=context.user_data.get('prev_msg_id', None)
    )
    context.user_data['prev_msg_id'] = prev_msg_id
    print('prev_msg_id', context.user_data['prev_msg_id'])


def recive_message(update: Update, context: CallbackContext) -> None:
    user_id = extract_user_data_from_update(update)["user_id"]
    msg_text = update.message.text
    print(f'recive recive_message from {user_id} {msg_text}')

    prev_state, next_state = User.get_prev_next_states(user_id, msg_text)

    prev_msg_id = utils.send_message(
        prev_state=prev_state,
        next_state=next_state,
        user_id=user_id,
        context=context,
        prev_message_id=context.user_data.get('prev_msg_id', None)
    )
    context.user_data['prev_msg_id'] = prev_msg_id


def recive_calback(update: Update, context: CallbackContext) -> None:
    user_id = extract_user_data_from_update(update)["user_id"]
    msg_text = update.callback_query.data

    print(f'recive recive_calback from {user_id} {msg_text}')
    update.callback_query.answer()
    _, next_state = User.get_prev_next_states(user_id, msg_text)

    prev_msg_id = utils.edit_message(
        next_state=next_state,
        user_id=user_id,
        update=update
    )
    context.user_data['prev_msg_id'] = prev_msg_id


def receive_poll_answer(update: Update, context) -> None:
    # TODO: check
    answer = update.poll_answer
    answered_poll = context.bot_data[answer.poll_id]

    context.bot.stop_poll(
        answered_poll["chat_id"], answered_poll["message_id"])

    user_id = extract_user_data_from_update(update)["user_id"]
    msg_text = answered_poll.lower().replace(' ', '')

    prev_state, next_state = User.get_prev_next_states(user_id, msg_text)

    prev_msg_id = utils.send_message(
        prev_state=prev_state,
        next_state=next_state,
        user_id=user_id,
        context=context,
        prev_message_id=context.user_data.get('prev_msg_id', None)
    )
    context.user_data['prev_msg_id'] = prev_msg_id


def forward_from_support(update: Update, context: CallbackContext) -> None:
    msg_text = update.message.text

    pass


def forward_to_support(update: Update, context: CallbackContext) -> None:
    user_id = extract_user_data_from_update(update)["user_id"]
    msg_text = update.message.text.lower()
    prev_state, next_state = User.get_prev_next_states(user_id, msg_text)

    prev_msg_id = utils.send_message(
        prev_state=prev_state,
        next_state=next_state,
        user_id=user_id,
        context=context,
        prev_message_id=context.user_data.get('prev_msg_id', None)
    )
    context.user_data['prev_msg_id'] = prev_msg_id
