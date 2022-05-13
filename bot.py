"""
Telegram Bot that provides training information and encouragement to SGS NDP 2022 participants.
"""

import logging
import os
from datetime import datetime
import json
import re
import requests

from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

# TOKEN = os.environ["TOKEN"]

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

FIRST_STEP = range(1)
LOGIN_STEP = range(1)

#/start handler
def start(update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    #reset
    context.user_data.pop('participantCode', None)
    context.user_data.pop('token', None)
    update.message.reply_text("What's your participant code:")
    logging.info('User attempting login: '+update.message.from_user.first_name)
    return LOGIN_STEP

#start: login
def login_step(update, context):
    if update.message.from_user.username==None:
        username=""
    else:
        username=update.message.from_user.username
    if update.message.from_user.last_name==None:
        lastname=""
    else:
        lastname=update.message.from_user.last_name

    #check if valid participantCode
    isValidPartCode = re.match("^[AaBbCcDdEeFf][0-9][0-9][0-9]$", update.message.text)
    if isValidPartCode:
        partCode=update.message.text.capitalize()
        context.user_data["participantCode"] = partCode
        # url = 'https://telegrambots-db.herokuapp.com/api/namjaninjabot/user/'+partCode+'/'
        url = 'http://127.0.0.1:8000/api/namjaninjabot/user/'+partCode+'/'
        data = {
                'participantCode':partCode,
                'username':username,
                'firstname': update.message.from_user.first_name,
                'lastname': lastname
        }
        response = requests.post(url, data = data)
        data = response.text
        parse_json = json.loads(data)
        context.user_data["token"] = parse_json['token']
        if response.status_code == 200:
            keyboard = [
                [KeyboardButton("Next NDP activity?")],
                [KeyboardButton("Zoom link?")],
                [KeyboardButton("Last updated?")],
                [KeyboardButton("Daily encouragement")],
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard)
            logging.info('Successful login by '+update.message.from_user.first_name+' ('+username+", "+ partCode+')')
            update.message.reply_text('Please select your query:', reply_markup=reply_markup)
            return ConversationHandler.END
        else:
            update.message.reply_text('Unable to process request at this time. Please try again later')
            return ConversationHandler.END
    else:
        update.message.reply_text('Invalid participant code. Please try again:')
        return LOGIN_STEP

#/help handler
def help(update, context):
    if update.message.from_user.username==None:
        username=""
        logging.info('Command issued by '+update.message.from_user.first_name+': help')
    else:
        username=update.message.from_user.username
        logging.info('Command issued by '+update.message.from_user.first_name+' ('+username+') '+': help')
    """Send a message when the command /help is issued."""
    update.message.reply_text('Hi '+update.message.from_user.first_name+'! I am NamjaNinja! I can assist you on your SGS NDP 2022 journey!\n\nSend the following commands to get started:\n/start - Lists all the queries I can help you with\n/about - Learn more about me\n/feedback - Tell me how I can improve\n/help - Describes how to use me')

#/about handler
def about(update, context):
    if update.message.from_user.username==None:
        username=""
        logging.info('Command issued by '+update.message.from_user.first_name+': about')
    else:
        username=update.message.from_user.username
        logging.info('Command issued by '+update.message.from_user.first_name+' ('+username+') '+': about')
    """Send a message when the command /about is issued."""
    update.message.reply_text('NamjaNinjaBot is a telegram bot that is aimed at easily allowing Soka Gakkai Singapore (SGS) NDP 2022 participants to obtain NDP training and meeting details easily and quickly. Participants can also get daily encouragements through the bot.\n\nThis bot was created in good faith by one of the participants to be a handy companion to the participants and should strictly be used for such purposes only. Thank you for your understanding')

#determine reply after query chosen
def reply(update, context):
    if 'participantCode' in context.user_data and context.user_data["participantCode"]!="":
        if update.message.from_user.username==None:
            username=""
        else:
            username=update.message.from_user.username
        if update.message.text=="Next NDP activity?":
            if update.message.from_user.username==None:
                logging.info('Question asked by '+update.message.from_user.first_name+': Next NDP activity?')
            else:
                logging.info('Question asked by '+update.message.from_user.first_name+' ('+username+') '+': Next NDP activity?')
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
            if update.message.from_user.username==None:
                logging.info('Question asked by '+update.message.from_user.first_name+': Last updated?')
            else:
                logging.info('Question asked by '+update.message.from_user.first_name+' ('+username+') '+': Last updated?')
            with open('./training.json', 'r') as f:
                data = json.load(f)
                f.close()
                update.message.reply_text("The training schedule for the bot was last updated on: "+data["lastupdate"])

        elif update.message.text=="Zoom link?":
            if update.message.from_user.username==None:
                logging.info('Question asked by '+update.message.from_user.first_name+': Zoom link?')
            else:
                logging.info('Question asked by '+update.message.from_user.first_name+' ('+username+') '+': Zoom link?')
            with open('./training.json', 'r') as f:
                data = json.load(f)
                f.close()
            update.message.reply_text("Zoom Link: "+data["zoomlink"])

        elif update.message.text=="Daily encouragement":
            if update.message.from_user.username==None:
                logging.info('Question asked by '+update.message.from_user.first_name+': Daily encouragement')
            else:
                logging.info('Question asked by '+update.message.from_user.first_name+' ('+username+') '+': Daily encouragement')
            link="https://www.sokaglobal.org/resources/daily-encouragement/"
            today = datetime.now()
            month=today.strftime("%B").lower()
            link = link + month + "-" + str(today.day) + ".html"
            update.message.reply_text(link)  
        else:
            update.message.reply_text('Please select a valid question or type /help')
    else:
        update.message.reply_text('Please type /start first')

#/feedback handler
def feedback(update, context):
    if update.message.from_user.username==None:
        username=""
        logging.info('Command issued by '+update.message.from_user.first_name+': feedback')
    else:
        username=update.message.from_user.username
        logging.info('Command issued by '+update.message.from_user.first_name+' ('+username+') '+': feedback')
    """Send a message when the command /feedback is issued."""
    update.message.reply_text('NamjaNinjaBot will listen to all feedback. Please follow the steps to submit one. If you decided to change your mind, just type /cancel')
    update.message.reply_text("Please type your feedback:")
    return FIRST_STEP

#feedback: get participant code
def first_step(update, context):
    lengthOfFeedback=len(update.message.text)
    if lengthOfFeedback<=500:
        if update.message.from_user.last_name==None:
            lastname=""
        else:
            lastname=update.message.from_user.last_name
        if update.message.from_user.username==None:
            username=""
        else:
            username=update.message.from_user.username
        # if logged in
        if 'participantCode' in context.user_data and context.user_data["participantCode"]!="":
            partCode=context.user_data["participantCode"]
            # url = 'https://telegrambots-db.herokuapp.com/api/namjaninjabot/feedback/'+partCode+'/'
            url = 'http://127.0.0.1:8000/api/namjaninjabot/feedback/'+partCode+'/'
        else:
            partCode=""
            # url = 'https://telegrambots-db.herokuapp.com/api/namjaninjabot/feedback/nil/'
            url = 'http://127.0.0.1:8000/api/namjaninjabot/feedback/nil/'
        data = {'participantCode': partCode,
                'username':username,
                'firstname': update.message.from_user.first_name,
                'lastname': lastname,
                "feedback": update.message.text
                }
        response = requests.post(url, data = data)
        if response.status_code == 201:
            update.message.reply_text("Thank you for your feedback!")
            if update.message.from_user.username==None:
                logging.info(update.message.from_user.first_name+' successfully submitted feedback')
            else:
                logging.info(update.message.from_user.first_name+' ('+username+') '+'successfully submitted feedback')
            return ConversationHandler.END
        else:
            if update.message.from_user.username==None:
                logging.info(update.message.from_user.first_name+' failed to submit feedback')
            else:
                logging.info(update.message.from_user.first_name+' ('+username+') '+'failed to submit feedback')
            update.message.reply_text("Failed to submit feedback. Please try again later")
            return ConversationHandler.END
    else:
        update.message.reply_text('Feedback is too long. It should be less than 500 characters. The submitted feedback was '+str(lengthOfFeedback)+' characters long. Please try again')
        return FIRST_STEP

#/cancel handler
def cancel(update, context):
    if update.message.from_user.username==None:
        username=""
        logging.info('Command issued by '+update.message.from_user.first_name+': cancel')
    else:
        username=update.message.from_user.username
        logging.info('Command issued by '+update.message.from_user.first_name+' ('+username+') '+': cancel')
    update.message.reply_text("Cancelled feedback submission")
    return ConversationHandler.END

#/error handler
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

    # handle login conversation
    conversation_handlerLogin = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            LOGIN_STEP: [MessageHandler(Filters.text & ~Filters.command, login_step)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dp.add_handler(conversation_handlerLogin)

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("about", about))

    # handle feedback conversation
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('feedback', feedback)],
        states={
            FIRST_STEP: [MessageHandler(Filters.text & ~Filters.command, first_step)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dp.add_handler(conversation_handler)

    # on noncommand i.e message - reply the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, reply))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    # PORT = int(os.environ.get("PORT", "8443"))
    # updater.start_webhook(listen="0.0.0.0",
    #                       port=PORT,
    #                       url_path=TOKEN,
    #                       webhook_url="https://namjaninjabot.herokuapp.com/" + TOKEN)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()