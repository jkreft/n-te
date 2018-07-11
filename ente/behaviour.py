import json, os
from telegram.parsemode import ParseMode as ParseMode


workdir = os.getcwd() + '/'


class behaviour:

    def __init__(self):
        # Initialize wordmatch list
        self.wordmatch = list()
        # Define behaviour state and storage dictionary (current state of command and intermediate variables)
        self.behav = {'match': {'state': 0, 'new': {}}, 'analysis':{'state':0}}

    # Load behaviour file
    def load(self, name):
        if not os.path.exists(workdir + 'behaviour/'):
            os.mkdir(workdir + 'behaviour/')
        if not os.path.exists(workdir + 'behaviour/' + name + '.json'):
            with open(workdir + 'behaviour/' + name + '.json', 'w') as behaviourfile:
                json.dump(None, behaviourfile)
        with open(workdir + 'behaviour/' + name + '.json', 'r') as behaviourfile:
            output = json.load(behaviourfile)
        self.wordmatch = output

    # Change (store current) behaviour file
    def store(self, dictionary, name):
        with open(workdir + 'behaviour/' + name + '.json', 'w') as behaviourfile:
            json.dump(dictionary, behaviourfile)


    ### Admin Commands and changing Entes behaviour ###

    def behave(self, bot, update, args=None):

        def add_wordmatch(newmatch):
            self.wordmatch.append(newmatch)
            self.store(self.wordmatch, 'wordmatch')
            bot.sendMessage(chat_id=update.message.chat_id, text='Match mode. Added: \n' + str(newmatch))

        if update.message.from_user.username == 'phaetjay':
            if self.behav['match']['state'] == 1:
                if args[0] == 'keywords':
                    print(args[1])
                    keywords = ' '.join(args[1:]).split('!!!')
                    print(keywords)
                    self.behav['match']['new']['keywords'] = keywords
                    if 'answers' in self.behav['match']['new']:
                        missing = False
                        bot.sendMessage(chat_id=update.message.chat_id,
                                    text='OK, keywords are: ' + '\n  '.join(keywords), parse_mode=ParseMode.MARKDOWN)
                    else:
                        missing = 'answers'
                        bot.sendMessage(chat_id=update.message.chat_id,
                                        text='Keywords are:\n' + '\n  '.join(keywords) + '\n * Missing ' + missing + '.*', parse_mode=ParseMode.MARKDOWN)
                elif args[0] == 'answers':
                    answers = ' '.join(args[1:]).split('!!!')
                    self.behav['match']['new']['answers'] = answers
                    if 'keywords' in self.behav['match']['new']:
                        missing = False
                        bot.sendMessage(chat_id=update.message.chat_id,
                                        text='OK, answers are: ' + '\n  '.join(answers), parse_mode=ParseMode.MARKDOWN)
                    else:
                        missing = 'keywords'
                        bot.sendMessage(chat_id=update.message.chat_id,
                                        text='Answers are: ' + '\n  '.join(answers) + '\n * Missing ' + missing + '.*',
                                        parse_mode=ParseMode.MARKDOWN)
                elif args[0] == 'weight':
                    weight = int(args[1])
                    print(weight)
                    self.behav['match']['new']['weight'] = weight
                    missing = True
                    bot.sendMessage(chat_id=update.message.chat_id,
                                    text='Weight is: ' + str(weight) + '\n*Still missing something.*', parse_mode=ParseMode.MARKDOWN)
                elif args[0] == 'cancel' or args[0] == 'abort':
                    bot.sendMessage(chat_id=update.message.chat_id, text='Canceling.', parse_mode=ParseMode.MARKDOWN)
                    self.behav['match']['state'] = 0
                    return None
                else:
                    missing = True
                    bot.sendMessage(chat_id=update.message.chat_id, text='I am sorry, I do not understand.', parse_mode=ParseMode.MARKDOWN)
                if not missing:
                    if not self.behav['match']['new']['weight']:
                        self.behav['match']['new']['weight'] = 1
                    add_wordmatch(self.behav['match']['new'])
                    self.behav['match']['state'] = 0
                return None

            if self.behav['match']['state'] == 0 and self.behav['analysis']['state'] == 0:
                print('Command: ' + update.message.text)
                bot.send_message(chat_id=update.message.chat_id, text='Yes Jay.', parse_mode=ParseMode.MARKDOWN)
                print(args)
                if not (len(args) > 0):
                    bot.send_message(chat_id=update.message.chat_id, text='What do you wish?', parse_mode=ParseMode.MARKDOWN)
                else:
                    if args[0] == 'match':
                        bot.send_message(chat_id=update.message.chat_id, text='Match mode.', parse_mode=ParseMode.MARKDOWN)
                        if len(args) > 2:
                            if args[1] == 'line':
                                try:
                                    arginput = ' '.join(args[2:]).split(' > ')
                                    print(arginput)
                                    keywords = arginput[0].split('!!!')
                                    print(keywords)
                                    answers = arginput[1].split('!!!')
                                    print(answers)
                                    if len(arginput) == 3:
                                        weight = int(arginput[2])
                                    else:
                                        weight = 1
                                    newmatch = {'keywords': keywords, 'answers': answers, 'weight' : weight}
                                except:
                                    bot.send_message(chat_id=update.message.chat_id,
                                                     text='But I am very sorry, I do not understand.',
                                                     parse_mode=ParseMode.MARKDOWN)
                                    return None
                            else:
                                bot.send_message(chat_id=update.message.chat_id, text='But I am very sorry, I do not understand.', parse_mode=ParseMode.MARKDOWN)
                                return None
                        else:
                            bot.sendMessage(chat_id=update.message.chat_id, text='Match mode. Enter keywords and answers:', parse_mode=ParseMode.MARKDOWN)
                            self.behav['match']['state'] = 1
                            return None
                        add_wordmatch(newmatch)
                        return None
                    elif args[0] == 'analysis':
                        bot.send_message(chat_id=update.message.chat_id, text='Analysis mode. Enter query:', parse_mode=ParseMode.MARKDOWN)
                        self.behav['analysis']['state'] = 1
                    else:
                        bot.send_message(chat_id=update.message.chat_id, text='But I am very sorry, I do not understand.', parse_mode=ParseMode.MARKDOWN)
            return None