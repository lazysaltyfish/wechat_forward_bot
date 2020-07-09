#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.
"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import argparse
import requests
import re

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from urllib.parse import urlparse

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

_parser = argparse.ArgumentParser(description='Pull artical links and push to Telegram channel.')
_parser.add_argument('--token', type=str, required=True, help='Telegram bot token.')
_parser.add_argument('--chat_id', type=str, required=True, help='Chat id.')
_parser.add_argument('--from_id', type=str, required=False, default="", help='Only forward message from specific user.')
_parser.add_argument('--dryrun', type=bool, required=False, default=False, help='Dry run.')
_args = _parser.parse_args()

TOKEN = _args.token
CHAT_ID = _args.chat_id
FROM_ID = _args.from_id
IS_DRYRUN = _args.dryrun

REGEX = r"<meta property=\"og:title\" content=\"(.*?)\"[\s\S]*?<meta property=\"og:image\" content=\"(.*?)\"[\s\S]*?<meta property=\"og:description\" content=\"(.*?)\"[\s\S]*?<a href=\"javascript:void\(0\);\" id=\"js_name\">\s*(.*?)\s*</a>"
PATTERN = re.compile(REGEX, flags=re.MULTILINE)

def is_wechat_artical(text):
    try:
        o = urlparse(text)
        if o.netloc != 'mp.weixin.qq.com':
            return False
        if not str(o.path).startswith('/s'):
            return False
        return True
    except ValueError:
        return False


def construct_message_by_url(url):
    AGENT_HEAD = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.3497.92 Safari/537.36"
    headers = {'user-agent': AGENT_HEAD}
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        logging.error("Error on get page")
        return None
    meta_data = re.findall(PATTERN, r.content.decode('utf-8'))[0]
    try:
        title, image, desc, author = meta_data
    except:
        logging.error("Error on extract meta data by regex")
        return None
    return r'#微信' + r' #' + author + '\n\n[' + title + '](' + url + ')\n' + desc


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def echo(update, context):
    """Echo the user message."""
    if update.message is None:
        logging.warning("Receive a empty message")
        return
    if len(FROM_ID) > 0 and str(update.message.chat_id) != FROM_ID:
        logging.warning("Receive a message from " + str(update.message.chat_id) + " ; forward to specific user id")
        update.message.forward(chat_id=FROM_ID)
        return

    logging.info("Receive a message: " + update.message.text)
    result = ""
    md_message = None
    if not is_wechat_artical(update.message.text):
        result = "Not a WeChat artical link"
        logging.warning("Not a Wechat artical link")
    else:
        md_message = construct_message_by_url(update.message.text)
        if md_message is None:
            result = "Cannot parse url page"
        else:
            result = "Success send message:\n" + md_message
    update.message.reply_text(result, disable_web_page_preview=True, parse_mode="Markdown")
    if md_message and not IS_DRYRUN:
        logging.info("Forward a message: " + md_message)
        context.bot.send_message(chat_id=CHAT_ID, text=md_message, disable_web_page_preview=True, parse_mode="Markdown")


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()