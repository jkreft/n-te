# coding=utf-8

from telegram.ext import CommandHandler, MessageHandler, Filters, Updater
from telegram.parsemode import ParseMode as ParseMode
import telegram
import time
import json
import os
from datetime import datetime
import locale
import numpy as np
from pyowm import OWM, timeutils #Weather API



locale.setlocale(locale.LC_TIME, ('de', 'UTF-8'))
workdir = os.getcwd() + '/'

with open(workdir + 'auth.json') as json_data:
    d = json.load(json_data)
    myname = d['name']
    token = d['telegram-key']


### Full data logging (work in progress ...) ###

class data:
    def __init__(self, name, directory=None):
        self.name = name
        if not directory:
            directory = 'bigdata/'
        if not os.path.exists(directory):
            os.mkdir(directory)
        self.dir = directory

    def make(self, entry, entryname=None):
        dt = str(datetime.now()).replace(' ', '_').replace('.', '').replace(':', '').replace('-', '')
        if not entryname:
            entryname = dt + '_entry'
        else:
            entryname = dt + '_' + entryname
        with open(self.dir + entryname + '.json') as entryfile:
            json.dump(entry, entryfile)

bigdata = data('bigdata', directory=workdir+'bigdata/')


### Conversation logging ###

if not os.path.exists(workdir + 'conlogs/'):
    os.mkdir(workdir + 'conlogs/')
dt = str(datetime.now())
dtfn = dt.replace('-', '')[0:8]
conlogpath = workdir + 'conlogs/' + dtfn + '_conlog_' + myname + '.log'
if not os.path.exists(conlogpath):
    with open(conlogpath, 'w') as conlogfile:
        conlogfile.write('Conversation log of ' + myname + ' (started ' + dt + ')\n')

def conlog(who, logentry):
    with open(conlogpath, 'a') as conlogfile:
        conlogfile.write(who + ': ' + logentry + '  -  (' + str(datetime.now()) + ')\n')


### Wetter ###

class weatherinfo:
    def __init__(self, name):
        self.name = name

owmkey = '04f9cff3a5fbb8c457e31444bae05328'
owm = OWM(API_key=owmkey, language='de') #initialize the Weather API

'''
    w = weatherinfo('w')
    w.object = obs.get_weather() #create the object Weather as w
    w.location = obs.get_location() #create a location related to our already created weather object And send the parameters
    w.status = str(w.object.get_detailed_status())
    w.placename = str(w.location.get_name())
    w.time = str(w.object.get_reference_time(timeformat='iso'))
    w.temperature = str(w.object.get_temperature('celsius').get('temp'))
    return w
'''

def get_weather_forecast(place):
    fc = owm.daily_forecast(place, limit=4)
    today = fc.get_weather_at(timeutils._timedelta_days(0))
    tomorrow = fc.get_weather_at(timeutils._timedelta_days(1))
    dayafter = fc.get_weather_at(timeutils._timedelta_days(2))
    return today, tomorrow, dayafter



# Compose a weather response message
gettingweatherstep = 0
def weather_message(update):
    #location = [update.message.location.latitude, update.message.location.longitude]
    location = 'Heidelberg, DE'
    today, tomorrow, dayafter = get_weather_forecast(location)
    messagetext = 'Das Wetter in ' + location +\
                  ':\n  Heute:\n    Temperatur ' + str(today.get_temperature('celsius').get('day')) +\
                  '\n    Status: ' + str(today.get_detailed_status()) + '\n  Morgen:\n    Temperatur: ' +\
                  str(tomorrow.get_temperature('celsius').get('day')) +\
                  '\n    Status: ' + str(tomorrow.get_detailed_status()) + '\n Übermorgen:\n    Temperatur: ' +\
                  str(dayafter.get_temperature('celsius').get('day')) +\
                  '\n    Status: ' + str(dayafter.get_detailed_status())
    print(messagetext)
    return messagetext

weather_message('lala')

####### TELEGRAM BOT #######


  ##### Define telegram bot (updater and dispatcher Objects, Commands and command handlers) #####



updater = Updater(token=token)
dispatcher = updater.dispatcher

    ### Admin Commands and changing Entes behaviour ###

behaviourmatchstep = 0
newmatch = {}
def behaviour(bot, update, args=None):
    global behaviourmatchstep
    global newmatch

    if update.message.from_user.username == 'phaetjay':

        if behaviourmatchstep == 3:
            weight = int(args[0])
            print(weight)
            newmatch['weight'] = weight
            bot.sendMessage(chat_id=update.message.chat_id, text='OK, weight is: ' + str(weight))
            behaviourmatchstep = 0

            # Add new match
            wordmatch.append(newmatch)
            store_behaviour(wordmatch, 'wordmatch')

            bot.sendMessage(chat_id=update.message.chat_id, text='Successfully added: \n' + str(newmatch))
            return None

        if behaviourmatchstep == 2:
            answers = ' '.join(args).split('!!!')
            print(answers)
            newmatch['answers'] = answers
            bot.sendMessage(chat_id=update.message.chat_id, text='OK, answers are: ' + '\n  '.join(answers) + '\n*Now the weight:*', parse_mode=ParseMode.MARKDOWN)
            behaviourmatchstep = 3

        if behaviourmatchstep == 1:
            print(args)
            keywords = ' '.join(args).split('!!!')
            print(keywords)
            newmatch['keywords'] = keywords
            bot.sendMessage(chat_id=update.message.chat_id, text='OK, keywords are: ' + '\n  '.join(keywords) + '\n*Now the answers:*', parse_mode=ParseMode.MARKDOWN)
            behaviourmatchstep = 2

        if behaviourmatchstep == 0:
            print('Command: ' + update.message.text)
            bot.send_message(chat_id=update.message.chat_id, text='Yes Jay.', parse_mode=ParseMode.MARKDOWN)
            print(args)
            if not (len(args) > 0):
                bot.send_message(chat_id=update.message.chat_id, text='What do you wish?', parse_mode=ParseMode.MARKDOWN)
            else:
                if args[0] == 'match':
                    bot.send_message(chat_id=update.message.chat_id, text='I understand.', parse_mode=ParseMode.MARKDOWN)
                    if (len(args) == 3):
                        newmatch = {'keywords' : [args[1]], 'answers' : [args[2]], 'weight' : 1}
                    elif (len(args) == 4):
                        newmatch = {'keywords': [args[1]], 'answers': [args[2]], 'weight' : int(args[3])}
                    else:
                        bot.sendMessage(chat_id=update.message.chat_id, text='Please enter the new match you want me to learn as a strings ...\n*First the keywords:*', parse_mode=ParseMode.MARKDOWN)
                        behaviourmatchstep = 1
                        return None

                    # Add new match
                    wordmatch.append(newmatch)
                    store_behaviour(wordmatch, 'wordmatch')

                    bot.sendMessage(chat_id=update.message.chat_id, text='Successfully added: \n' + str(newmatch))
                    return None


behaviour_handler = CommandHandler('behaviour', behaviour, pass_args=True)
dispatcher.add_handler(behaviour_handler)


    ### Other command handlers ###

def start(bot, update):
    #bot.send_message(chat_id=update.message.chat_id, text="Quack, ich bin Ente!")
    return None

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

def license(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Welcome!\nThis bot is a program which is available under the GPL-3.0 license at [https://github.com/phaetjay/physical_ente](https://github.com/phaetjay/physical_ente)", parse_mode=ParseMode.MARKDOWN)

license_handler = CommandHandler('license', license)
dispatcher.add_handler(license_handler)

def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="I'm sorry Dave, I'm afraid I can't do that.")

unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)

def echo(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="You said: " + str(update.message.text))

# To start bot: Run updater.start_polling()
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

def load_behaviour(name):
    if not os.path.exists(workdir + 'behaviour/'):
        os.mkdir(workdir + 'behaviour/')
    if not os.path.exists(workdir + 'behaviour/' + name + '.json'):
        with open(workdir + 'behaviour/' + name + '.json', 'w') as behaviourfile:
            json.dump(None, behaviourfile)
    with open(workdir + 'behaviour/' + name + '.json', 'r') as behaviourfile:
        output = json.load(behaviourfile)
    return output

def store_behaviour(dictionary, name):
    with open(workdir + 'behaviour/' + name + '.json', 'w') as behaviourfile:
        json.dump(dictionary, behaviourfile)

def fallback(bot, update):
    fallback = 'Öööh ... äääähm ... hmmm'
    bot.send_message(chat_id=update.message.chat_id, text=fallback)

def in_(text, keywords):
    return any(k.lower() in text for k in keywords)

def shuffle(answerlist):
    lottery = np.random.randint(0, len(answerlist))
    print(lottery)
    return answerlist[lottery]

def match_answer(text):
    matches = list()
    for pair in wordmatch:
        if in_(text, pair['keywords']):
            matches.append(pair)
    highest = 0
    bestmatch = None
    for match in matches:
        if match['weight'] > highest:
            bestmatch = match
            highest = match['weight']
    return shuffle(bestmatch['answers'])


def check_actions(bot, update):
    answer = None
    text = update.message.text

    #if in_(text, ['datum', 'wievielt', 'welcher tag', 'heute', 'wochentag']):
    #    answer = 'Heute ist ' + str(datetime.today().strftime('%A der %d.%m.%Y')) + ' QUACK!'

    #if in_(text, ['wetter', 'regen', 'regnen', 'schön sein', 'schön ist', 'morgen gut', 'sonne']):
    #    answer = weather_message('Heidelberg')


    return answer


def parse_text_message(bot, update):
    response = None
    text = update.message.text
    print('they:', text)
    conlog('they', text)

    action = check_actions(bot, update)
    response = action
    if not action:
        answer = match_answer(text)
        response = answer

    if response:
        print('  me:', response)
        conlog('me', response)
        bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode=ParseMode.MARKDOWN)
    return response


def receiver(bot, update):
    #bigdata.make(update, entryname='update')
    if update.message.text:
        textresponse = parse_text_message(bot, update)
        if not textresponse:
            print('I do not know what to say!')


wordmatch = load_behaviour('wordmatch')
receiver_handler = MessageHandler(Filters.text, receiver)
dispatcher.add_handler(receiver_handler)


updater.start_polling()
updater.idle()

