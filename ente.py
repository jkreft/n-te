# coding=utf-8

from telegram.ext import CommandHandler, MessageHandler, Filters, Updater
from telegram.parsemode import ParseMode as ParseMode
import json
import os
import time

myname = 'physical_ente_bot'
workdir = os.getcwd() + '/'

with open(workdir + 'authentication.json') as json_data:
    d = json.load(json_data)
    token = d['telegram-key']

updater = Updater(token=token)
dispatcher = updater.dispatcher

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Quak, ich bin Ente!")

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="I'm sorry Dave, I'm afraid I can't do that.")

unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)

# To start bot: Run updater.start_polling()
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

def original_ente(bot, update):
    answer = False
    text = update.message.text.lower()

    def in_text(keywords):
        return any(k in text for k in keywords)

    if in_text(['ente']):
        answer = "*QUACK!*"
    elif in_text(['.*f+o+s+s+.*']):
        answer = "*FOOOOOOOSSSS <3!*"
    elif in_text(['turmbraeu', "turmbräu", "git", "love"]):
        answer = "*<3*"
    elif in_text(["svn", "subversion"]):
        answer = "*QUAAAAACKKKK😡!!*"
    elif in_text(["bread", "brot"]):
        answer = "Mmhhh"

    if answer:
        bot.send_message(chat_id=update.message.chat_id, text=answer)
    return answer

def fallback(bot, update):
    fallback = 'Öööh ... äääähm ... hmmm'
    bot.send_message(chat_id=update.message.chat_id, text=fallback)

def receiver(bot, update):
    conlist.append(update)
    original = original_ente(bot, update)
    if not original:
        return
    else:
        conlist.append()

receiver_handler = MessageHandler(Filters.text, receiver)
dispatcher.add_handler(receiver_handler)


conlist = list()
updater.start_polling()

