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
import os
from datetime import datetime
import json

from telegram.utils.helpers import escape_markdown
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup, KeyboardButton, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

# TOKEN = os.environ["TOKEN"]

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    keyboard = [
        [KeyboardButton("Next NDP activity?")],
        [KeyboardButton("Zoom link?")],
        [KeyboardButton("Last updated?")],
        [KeyboardButton("Daily encouragement")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard)
    update.message.reply_text('Please select your query:', reply_markup=reply_markup)

def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Hi there! I can assist you on your SGS NDP 2022 journey!\n\nSend the following commands to get started:\n/start - Lists all the queries I can help you with!\n/about - Learn more about me!\n/help - Describes how to use me!')

def about(update, context):
    """Send a message when the command /about is issued."""
    update.message.reply_text('xxxbot is a telegram bot that is aimed at easily allowing Soka Gakkai Singapore (SGS) NDP 2022 participants to obtain NDP training and meeting details easily and quickly. Participants can also get daily encouragements through the bot.\n\nThis bot was created in good faith by one of the participants to be a handy companion to the participants and should strictly be used for such purposes only. Thank you for your understanding.')

def reply(update, context):
    if update.message.text=="Next NDP activity?":
        # Find next NDP activity
        with open('./training.json', 'r') as f:
            data = json.load(f)
            f.close()
        today = datetime.now()
        daysdiff=""
        smallestDateIndex=""
        i=0
        for item in data["schedule"]:
            if item["datetime_end"]!="TBA":
                datetimeInterator=datetime.strptime(item["datetime_end"], '%Y-%m-%dT%H:%M:%S')
                if datetimeInterator > today:
                    difftemp=datetimeInterator-today
                    if daysdiff == "" or difftemp < daysdiff:
                        smallestDateIndex=i
                        daysdiff=difftemp
            i=i+1
        # Format Date to Display
        dateToFormat=datetime.strptime(data["schedule"][smallestDateIndex]["datetime_start"], '%Y-%m-%dT%H:%M:%S')
        dateToFormatEnd=datetime.strptime(data["schedule"][smallestDateIndex]["datetime_end"], '%Y-%m-%dT%H:%M:%S')
        reply="*"+data["schedule"][smallestDateIndex]["title"]+"*\n"+"📍: "+data["schedule"][smallestDateIndex]["location"]+"\n"+"📅:"+dateToFormat.strftime(" %d %b %Y").replace(' 0', ' ')+"\n"+"🕓:"+dateToFormat.strftime(" %I:%M%p -").replace(' 0', ' ') + dateToFormatEnd.strftime(" %I:%M%p").replace(' 0', ' ')
        if data["schedule"][smallestDateIndex]["Note"]!="Nil":
            reply=reply+"\n"+"📝: "+data["schedule"][smallestDateIndex]["Note"]
        if data["schedule"][smallestDateIndex]["location"]=="Zoom":
            reply=reply+"\n"+"Zoom Link: "+data["zoomlink"]
        if data["schedule"][smallestDateIndex]["title"]=="NDP Training":
            reply=reply+"\n\n"+"Attire: "
            for i in range(0, len(data["training_attire"])):
                reply=reply+"\n    "+"- "+data["training_attire"][i]
            if data["schedule"][smallestDateIndex]["location"]=="Keat Hong Camp":
                reply=reply+"\n"+"Things to Bring: "
                for i in range(0, len(data["training_bring"])):
                    reply=reply+"\n    "+str(i+1)+") "+data["training_bring"][i]
        update.message.reply_text(reply, parse_mode='Markdown')

    elif update.message.text=="Last updated?":
        with open('./training.json', 'r') as f:
            data = json.load(f)
            f.close()
            update.message.reply_text("The training schedule for the bot was last updated on: "+data["lastupdate"])

    elif update.message.text=="Zoom link?":
        with open('./training.json', 'r') as f:
            data = json.load(f)
            f.close()
        update.message.reply_text("Zoom Link: "+data["zoomlink"])

    elif update.message.text=="Daily encouragement":
        link="https://www.sokaglobal.org/resources/daily-encouragement/"
        today = datetime.now()
        month=today.strftime("%B").lower()
        link = link + month + "-" + str(today.day) + ".html"
        update.message.reply_text(link)
        
    else:
        update.message.reply_text('Please select a valid question')

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("5364483829:AAFwah_x3WCBtiRJ7cnVv9JFIt_kQgp7g_k", use_context=True)
    # updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("about", about))

    # on noncommand i.e message - reply the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, reply))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    # PORT = int(os.environ.get("PORT", "8443"))
    # updater.start_webhook(listen="0.0.0.0",
    #                       port=PORT,
    #                       url_path=TOKEN)
    # updater.bot.set_webhook("https://{}.herokuapp.com/{}".format("fishyyybot", TOKEN))

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()