# coding=utf-8

from telegram.ext import CommandHandler, MessageHandler, Filters, Updater
from telegram.parsemode import ParseMode as ParseMode
import telegram
import time
import json
import os
import datetime
import locale
import atexit
import numpy as np
from pyowm import OWM, timeutils #Openweathermap Weather API
import xml.etree.ElementTree as ET #Reading Mensa xml-file
import urllib.request
import ente.behaviour


### Full data logging (work in progress ...) ###

def exit_handler():
    print('Ente out.')
    bigdata.store()

class data:
    def __init__(self, name, filepath=None):
        self.name = name
        if not filepath:
            filepath = workdir + 'bigdata/bigdata_' + myname + '.json'
        self.filepath = filepath
        self.dictionary = {}
        if os.path.exists(filepath):
            with open(filepath, 'r') as bigdatafile:
                self.dictionary = json.load(bigdatafile)
        else:
            if not os.path.exists(workdir + 'bigdata'):
                os.mkdir(workdir +  'bigdata')
            with open(filepath, 'w') as bigdatafile:
                json.dump({}, bigdatafile)
    def store(self):
        with open(self.filepath, 'w') as bigdatafile:
            json.dump(self.dictionary, bigdatafile)
    def add(self, entry, type='entries'):
        if not type in self.dictionary:
            self.dictionary[type] = []
        if type == 'updates':
            update = dict()
            update['message'] = entry.message.text
            self.dictionary[type].append(update)


### Conversation logging ###

def start_conlog():
    if not os.path.exists(workdir + 'conlogs/'):
        os.mkdir(workdir + 'conlogs/')
    dt = str(datetime.datetime.now())
    dtfn = dt.replace('-', '')[0:8]
    conlogpath = workdir + 'conlogs/' + dtfn + '_conlog_' + myname + '.log'
    if not os.path.exists(conlogpath):
        with open(conlogpath, 'w') as conlogfile:
            conlogfile.write('Conversation log of ' + myname + ' (started ' + dt + ')\n')
    return conlogpath

def conlog(who, logentry):
    global conlogpath
    with open(conlogpath, 'a') as conlogfile:
        conlogfile.write(who + ': ' + logentry + '  -  (' + str(datetime.datetime.now()) + ')\n')


### Wetter ###

# Openweathermap Weather codes and corressponding emojis
thunderstorm = u'\U0001F4A8'    # Code: 200's, 900, 901, 902, 905
drizzle = u'\U0001F4A7'         # Code: 300's
rain = u'\U00002614'            # Code: 500's
snowflake = u'\U00002744'       # Code: 600's snowflake
snowman = u'\U000026C4'         # Code: 600's snowman, 903, 906
atmosphere = u'\U0001F301'      # Code: 700's foogy
clearSky = u'\U00002600'        # Code: 800 clear sky
fewClouds = u'\U000026C5'       # Code: 801 sun behind clouds
clouds = u'\U00002601'          # Code: 802-803-804 clouds general
hot = u'\U0001F525'             # Code: 904
defaultEmoji = u'\U0001F300'    # default emojis

def getEmoji(weatherID):
    if weatherID:
        if str(weatherID)[0] == '2' or weatherID == 900 or weatherID==901 or weatherID==902 or weatherID==905:
            return thunderstorm
        elif str(weatherID)[0] == '3':
            return drizzle
        elif str(weatherID)[0] == '5':
            return rain
        elif str(weatherID)[0] == '6' or weatherID==903 or weatherID== 906:
            return snowflake + ' ' + snowman
        elif str(weatherID)[0] == '7':
            return atmosphere
        elif weatherID == 800:
            return clearSky
        elif weatherID == 801:
            return fewClouds
        elif weatherID==802 or weatherID==803 or weatherID==803:
            return clouds
        elif weatherID == 904:
            return hot
        else:
            return defaultEmoji    # Default emoji

    else:
        return defaultEmoji   # Default emoji

class weatherinfo:
    def __init__(self, name):
        self.name = name

def get_weather_forecast(place):
    fc = owm.daily_forecast(place, limit=4)
    today = fc.get_weather_at(timeutils._timedelta_days(0))
    tomorrow = fc.get_weather_at(timeutils._timedelta_days(1))
    dayafter = fc.get_weather_at(timeutils._timedelta_days(2))
    return today, tomorrow, dayafter

# Compose a weather response message
def weather_message(update):
    try:
        #location = [update.message.location.latitude, update.message.location.longitude]
        location = 'Heidelberg, DE'
        today, tomorrow, dayafter = get_weather_forecast(location)
        messagetext = 'Das Wetter in ' + location +\
                      ':\n  Heute:\n    Temperatur: ' + str(round(today.get_temperature('celsius').get('day'), 0))[:-2] + ' °C' +\
                      '\n    Status: ' + str(today.get_detailed_status()) + ' ' + getEmoji(today.get_weather_code()) + '\n  Morgen:\n    Temperatur: ' +\
                      str(round(tomorrow.get_temperature('celsius').get('day'), 0))[:-2] + ' °C' +\
                      '\n    Status: ' + str(tomorrow.get_detailed_status()) + ' ' + getEmoji(tomorrow.get_weather_code()) + '\n Übermorgen:\n    Temperatur: ' +\
                      str(round(dayafter.get_temperature('celsius').get('day'), 0))[:-2] + ' °C' +\
                      '\n    Status: ' + str(dayafter.get_detailed_status()) + ' ' + getEmoji(dayafter.get_weather_code())
        return messagetext

    except:
        return 'Wetter geht grade nicht *Quack*'


### Mensa ###

def mensa_message(tag):
    try:
        if tag == 'heute':
            datum = datetime.date.today()
        if tag == 'morgen':
            datum = datetime.date.today() + datetime.timedelta(days=1)
        urllib.request.urlretrieve(mensaurl, workdir + 'mensa/mensa.xml')
        with open(workdir + 'mensa/mensa.xml', 'r') as mensafile:
            mensastring = mensafile.read()
            mensaxml = ET.fromstring(mensastring)
        days = mensaxml.findall('.//{http://openmensa.org/open-mensa-v2}day')
        for day in days:
            if day.attrib['date'] == datum.strftime("%Y-%m-%d"):
                speiseplan = day
                print(day)
        if speiseplan.findall('./{http://openmensa.org/open-mensa-v2}closed'):
            mensamessage = tag.capitalize() + ' (' + datum.strftime("%d.%m.") + ') gibts *kein Essen!* Quack'
            return mensamessage
        else:
            mensamessage = ['*Speiseplan* Mensa INF für ' + tag + ' (' + datum.strftime("%d.%m.") + '):\n']
            for kategorie in speiseplan.findall('./{http://openmensa.org/open-mensa-v2}category'):
                if not (kategorie.attrib['name'] == 'B') and not kategorie.attrib['name'] == 'A+B':
                    mensamessage.append('\nBei *' + kategorie.attrib['name'] + "* gibt's:\n")
                    for essen in kategorie.findall('./{http://openmensa.org/open-mensa-v2}meal'):
                        if kategorie.attrib['name'] == 'D':
                            gerichtD = essen[0].text.split(',\n')
                            for komponente in gerichtD:
                                if in_(komponente, ['Tagessuppe', 'Salat der Saison']):
                                    gerichtD.remove(komponente)
                            mensamessage.append(', '.join(gerichtD) + '\n')
                        if kategorie.attrib['name'] == 'E':
                            gericht = ' '.join(essen[0].text.split())
                            print(gericht)
                            if not in_(gericht, ['Tagessuppe', 'Salat der Saison']):
                                mensamessage.append(gericht + '\n')
            return ' '.join(mensamessage)
    except:
        return 'Mensa geht grade nicht *Quack*'


### Musixmatch ###

from musixmatch import Musixmatch
musixmatcher = Musixmatch('82adb4026cc5a4c29babc2818c0713e2')

def get_lyrics(info):
    try:
        trackobject = musixmatcher.matcher_track_get(info, info)
        songname = trackobject['message']['body']['track']['track_name']
        artist =  trackobject['message']['body']['track']['artist_name']
        album = trackobject['message']['body']['track']['album_name']
        try:
            lyricsobject = musixmatcher.track_lyrics_get(trackobject['message']['body']['track']['track_id'])
            print(lyricsobject)
            lyrics = '\n'.join(lyricsobject['message']['body']['lyrics']['lyrics_body'].split('\n')[:-2])
            print(lyrics)
            output = 'Lyrics zu ' + songname + ' von ' + artist + ':\n \n' + lyrics
            return output
        except:
            output = 'Leider kann ich zu ' + songname + ' von ' + artist + ' keine Lyrics finden.'
            return output
    except:
        return None

### Sag mal, Ente ###

import rubberduck
from mtranslate import translate

def ok_ente(bot, update, trigger=None):
    response = None
    text = update.message.text
    if not trigger:
        trigger = 'ok ente'
    position = text.lower().find(trigger) + len(trigger)
    query = text[position:]

    if in_(text, ['lyrics']):
        lyricsinfo = query[query.find('lyrics') + 5:]
        response = get_lyrics(lyricsinfo)

    elif in_(text, [' such']):
        triggerindex = [idx for idx, s in enumerate(text.split(' ')) if 'such' in s][0]
        searchterm = query[triggerindex + 4:]
        try:
            searchtermEN = translate(searchterm, 'en')
        except:
            return 'Ich kann so leider keine Antwort finden. Du könntest versuchen, die Frage auf Englisch zu stellen.'
        if not searchterm:
            return 'Wie kann ich helfen?'

        print('Trying DuckDuckGo API:', searchtermEN)
        ddg_json = rubberduck.DuckDuckGoJSON(rubberduck.search(searchtermEN, bang=0, no_redirect=1, skip_disambig=1))
        results_priority = [ddg_json.answer, ddg_json.abstract, None]
        for result in results_priority:
            if result:
                try:
                    response = translate(result, 'de')
                    response = response + '\nQuelle: [DuckDuckGo.com](https://duckduckgo.com/?q=' + '+'.join(searchtermEN.split()) + ')'
                except:
                    response = 'Antwort leider nur auf Englisch:\n' + result
                break
        if not response:
            print('Trying Wikipedia EN:', searchtermEN)
            bang = 'wikipedia'
            wikiresult = rubberduck.search(searchtermEN, bang=bang, no_redirect=0, skip_disambig=1)
            try:
                responseURL = wikiresult.url
                response = 'Hier kannst du selber auf [Wikipedia](' + responseURL + ') nachschauen *QUACK*'
            except:
                response = 'Habe leider nichts gefunden *Quack*'
    if not response:
        response = 'Ich verstehe leider die Frage nicht *Quack*'
    print(response)

    return response


####### TELEGRAM BOT #######

##### Commands and command handler functions) #####

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Quack, ich bin Ente!")
    return None

def license(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Welcome!\nThis bot is a program which is available under the GPL-3.0 license at [https://github.com/phaetjay/physical_ente](https://github.com/phaetjay/physical_ente)", parse_mode=ParseMode.MARKDOWN)

def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="I'm sorry Dave, I'm afraid I can't do that.")


##### Message (text) handling, generation of reply

def in_(text, keywords):
    return any(k.lower() in text.lower() for k in keywords)

def shuffle(answerlist):
    lottery = np.random.randint(0, len(answerlist))
    return answerlist[lottery]

def match_answer(text):
    matches = list()
    for pair in behaviour.wordmatch:
        if in_(text, pair['keywords']):
            matches.append(pair)
    highest = 0
    bestmatch = None
    for match in matches:
        if match['weight'] > highest:
            bestmatch = match
            highest = match['weight']
    return shuffle(bestmatch['answers'])

def check_user(bot, update):
    global users
    user = update.message.from_user
    text = update.message.text
    if not user.username in users:
        users[user.username] = {'counter': 0}

    # Punkt punkt punkt
    lastthree = text.replace(" ", "")[-3:]
    if user.username == 'digital_ostrich' and lastthree == '...':
        bot.send_message(chat_id=update.message.chat_id,
                         text=shuffle(['Schon wieder diese drei Punkte ...',
                                       'Jonah, ich wundere mich doch sehr über deinen Tonfall ...',
                                       'Was ist denn das schon wieder für ein passiv-aggressiver Ton, Jonah?']),
                         reply_to_message_id=update.message.message_id, parse_mode=ParseMode.MARKDOWN)
        return 'lastthree'

    # Nerv nicht
    if in_(text, ['ente']):
        users[user.username]['counter'] += 1
    else:
        users[user.username]['counter'] = 0
    if users[user.username]['counter'] >= 4:
        bot.send_message(chat_id=update.message.chat_id,
                         text=shuffle(["Nerv' nicht, " + user.first_name + '!', user.first_name + ' du nervst ...',
                                       "Alter nerv' mich nicht " + user.first_name] + '!'), parse_mode=ParseMode.MARKDOWN)
        users[user.username]['counter'] = 0
        return 'nervnicht'
    if in_(text, ['ente ist']) and in_(text, ['cool', 'toll', 'gute ente', 'super', 'die beste']):
        bot.send_message(chat_id=update.message.chat_id,
                         text='Ja, das bin ich, ' + user.first_name,
                         parse_mode=ParseMode.MARKDOWN)
        return 'ente cool'


    # Hallo Lukas
    if user.username == 'lukas_mandok' and in_(text, ['ente']):
        bot.send_message(chat_id=update.message.chat_id, text=shuffle(['Hallo Lukas 😊', 'Hallo Lukas 😊', 'Hallo Lukas 😊', 'Hi Lukas!']), parse_mode=ParseMode.MARKDOWN)
        return 'hallolukas'

def check_actions(bot, update):
    text = update.message.text.lower()

    # OK ente
    if in_(text, ['ok ente']):
        try:
            answer = ok_ente(bot, update)
        except:
            answer = 'Not OK, ' + update.message.from_user.first_name

    # Mensa
    elif in_(text, ['mensa', 'speiseplan', 'was gibt es', 'zu essen']) and in_(text, ['morgen']):
        answer = mensa_message('morgen')
    elif in_(text, ['mensa', 'speiseplan']) or (in_(text, ['was gibt es', 'zu essen']) and in_(text, ['heute'])):
        answer = mensa_message('heute')

    # Wetter
    elif in_(text, ['wetter', 'regen', 'regnen', 'schön sein', 'schön ist', 'morgen gut', 'sonne']):
        answer = weather_message('Heidelberg')

    # Datum von Heute
    elif in_(text, ['datum', 'wievielt', 'welcher tag']) or (in_(text, ['heute']) and in_(text, ['tag'])):
        answer = 'Heute ist ' + str(datetime.datetime.today().strftime('%A der %d.%m.%Y')) + ' QUACK!'

    else:
        answer = None
    return answer

def parse_text_message(bot, update):
    response = None
    text = update.message.text
    print('they:', text)
    conlog('they', text)

    userspecific = check_user(bot, update)
    if not userspecific:
        action = check_actions(bot, update)
        if action:
            response = action
        else:
            answer = match_answer(text)
            response = answer

    if response:
        print('  me:', response)
        conlog('me', response)
        bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode=ParseMode.MARKDOWN)
    return response

# Receiver handler function
def receiver(bot, update):
    bigdata.add(update, type='updates')
    if update.message.text:
        textresponse = parse_text_message(bot, update)


### The true beginning

# Set locale, initialize working directory
locale.setlocale(locale.LC_TIME, ('de', 'UTF-8'))
workdir = os.getcwd() + '/'

# Exit handler
atexit.register(exit_handler)

# Read Telegram bot authentication information
with open(workdir + 'auth.json') as json_data:
    d = json.load(json_data)
    myname = d['name']
    token = d['telegram-key']

# Logging
conlogpath = start_conlog()
bigdata = data('bigdata')

# Initialize the Weather API
owmkey = '04f9cff3a5fbb8c457e31444bae05328'
owm = OWM(API_key=owmkey, language='de')

# Stuff for Mensa interface
mensaurl = 'https://mensahd.herokuapp.com/all/inf304.xml'
if not os.path.exists(workdir + 'mensa/'):
    os.mkdir(workdir + 'mensa/')

# Define telegram bot (updater and dispatcher Objects,
updater = Updater(token=token)
dispatcher = updater.dispatcher

# Initialize behaviour object and oad behaviour file
behaviour = ente.behaviour.behaviour()
behaviour.load('wordmatch')

# Register command handlers
behaviour_handler = CommandHandler('behaviour', behaviour.behave, pass_args=True)
dispatcher.add_handler(behaviour_handler)
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)
license_handler = CommandHandler('license', license)
dispatcher.add_handler(license_handler)
unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)

# Define user dictionary
users = dict()

# Register main receiver handler (first to get all non-command messages
receiver_handler = MessageHandler(Filters.text, receiver)
dispatcher.add_handler(receiver_handler)

# Start the bot
updater.start_polling()
updater.idle()