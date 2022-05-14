"""
Telegram Bot that provides training information and encouragement to SGS NDP 2022 participants.
"""

import logging
import os
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import re
import requests
import math

from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

TOKEN = os.environ["TOKEN"]

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

FIRST_STEP = range(1)
LOGIN_STEP = range(1)

baseurl = 'https://telegrambots-db.herokuapp.com/api/namjaninjabot/'
# baseurl = 'http://127.0.0.1:8000/api/namjaninjabot/'

#/start handler
def start(update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    #reset
    context.user_data.pop('participantCode', None)
    context.user_data.pop('token', None)
    context.user_data["cancelCmd"]="login"
    context.user_data["loginTries"]=0
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
    isValidPartCode = re.match("^[AaBbCcDdEeFf][0-6][0-3][0-9]$", update.message.text)
    if isValidPartCode:
        partCode=update.message.text.capitalize().strip()
        context.user_data["participantCode"] = partCode
        url = baseurl+'user/'+partCode+'/'
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
            #got user's session token and participant code. enable user to use the service
            keyboard = [
                [KeyboardButton("Next NDP activity?")],
                [KeyboardButton("Zoom link?")],
                [KeyboardButton("Countdown")],
                [KeyboardButton("Daily encouragement")],
                [KeyboardButton("Last updated?")],
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard)
            context.user_data.pop('cancelCmd', None)
            context.user_data.pop('loginTries', None)
            logging.info('Successful login by '+update.message.from_user.first_name+' ('+username+", "+ partCode+')')
            update.message.reply_text('Please select your query:', reply_markup=reply_markup)
            return ConversationHandler.END
        else:
            context.user_data.pop('cancelCmd', None)
            context.user_data.pop('loginTries', None)
            logging.error('Unsuccessful login by '+update.message.from_user.first_name+' ('+username+", "+ partCode+')')
            update.message.reply_text('Unable to process request at this time. Please try again later')
            return ConversationHandler.END
    else:
        if context.user_data["loginTries"]>=3:
            update.message.reply_text('You can type /cancel to exit')
            logging.warning(update.message.from_user.first_name+' ('+username+') failed to login '+str(context.user_data["loginTries"])+' times')
        context.user_data["loginTries"]=context.user_data["loginTries"]+1
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
    update.message.reply_text('Hi '+update.message.from_user.first_name+'! I am NamjaNinja! I can assist you on your SGS NDP 2022 journey!\n\nSend the following commands to get started:\n/start - Lists all the queries I can help you with\n/about - Learn more about me\n/feedback - Tell me how I can improve\n/help - Describes how to use me\n/share - Share me with your fellow participants')

#/share handler
def share(update, context):
    if update.message.from_user.username==None:
        username=""
        logging.info('Command issued by '+update.message.from_user.first_name+': share')
    else:
        username=update.message.from_user.username
        logging.info('Command issued by '+update.message.from_user.first_name+' ('+username+') '+': share')
    """Send a message when the command /share is issued."""
    update.message.reply_text('Hello! I am NamjaNinjaBot, a telegram Bot that can provide training information and encouragement to SGS NDP 2022 participants\nhttps://t.me/NamjaNinjabot')

#/about handler
def about(update, context):
    if update.message.from_user.username==None:
        username=""
        logging.info('Command issued by '+update.message.from_user.first_name+': about')
    else:
        username=update.message.from_user.username
        logging.info('Command issued by '+update.message.from_user.first_name+' ('+username+') '+': about')
    """Send a message when the command /about is issued."""
    update.message.reply_text('*About*\nNamjaNinjaBot is a telegram bot that is aimed at allowing Soka Gakkai Singapore (SGS) NDP 2022 participants to obtain NDP training and meeting details easily and quickly. Participants can also get daily encouragements through the bot\n\n*Disclaimer*\nThis bot was created in good faith by one of the participants to be a handy companion to the participants and should strictly be used for such purposes only. By using NamjaNinjaBot, you agree to the collection of user data that will solely be used for NamjaNinjaBot performance monitoring and the bot is used for its intended purpose only. Thank you for your understanding', parse_mode='Markdown')

#determine reply after query chosen, ensures participantCode and session token is available
def reply(update, context):
    if 'participantCode' in context.user_data and context.user_data["participantCode"]!="" and 'token' in context.user_data and context.user_data["token"]!="":
        if update.message.from_user.username==None:
            username=""
        else:
            username=update.message.from_user.username
        urlDets = baseurl+'details/'+context.user_data["participantCode"]+"/1/"
        urlTrainings = baseurl+'training/'+context.user_data["participantCode"]+"/1/"
        headers = {
            "token":context.user_data["token"]
        }
        if update.message.text=="Next NDP activity?":
            if update.message.from_user.username==None:
                logging.info('Question asked by '+update.message.from_user.first_name+': Next NDP activity?')
            else:
                logging.info('Question asked by '+update.message.from_user.first_name+' ('+username+') '+': Next NDP activity?')
            # Find next NDP activity
            responseDets=requests.get(urlDets, headers=headers)
            responseTraining=requests.get(urlTrainings, headers=headers)
            if responseDets.status_code == 200 and responseTraining.status_code == 200:
                data = responseDets.text
                dataDets = json.loads(data)
                data = responseTraining.text
                dataTrain = json.loads(data)

                today = datetime.now(ZoneInfo('Singapore'))
                daysdiff=""
                smallestDateIndex=""
                i=0
                for item in dataTrain:
                    if item["datetime_end"]!="TBA":
                        datetimeInterator=datetime.strptime(item["datetime_end"], '%Y-%m-%dT%H:%M:%S')
                        datetimeInterator=datetimeInterator.replace(tzinfo=ZoneInfo('Singapore'))
                        if datetimeInterator > today:
                            difftemp=datetimeInterator-today
                            if daysdiff == "" or difftemp < daysdiff:
                                smallestDateIndex=i
                                daysdiff=difftemp
                    i=i+1
                # Format Date to Display
                dateToFormat=datetime.strptime(dataTrain[smallestDateIndex]["datetime_start"], '%Y-%m-%dT%H:%M:%S')
                dateToFormatEnd=datetime.strptime(dataTrain[smallestDateIndex]["datetime_end"], '%Y-%m-%dT%H:%M:%S')
                dateToFormat=dateToFormat.replace(tzinfo=ZoneInfo('Singapore'))
                dateToFormatEnd=dateToFormatEnd.replace(tzinfo=ZoneInfo('Singapore'))
                # Format reply
                reply="*"+dataTrain[smallestDateIndex]["title"]+"*\n"+"📍: "+dataTrain[smallestDateIndex]["location"]+"\n"+"📅:"+dateToFormat.strftime(" %d %b %Y, %a").replace(' 0', ' ')+"\n"+"🕓:"+dateToFormat.strftime(" %I:%M%p -").replace(' 0', ' ') + dateToFormatEnd.strftime(" %I:%M%p").replace(' 0', ' ')
                if dataTrain[smallestDateIndex]["Note"]!="Nil":
                    reply=reply+"\n"+"📝: "+dataTrain[smallestDateIndex]["Note"]
                if dataTrain[smallestDateIndex]["location"]=="Zoom":
                    reply=reply+"\n"+"Zoom Link: "+dataDets["zoomlink"]
                if dataTrain[smallestDateIndex]["title"]=="NDP Training":
                    reply=reply+"\n\n"+"Attire: "
                    for i in range(0, len(dataDets["training_attire"])):
                        reply=reply+"\n    "+"- "+dataDets["training_attire"][i]
                    if dataTrain[smallestDateIndex]["location"]=="Keat Hong Camp":
                        reply=reply+"\n"+"Things to Bring: "
                        for i in range(0, len(dataDets["training_bring"])):
                            reply=reply+"\n    "+str(i+1)+") "+dataDets["training_bring"][i]
                logging.info(context.user_data["participantCode"]+': Successfully answered question')
                update.message.reply_text(reply, parse_mode='Markdown')
            else:
                logging.error(context.user_data["participantCode"]+': Failed to get DB data')
                update.message.reply_text("Unable to get next training details. Please try again later or type /start to reset")

        elif update.message.text=="Last updated?":
            if update.message.from_user.username==None:
                logging.info('Question asked by '+update.message.from_user.first_name+': Last updated?')
            else:
                logging.info('Question asked by '+update.message.from_user.first_name+' ('+username+') '+': Last updated?')
            response=requests.get(urlDets, headers=headers)
            if response.status_code == 200:
                data = response.text
                parse_json = json.loads(data)
                logging.info(context.user_data["participantCode"]+': Successfully answered question')
                update.message.reply_text("The training schedule for the bot was last updated on: "+parse_json["lastupdate"])
            else:
                logging.error(context.user_data["participantCode"]+': Failed to get DB data')
                update.message.reply_text("Unable to get training schedule last updated details. Please try again later or type /start to reset")

        elif update.message.text=="Zoom link?":
            if update.message.from_user.username==None:
                logging.info('Question asked by '+update.message.from_user.first_name+': Zoom link?')
            else:
                logging.info('Question asked by '+update.message.from_user.first_name+' ('+username+') '+': Zoom link?')
            response=requests.get(urlDets, headers=headers)
            if response.status_code == 200:
                data = response.text
                parse_json = json.loads(data)
                logging.info(context.user_data["participantCode"]+': Successfully answered question')
                update.message.reply_text("Zoom Link: "+parse_json["zoomlink"])
            else:
                logging.error(context.user_data["participantCode"]+': Failed to get DB data')
                update.message.reply_text("Unable to get zoom link. Please try again later or type /start to reset")

        elif update.message.text=="Countdown":
            if update.message.from_user.username==None:
                logging.info('Question asked by '+update.message.from_user.first_name+': Countdown')
            else:
                logging.info('Question asked by '+update.message.from_user.first_name+' ('+username+') '+': Countdown')
            # Find next NDP activity
            responseTraining=requests.get(urlTrainings, headers=headers)
            if responseTraining.status_code == 200:
                data = responseTraining.text
                dataTrain = json.loads(data)
                today = datetime.now(ZoneInfo('Singapore'))
                daysdiff=""
                smallestDateIndex=""
                i=0
                for item in dataTrain:
                    if item["datetime_end"]!="TBA":
                        datetimeInterator=datetime.strptime(item["datetime_end"], '%Y-%m-%dT%H:%M:%S')
                        datetimeInterator=datetimeInterator.replace(tzinfo=ZoneInfo('Singapore'))
                        if datetimeInterator > today:
                            difftemp=datetimeInterator-today
                            if daysdiff == "" or difftemp < daysdiff:
                                smallestDateIndex=i
                                daysdiff=difftemp
                    i=i+1
                dateToFormat=datetime.strptime(dataTrain[smallestDateIndex]["datetime_start"], '%Y-%m-%dT%H:%M:%S')
                dateToFormat=dateToFormat.replace(tzinfo=ZoneInfo('Singapore'))
                countdownToNext=dateToFormat-today
                seconds = countdownToNext.total_seconds()
                hours = str(seconds // 3600 % 24).replace(".0","")
                minutes = str((seconds % 3600) // 60).replace(".0","")
                seconds = str(math.floor(seconds % 60))
                if countdownToNext.days==1:
                    dayStr="Day"
                else:
                    dayStr="Days"
                countdownToNextStr=str(countdownToNext.days)+" "+dayStr+", "+hours+"h "+minutes+"m "+seconds+"s"
                NDPDate=datetime(2022, 9, 9)
                NDPDate=NDPDate.replace(tzinfo=ZoneInfo('Singapore'))
                countdownToNDP=NDPDate-today
                seconds = countdownToNDP.total_seconds()
                hours = str(seconds // 3600 % 24).replace(".0","")
                minutes = str((seconds % 3600) // 60).replace(".0","")
                seconds = str(math.floor(seconds % 60))
                if countdownToNDP.days==1:
                    dayStr="Day"
                else:
                    dayStr="Days"
                countdownToNDPStr=str(countdownToNDP.days)+" "+dayStr+", "+hours+"h "+minutes+"m "+seconds+"s"
                logging.info(context.user_data["participantCode"]+': Successfully answered question')
                update.message.reply_text('🎉 *Countdown* 🎉\nNext NDP activity: '+countdownToNextStr+'\nNDP 2022: '+countdownToNDPStr, parse_mode='Markdown')
            else:
                logging.error(context.user_data["participantCode"]+': Failed to get DB data')
                update.message.reply_text("Unable to get countdown. Please try again later or type /start to reset")

        elif update.message.text=="Daily encouragement":
            if update.message.from_user.username==None:
                logging.info('Question asked by '+update.message.from_user.first_name+': Daily encouragement')
            else:
                logging.info('Question asked by '+update.message.from_user.first_name+' ('+username+') '+': Daily encouragement')
            link="https://www.sokaglobal.org/resources/daily-encouragement/"
            today = datetime.now(ZoneInfo('Singapore'))
            month=today.strftime("%B").lower()
            link = link + month + "-" + str(today.day) + ".html"
            logging.info(context.user_data["participantCode"]+': Successfully answered question')
            update.message.reply_text(link)  
        else:
            update.message.reply_text('Please select a valid question or type /help')
    else:
        update.message.reply_text('Please type /start first')

#/feedback handler
def feedback(update, context):
    context.user_data["cancelCmd"]="feedback"
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
    if update.message.text !="Next NDP activity?" and  update.message.text !="Zoom link?" and update.message.text != "Countdown" and update.message.text !="Daily encouragement" and update.message.text !="Last updated?": 
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
                url=baseurl+'feedback/'+partCode+'/'
            else:
                partCode=""
                url=baseurl+'feedback/nil/'
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
                context.user_data.pop('cancelCmd', None)
                return ConversationHandler.END
            else:
                if update.message.from_user.username==None:
                    logging.info(update.message.from_user.first_name+' failed to submit feedback')
                else:
                    logging.info(update.message.from_user.first_name+' ('+username+') '+'failed to submit feedback')
                update.message.reply_text("Failed to submit feedback. Please try again later")
                context.user_data.pop('cancelCmd', None)
                return ConversationHandler.END
        else:
            update.message.reply_text('Feedback is too long. It should be less than 500 characters. The submitted feedback was '+str(lengthOfFeedback)+' characters long. Please try again')
            return FIRST_STEP
    else:
        update.message.reply_text('Feedback cannot be one of the questions that NamjaNinja can help you with. Type /cancel if you want to ask a question instead')
        return FIRST_STEP

#/cancel handler
def cancel(update, context):
    if update.message.from_user.username==None:
        username=""
        logging.info('Command issued by '+update.message.from_user.first_name+': cancel')
    else:
        username=update.message.from_user.username
        logging.info('Command issued by '+update.message.from_user.first_name+' ('+username+') '+': cancel')
    if context.user_data["cancelCmd"]=="feedback":
        update.message.reply_text("Cancelled feedback submission")
    elif context.user_data["cancelCmd"]=="login":
        context.user_data.pop('loginTries', None)
        update.message.reply_text("Cancelled process")
    else:
        update.message.reply_text("Cancelled process")
    context.user_data.pop('cancelCmd', None)
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
    updater = Updater(TOKEN, use_context=True)

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
    dp.add_handler(CommandHandler("share", share))

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
    # updater.start_polling()
    PORT = int(os.environ.get("PORT", "8443"))
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN,
                          webhook_url="https://namjaninjabot.herokuapp.com/" + TOKEN)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()