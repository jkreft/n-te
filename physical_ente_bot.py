# coding=utf-8

from telegram.ext import CommandHandler, MessageHandler, Filters, Updater
from telegram.parsemode import ParseMode as ParseMode
import json
import os
from datetime import datetime
import locale
import numpy as np
from pyowm import OWM #Weather API



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


### Weather ###

owmkey = '04f9cff3a5fbb8c457e31444bae05328'
owm = OWM(owmkey) #initialize the Weather API
def get_weather(update, location=None):
    class weatherinfo:
        def __init__(self, name):
            self.name = name
    if location is 'coords':
        latitude = update.message.location.latitude
        longitude = update.message.location.longitude
        obs = owm.weather_at_coords(latitude, longitude)
    elif location is 'place':
        #inputplace = update.message.text
        place = 'Heidelberg, DE'
        obs = owm.weather_at_place(place)
    else:
        return None
    w = weatherinfo('w')
    w.object = obs.get_weather() #create the object Weather as w
    print(w.object) # <Weather - reference time=2013-12-18 09:20, status=Clouds>
    w.location = obs.get_location() #create a location related to our already created weather object And send the parameters
    w.status = str(w.object.get_detailed_status())
    w.placename = str(w.location.get_name())
    w.time = str(w.object.get_reference_time(timeformat='iso'))
    w.temperature = str(w.object.get_temperature('celsius').get('temp'))
    return w

we = get_weather('test', location='place')
print(we.placename)

def weather_message(w):
    messagetext = 'Das Wetter'
    return messagetext


##### TELEGRAM BOT #####

### Define telegram bot (updater, dispatcher) ###

updater = Updater(token=token)
dispatcher = updater.dispatcher


### Command Handlers ###

def start(bot, update):
    #bot.send_message(chat_id=update.message.chat_id, text="Quak, ich bin Ente!")
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

# To start bot: Run updater.start_polling()
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

def in_(text, keywords):
    return any(k in text for k in keywords)

def shuffle(answerlist):
    lottery = np.random.randint(0, len(answerlist))
    print(lottery)
    return answerlist[lottery]

def original_ente(bot, update):
    answer = False
    text = update.message.text.lower()

    if in_(text, ['ente']):
        answer = "*QUACK!*"
    elif in_(text, ['.*f+o+s+s+.*']):
        answer = "*FOOOOOOOSSSS <3!*"
    elif in_(text, ['turmbraeu', "turmbräu", "git", "love"]):
        answer = "*<3*"
    elif in_(text, ["svn", "subversion"]):
        answer = "*QUAAAAACKKKK😡!!*"
    elif in_(text, ["bread", "brot"]):
        answer = "Mmhhh"

    if answer:
        bot.send_message(chat_id=update.message.chat_id, text=answer, parse_mode=ParseMode.MARKDOWN)
    return answer

def hannes_ente(bot, update):
    answer = False
    text = update.message.text.lower()

    if in_(text, ['kompetenz', 'kompetent']):
        answer = shuffle(['Quack quack, Kompetenz!', 'Hihi, Kompetenz ... quack ...', 'QUACK! Hast du Kompetenz gesagt? Haha quack'])
    if in_(text, ['datum', 'wievielt', 'welcher tag', 'heute']):
        answer = 'Heute ist ' + str(datetime.today().strftime('%A der %d.%m.%Y')) + ' QUACK!'
    if in_(text, ['bier', 'beer']):
        answer = shuffle(['Prost!', '🍺', '🍻'])
    if in_(text, ['kuchen', 'cake', 'torte']):
        answer = shuffle(['Mhmmmmm Kuuchen!', '🍰', '🎂'])
    if in_(text, ['quack', 'quak']):
        answer = shuffle(['Quack! 🦆  😍', 'Quack?', 'Quack quack quack quack quack ... *QUACK!*', 'Hä? 🦆'])

    if answer:
        bot.send_message(chat_id=update.message.chat_id, text=answer, parse_mode=ParseMode.MARKDOWN)
    return answer


def fallback(bot, update):
    fallback = 'Öööh ... äääähm ... hmmm'
    bot.send_message(chat_id=update.message.chat_id, text=fallback)

def receiver(bot, update):
    #bigdata.make(update, entryname='update')
    text = update.message.text
    conlog('they', text)
    hannes = hannes_ente(bot, update)
    if hannes:
        print(hannes)
        conlog('me', hannes)
    else:
        original = original_ente(bot, update)
        if original:
            print(original)
            conlog('me', original)


receiver_handler = MessageHandler(Filters.text, receiver)
dispatcher.add_handler(receiver_handler)


updater.start_polling()

