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

from telegram import ReplyKeyboardMarkup, KeyboardButton, ChatAction
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
    context.bot.send_chat_action(chat_id=update.message.chat.id, action=ChatAction.TYPING, timeout=None)
    #reset
    context.user_data.pop('participantCode', None)
    context.user_data.pop('token', None)
    context.user_data["cancelCmd"]="login"
    context.user_data["loginTriesNonText"]=0
    update.message.reply_text("What's your participant code:")
    logging.info('User attempting login: '+update.message.from_user.first_name+ ' ('+str(update.message.from_user.id)+')')
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
    context.bot.send_chat_action(chat_id=update.message.chat.id, action=ChatAction.TYPING, timeout=None)
    if update.message.text:
        partCode=update.message.text.capitalize().strip()
        telegramid=str(update.message.from_user.id)
        url = baseurl+'user/'+partCode+'/'+telegramid+'/'
        data = {
            'telegramId':telegramid,
            'participantCode':partCode,
            'username':username,
            'firstname': update.message.from_user.first_name,
            'lastname': lastname
        }
        response = requests.post(url, data = data)
        if response.status_code == 200:
            data = response.text
            parse_json = json.loads(data)
            if parse_json['token']!="":
                #successful login
                #got user's session token and participant code. enable user to use the service
                context.user_data["token"] = parse_json['token']
                context.user_data["participantCode"] = partCode
                #show questions
                keyboard = [
                    [KeyboardButton("Next NDP activity?")],
                    [KeyboardButton("Show all NDP activities")],
                    [KeyboardButton("Zoom link?")],
                    [KeyboardButton("Countdown")],
                    [KeyboardButton("Daily encouragement")],
                    [KeyboardButton("Last updated?")],
                ]
                reply_markup = ReplyKeyboardMarkup(keyboard)
                context.user_data.pop('cancelCmd', None)
                context.user_data.pop('loginTriesNonText', None)
                logging.info('Successful login by '+telegramid+' ('+username+", "+ partCode+')')
                update.message.reply_text('Please select your query:', reply_markup=reply_markup)
                return ConversationHandler.END
            else:
                #failed login
                if parse_json['loginAttempts']>=3:
                    update.message.reply_text('You can type /cancel to exit')
                    logging.warning(telegramid+' ('+username+') failed to login '+str(parse_json['loginAttempts'])+' times')
                update.message.reply_text('Invalid participant code. Please try again:')
                return LOGIN_STEP
        elif response.status_code == 423:
            #Account blocked
            logging.info('Blocked account: '+telegramid+' ('+username+", "+ partCode+')')
            update.message.reply_text("Sorry, your account has been blocked from using NamjaNinjaBot due to repeated failed login attempts. Please type /feedback to submit a request for the account to be unblocked if you are a legitimate NDP 2022 SGS participant")
            return ConversationHandler.END
        else:
            #bad requests
            context.user_data.pop('cancelCmd', None)
            context.user_data.pop('loginTriesNonText', None)
            logging.error('Unsuccessful login by '+telegramid+' ('+username+", "+ partCode+')')
            update.message.reply_text('Unable to process request at this time. Please try again later')
            return ConversationHandler.END
    else:
        #Non-text input during login
        if context.user_data["loginTriesNonText"]>=3:
            update.message.reply_text('You can type /cancel to exit')
        context.user_data["loginTriesNonText"]=context.user_data["loginTriesNonText"]+1
        logging.warning(str(update.message.from_user.id)+' ('+username+') gave non-text reply on login')
        update.message.reply_text('Input should be a text message. Please try again')

#/help handler
def help(update, context):
    context.bot.send_chat_action(chat_id=update.message.chat.id, action=ChatAction.TYPING, timeout=None)
    if update.message.from_user.username==None:
        username=""
        logging.info('Command issued by '+update.message.from_user.first_name+' ('+str(update.message.from_user.id)+'): help')
    else:
        username=update.message.from_user.username
        logging.info('Command issued by '+update.message.from_user.first_name+' ('+username+', '+str(update.message.from_user.id)+'): help')
    """Send a message when the command /help is issued."""
    update.message.reply_text('Hi '+update.message.from_user.first_name+'! I am NamjaNinja! I can assist you on your SGS NDP 2022 journey!\n\nSend the following commands to get started:\n/start - Lists all the queries I can help you with\n/about - Learn more about me\n/feedback - Tell me how I can improve\n/help - Describes how to use me\n/share - Share me with your fellow participants')

#/share handler
def share(update, context):
    context.bot.send_chat_action(chat_id=update.message.chat.id, action=ChatAction.TYPING, timeout=None)
    if update.message.from_user.username==None:
        username=""
        logging.info('Command issued by '+update.message.from_user.first_name+' ('+str(update.message.from_user.id)+'): share')
    else:
        username=update.message.from_user.username
        logging.info('Command issued by '+update.message.from_user.first_name+' ('+username+', '+str(update.message.from_user.id)+'): share')
    """Send a message when the command /share is issued."""
    update.message.reply_text('Hello! I am NamjaNinjaBot, a Telegram Bot that can provide training information and encouragement to SGS NDP 2022 participants:\nhttps://t.me/NamjaNinjabot')

#/about handler
def about(update, context):
    context.bot.send_chat_action(chat_id=update.message.chat.id, action=ChatAction.TYPING, timeout=None)
    if update.message.from_user.username==None:
        username=""
        logging.info('Command issued by '+update.message.from_user.first_name+' ('+str(update.message.from_user.id)+'): about')
    else:
        username=update.message.from_user.username
        logging.info('Command issued by '+update.message.from_user.first_name+' ('+username+', '+str(update.message.from_user.id)+'): about')
    """Send a message when the command /about is issued."""
    update.message.reply_text('*About*\nNamjaNinjaBot is a Telegram bot that is aimed at allowing Soka Gakkai Singapore (SGS) NDP 2022 participants to obtain NDP training and meeting details easily and quickly. Participants can also get daily encouragements through the bot\n\n*Disclaimer*\nThis bot was created in good faith by one of the participants to be a handy companion to the participants and should strictly be used for such purposes only. By using NamjaNinjaBot, you agree to the collection of user data that will only be used for NamjaNinjaBot performance monitoring and to ensure that the bot is used for its intended purpose only. Thank you for your understanding', parse_mode='Markdown')

#determine reply after query chosen, ensures participantCode and session token is available
def reply(update, context):
    context.bot.send_chat_action(chat_id=update.message.chat.id, action=ChatAction.TYPING, timeout=None)
    if 'participantCode' in context.user_data and context.user_data["participantCode"]!="" and 'token' in context.user_data and context.user_data["token"]!="":
        if update.message.text:
            if update.message.from_user.username==None:
                username=""
            else:
                username=update.message.from_user.username
            telegramid=str(update.message.from_user.id)
            urlDets = baseurl+'details/'+context.user_data["participantCode"]+'/'+telegramid+"/1/"
            urlTrainings = baseurl+'training/'+context.user_data["participantCode"]+'/'+telegramid+"/1/"
            headers = {
                "token":context.user_data["token"]
            }
            if update.message.text=="Next NDP activity?":
                if update.message.from_user.username==None:
                    logging.info('Question asked by '+update.message.from_user.first_name+' ('+telegramid+'): Next NDP activity?')
                else:
                    logging.info('Question asked by '+update.message.from_user.first_name+' ('+username+', '+telegramid+'): Next NDP activity?')
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
                    ndpInt=""
                    ndpDatetime=""
                    postcelebrationInt=""
                    i=0
                    for item in dataTrain:
                        if re.search("^NDP [0-9][0-9][0-9][0-9] Post Celebration$", item["title"]):
                            postcelebrationInt = i
                        if item["datetime_end"]!="TBA":
                            datetimeInterator=datetime.strptime(item["datetime_end"], '%Y-%m-%dT%H:%M:%S')
                            datetimeInterator=datetimeInterator.replace(tzinfo=ZoneInfo('Singapore'))
                            # If NDP, save details for use later
                            if datetimeInterator.day == 9 and datetimeInterator.month == 8:
                                ndpInt = i
                                ndpDatetime = datetimeInterator
                            if datetimeInterator > today:
                                difftemp=datetimeInterator-today
                                if daysdiff == "" or difftemp < daysdiff:
                                    smallestDateIndex=i
                                    daysdiff=difftemp
                        i=i+1
                    # Check if pass 9 Aug
                    if today > datetimeInterator and data["schedule"][postcelebrationInt]["datetime_end"]=="TBA":
                        reply = "Hope NamjaNinjaBot was useful to you in some way or another. The NDP Post Celebration Details have not been updated or released. This will be updated in due time. See you at the post celebrations and congratulations on completing NDP 2022!"
                        logging.info(context.user_data["participantCode"]+': Successfully answered question')
                        update.message.reply_text(reply, parse_mode='Markdown')
                    # Check if pass post celebrations
                    elif today > datetimeInterator and data["schedule"][postcelebrationInt]["datetime_end"]!="TBA":
                        datetimePostCeleb=datetime.strptime(data["schedule"][postcelebrationInt]["datetime_end"], '%Y-%m-%dT%H:%M:%S')
                        datetimePostCeleb=datetimePostCeleb.replace(tzinfo=ZoneInfo('Singapore'))
                        if today > datetimePostCeleb:
                            reply = "NDP 2022 has come to an end. Thank you for using NamjaNinjaBot and hope it has helped you on this journey. May you continue to achieve more victories in the future! NamjaNinjaBot signing off~"
                            logging.info(context.user_data["participantCode"]+': Successfully answered question')
                            update.message.reply_text(reply, parse_mode='Markdown')
                    else:
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
                        if re.match("^NDP (Training[a-zA-Z1-4]*|[NC][ER] [1-3]|Preview|2022)", dataTrain[smallestDateIndex]["title"]):
                            reply=reply+"\n\n"+"Attire: "
                            for i in range(0, len(dataDets["training_attire"])):
                                reply=reply+"\n    "+"- "+dataDets["training_attire"][i]
                            if dataTrain[smallestDateIndex]["location"]=="Floating Platform" or dataTrain[smallestDateIndex]["location"]=="Senja Soka Centre":
                                reply=reply+"\n"+"Things to Bring: "
                                for i in range(0, len(dataDets["training_bring"])):
                                    reply=reply+"\n    "+str(i+1)+") "+dataDets["training_bring"][i]
                                if re.match("^NDP ([NC][ER] [1-3]|Preview|2022)", dataTrain[smallestDateIndex]["title"]):
                                    reply=reply+"\n    "+str(i+2)+") "+"Costume"
                        logging.info(context.user_data["participantCode"]+': Successfully answered question')
                        update.message.reply_text(reply, parse_mode='Markdown')
                else:
                    logging.error(context.user_data["participantCode"]+': Failed to get DB data')
                    update.message.reply_text("Unable to get next training details. Please try again later or type /start to reset")

            elif update.message.text=="Show all NDP activities":
                if update.message.from_user.username==None:
                    logging.info('Question asked by '+update.message.from_user.first_name+' ('+telegramid+'): Show all NDP activities')
                else:
                    logging.info('Question asked by '+update.message.from_user.first_name+' ('+username+', '+telegramid+'): Show all NDP activities')
                responseTraining=requests.get(urlTrainings, headers=headers)
                if responseTraining.status_code == 200:
                    data = responseTraining.text
                    dataTrain = json.loads(data)

                    today = datetime.now(ZoneInfo('Singapore'))
                    remainingTrain=[]
                    tbaEndTrain=[]
                    for item in dataTrain:
                        if item["datetime_end"]!="TBA":
                            datetimeInterator=datetime.strptime(item["datetime_end"], '%Y-%m-%dT%H:%M:%S')
                            datetimeInterator=datetimeInterator.replace(tzinfo=ZoneInfo('Singapore'))
                            if item["datetime_start"]!="TBA":
                                datetimeStart=datetime.strptime(item["datetime_start"], '%Y-%m-%dT%H:%M:%S')
                                item["startDate"]= datetimeStart
                            elif item["datetime_start"]=="TBA":
                                item["startDate"]= "TBA"
                            if datetimeInterator > today:
                                item["endDate"]= datetimeInterator
                                remainingTrain.append(item)
                        elif item["datetime_end"]=="TBA":
                            tbaEndTrain.append(item)
                    #sort by date for activity with end datetime then add TBA trainings at the back
                    sortedRemainingTrain = sorted(remainingTrain, key=lambda d: d['endDate'])
                    sortedRemainingTrain=sortedRemainingTrain+tbaEndTrain
                    reply="*NDP Activity Schedule*"
                    if len(sortedRemainingTrain)==0:
                        reply="NDP 2022 has come to an end. Thank you for using NamjaNinjaBot and hope it has helped you on this journey. May you continue to achieve more victories in the future! NamjaNinjaBot signing off~"
                    else:
                        # Format reply
                        i=1
                        for activity in sortedRemainingTrain:
                            reply=reply+"\n"+str(i)+") "+activity["title"]+": "
                            if activity["datetime_end"]!="TBA":
                                reply=reply+activity["endDate"].strftime(" %d %b %Y (%a)").replace(' 0', ' ')
                            else:
                                reply=reply + "TBA"
                            if activity["datetime_start"]!="TBA":
                                reply=reply+", "+activity["startDate"].strftime(" %I:%M%p -").replace(' 0', ' ')
                            else:
                                reply=reply+", TBA - "
                            if activity["datetime_end"]!="TBA":
                                reply=reply+activity["endDate"].strftime(" %I:%M%p").replace(' 0', ' ')
                            else:
                                reply=reply+"TBA"
                            reply=reply+" @ "+activity["location"]
                            i=i+1
                        
                    logging.info(context.user_data["participantCode"]+': Successfully answered question')
                    update.message.reply_text(reply, parse_mode='Markdown')
                else:
                    logging.error(context.user_data["participantCode"]+': Failed to get DB data')
                    update.message.reply_text("Unable to get training details. Please try again later or type /start to reset")
                    
            elif update.message.text=="Last updated?":
                #returns when training schedule last updated
                if update.message.from_user.username==None:
                    logging.info('Question asked by '+update.message.from_user.first_name+' ('+telegramid+'): Last updated?')
                else:
                    logging.info('Question asked by '+update.message.from_user.first_name+' ('+username+', '+telegramid+'): Last updated?')
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
                #returns zoom link used for meetings
                if update.message.from_user.username==None:
                    logging.info('Question asked by '+update.message.from_user.first_name+' ('+telegramid+'): Zoom link?')
                else:
                    logging.info('Question asked by '+update.message.from_user.first_name+' ('+username+', '+telegramid+'): Zoom link?')
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
                #returns countdown to next NDP activity and NDP 2022
                if update.message.from_user.username==None:
                    logging.info('Question asked by '+update.message.from_user.first_name+' ('+telegramid+'): Countdown')
                else:
                    logging.info('Question asked by '+update.message.from_user.first_name+' ('+username+', '+telegramid+'): Countdown')
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
                    if countdownToNext>0:
                        seconds = countdownToNext.total_seconds()
                        hours = str(seconds // 3600 % 24).replace(".0","")
                        minutes = str((seconds % 3600) // 60).replace(".0","")
                        seconds = str(math.floor(seconds % 60))
                        if countdownToNext.days==1:
                            dayStr="Day"
                        else:
                            dayStr="Days"
                        countdownToNextStr=str(countdownToNext.days)+" "+dayStr+", "+hours+"h "+minutes+"m "+seconds+"s"
                    else:
                        countdownToNextStr="Countdown has ended"
                    NDPDate=datetime(2022, 8, 9)
                    NDPDate=NDPDate.replace(tzinfo=ZoneInfo('Singapore'))
                    countdownToNDP=NDPDate-today
                    if countdownToNDP>0:
                        seconds = countdownToNDP.total_seconds()
                        hours = str(seconds // 3600 % 24).replace(".0","")
                        minutes = str((seconds % 3600) // 60).replace(".0","")
                        seconds = str(math.floor(seconds % 60))
                        if countdownToNDP.days==1:
                            dayStr="Day"
                        else:
                            dayStr="Days"
                        countdownToNDPStr=str(countdownToNDP.days)+" "+dayStr+", "+hours+"h "+minutes+"m "+seconds+"s"
                    else:
                        countdownToNDPStr="Countdown has ended"
                    logging.info(context.user_data["participantCode"]+': Successfully answered question')
                    update.message.reply_text('🎉 *Countdown* 🎉\nNext NDP activity: '+countdownToNextStr+'\nNDP 2022: '+countdownToNDPStr, parse_mode='Markdown')
                else:
                    logging.error(context.user_data["participantCode"]+': Failed to get DB data')
                    update.message.reply_text("Unable to get countdown. Please try again later or type /start to reset")

            elif update.message.text=="Daily encouragement":
                #returns daily encouragement
                if update.message.from_user.username==None:
                    logging.info('Question asked by '+update.message.from_user.first_name+' ('+telegramid+'): Daily encouragement')
                else:
                    logging.info('Question asked by '+update.message.from_user.first_name+' ('+username+', '+telegramid+'): Daily encouragement')
                link="https://www.sokaglobal.org/resources/daily-encouragement/"
                today = datetime.now(ZoneInfo('Singapore'))
                month=today.strftime("%B").lower()
                link = link + month + "-" + str(today.day) + ".html"
                logging.info(context.user_data["participantCode"]+': Successfully answered question')
                update.message.reply_text(link)  
            else:
                update.message.reply_text('Please select a valid question or type /help')
        else:
            update.message.reply_text('Please select a valid question or type /help')
    else:
        update.message.reply_text('Please type /start first')

#/feedback handler
def feedback(update, context):
    context.bot.send_chat_action(chat_id=update.message.chat.id, action=ChatAction.TYPING, timeout=None)
    context.user_data["cancelCmd"]="feedback"
    context.user_data["feedbackTriesNonText"]=0
    if update.message.from_user.username==None:
        username=""
        logging.info('Command issued by '+update.message.from_user.first_name+' ('+str(update.message.from_user.id)+'): feedback')
    else:
        username=update.message.from_user.username
        logging.info('Command issued by '+update.message.from_user.first_name+' ('+username+', '+str(update.message.from_user.id)+'): feedback')
    """Send a message when the command /feedback is issued."""
    update.message.reply_text('NamjaNinjaBot will listen to all feedback. Please follow the steps to submit one. If you decided to change your mind, just type /cancel')
    update.message.reply_text("Please type your feedback:")
    return FIRST_STEP

#feedback submission
def first_step(update, context):
    context.bot.send_chat_action(chat_id=update.message.chat.id, action=ChatAction.TYPING, timeout=None)
    telegramid=str(update.message.from_user.id)
    if update.message.from_user.last_name==None:
        lastname=""
    else:
        lastname=update.message.from_user.last_name
    if update.message.from_user.username==None:
        username=""
    else:
        username=update.message.from_user.username
    if update.message.text:
        #ensures feedback is not a defined query
        if update.message.text !="Next NDP activity?" and  update.message.text !="Zoom link?" and update.message.text != "Countdown" and update.message.text !="Daily encouragement" and update.message.text !="Last updated?" and update.message.text !="Show all NDP activities": 
            lengthOfFeedback=len(update.message.text)
            #ensures feedback is not too long or short
            if lengthOfFeedback>5:
                if lengthOfFeedback<=500:
                    # if logged in
                    if 'participantCode' in context.user_data and context.user_data["participantCode"]!="":
                        partCode=context.user_data["participantCode"]
                        url=baseurl+'feedback/'+partCode+'/'+telegramid+'/'
                    else:
                        partCode=""
                        url=baseurl+'feedback/nil/'+telegramid+'/'
                    data = {'telegramId':update.message.from_user.id,
                            'participantCode': partCode,
                            'username':username,
                            'firstname': update.message.from_user.first_name,
                            'lastname': lastname,
                            "feedback": update.message.text
                            }
                    #submit feedback
                    response = requests.post(url, data = data)
                    if response.status_code == 201:
                        update.message.reply_text("Thank you for your feedback!")
                        if update.message.from_user.username==None:
                            logging.info(update.message.from_user.first_name+' ('+telegramid+') successfully submitted feedback')
                        else:
                            logging.info(update.message.from_user.first_name+' ('+username+', '+telegramid+') '+'successfully submitted feedback')
                        context.user_data.pop('cancelCmd', None)
                        context.user_data.pop('feedbackTriesNonText', None)
                        return ConversationHandler.END
                    else:
                        if update.message.from_user.username==None:
                            logging.info(update.message.from_user.first_name+' ('+telegramid+') failed to submit feedback')
                        else:
                            logging.info(update.message.from_user.first_name+' ('+username+', '+telegramid+') '+'failed to submit feedback')
                        update.message.reply_text("Failed to submit feedback. Please try again later")
                        context.user_data.pop('cancelCmd', None)
                        context.user_data.pop('feedbackTriesNonText', None)
                        return ConversationHandler.END
                else:
                    update.message.reply_text('Feedback is too long. It should be less than 500 characters. The submitted feedback was '+str(lengthOfFeedback)+' characters long. Please try again')
                    return FIRST_STEP
            else:
                update.message.reply_text('Feedback is too short. More details will allow NamjaNinjaBot to understand the issue. Please try again')
                return FIRST_STEP
        else:
            update.message.reply_text('Feedback cannot be one of the questions that NamjaNinja can help you with. Type /cancel if you want to ask a question instead')
            return FIRST_STEP
    else:
        if context.user_data["feedbackTriesNonText"]>=3:
            update.message.reply_text('You can type /cancel to exit')
        context.user_data["feedbackTriesNonText"]=context.user_data["feedbackTriesNonText"]+1
        logging.info(update.message.from_user.first_name+' ('+username+', '+telegramid+') gave non-text reply on feedback')
        update.message.reply_text('Input should be a text message. Please try again')

#/cancel handler
def cancel(update, context):
    context.bot.send_chat_action(chat_id=update.message.chat.id, action=ChatAction.TYPING, timeout=None)
    if update.message.from_user.username==None:
        username=""
        logging.info('Command issued by '+update.message.from_user.first_name+' ('+str(update.message.from_user.id)+'): cancel')
    else:
        username=update.message.from_user.username
        logging.info('Command issued by '+update.message.from_user.first_name+' ('+username+', '+str(update.message.from_user.id)+'): cancel')
    if context.user_data["cancelCmd"]=="feedback":
        context.user_data.pop('feedbackTriesNonText', None)
        update.message.reply_text("Cancelled feedback submission")
    elif context.user_data["cancelCmd"]=="login":
        context.user_data.pop('loginTriesNonText', None)
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
            LOGIN_STEP: [MessageHandler(~Filters.command, login_step)],
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
            FIRST_STEP: [MessageHandler(~Filters.command, first_step)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dp.add_handler(conversation_handler)

    # on noncommand i.e message - reply the message on Telegram
    dp.add_handler(MessageHandler(~Filters.command, reply))

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