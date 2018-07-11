# coding=utf-8

from telegram.ext import CommandHandler, MessageHandler, Filters, Updater
from telegram.parsemode import ParseMode as ParseMode
import json
import os
from datetime import datetime
import locale
import numpy as np


locale.setlocale(locale.LC_TIME, ('de', 'UTF-8'))
workdir = os.getcwd() + '/'

with open(workdir + 'auth.json') as json_data:
    d = json.load(json_data)
    myname = d['name']
    token = d['telegram-key']


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
	if in_(text, ['geheim']):
		answer = 'Pssst!'

    if answer:
        bot.send_message(chat_id=update.message.chat_id, text=answer, parse_mode=ParseMode.MARKDOWN)
    return answer


def fallback(bot, update):
    fallback = 'Öööh ... äääähm ... hmmm'
    bot.send_message(chat_id=update.message.chat_id, text=fallback)

def receiver(bot, update):
    conlog('they', update.message.text)
    original = original_ente(bot, update)
    if original:
        print(original)
        conlog('me', original)
    else:
        hannes = hannes_ente(bot, update)
        if hannes:
            print(hannes)
            conlog('me', hannes)

receiver_handler = MessageHandler(Filters.text, receiver)
dispatcher.add_handler(receiver_handler)


updater.start_polling()

