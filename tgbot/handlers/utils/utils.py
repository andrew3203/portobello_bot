import imp
import redis
from tgbot.models import User, Message
import datetime

from django.utils import timezone
from tgbot.handlers.broadcast_message.utils import _send_message
from telegram import ParseMode, Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from tgbot.handlers.onboarding import static_text
from tgbot.handlers.utils.info import extract_user_data_from_update


def get_marckup():
    pass


def get_message_text():
    pass


def check_state():
    pass


def set_state():
    pass


def send_message():
    pass


def send_poll():
    pass
