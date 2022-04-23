import json
import time

import requests
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup

from MyMQTT import *


class TelegramBot:
    exposed=True
    def __init__(self, token):
        # Local token
        self.tokenBot = token
        # Catalog token
        # self.tokenBot=requests.get("http://catalogIP/telegram_token").json()["telegramToken"]
        self.bot = telepot.Bot(self.tokenBot)
        self.chatIDs=[]
        # self.client = MyMQTT("telegramBotIoT", broker, port, self)
        # self.client.start()
        # self.topic = topic
        # self.client.mySubscribe(topic)
        # self.__message={"alert":"","action":""}
        MessageLoop(self.bot, {'chat': self.on_chat_message, 'callback_query': self.on_callback_query}).run_as_thread()

    def on_chat_message(self, msg):
        content_type, chat_type, chat_ID = telepot.glance(msg)
        self.chatIDs.append(chat_ID)
        if content_type == "text":
            message = msg['text']
            if message=="/start":
                self.bot.sendMessage(chat_ID, text="Welcome")
                buttons=[[InlineKeyboardButton(text=f'Patient🧑', callback_data=f'patient'),InlineKeyboardButton(text=f'Doctor🩺', callback_data=f'doctor')]]
                keyboard=InlineKeyboardMarkup(inline_keyboard=buttons)
                self.bot.sendMessage(chat_ID, text='Select the category you belong to', reply_markup=keyboard)
            else:
                self.bot.sendMessage(chat_ID, text="Command is not supported!")
        else:
                self.bot.sendMessage(chat_ID, text="Message format is not supported! Use only text")


    def notify(self,topic,message):
        print(message)
        msg=json.loads(message)
        
        alert=msg["alert"]
        action=msg["action"]
        tosend=f"ATTENTION!!!\n{alert}, you should {action}"
        for chat_ID in self.chatIDs:
            self.bot.sendMessage(chat_ID, text=tosend)

    def on_callback_query(self,msg):
        query_ID, chat_ID, query_data=telepot.glance(msg,flavor='callback_query')
        user=query_data
        if user=="patient":
            self.bot.sendMessage(chat_ID, text='Insert your identification number')
        elif user=="doctor":
            self.bot.sendMessage(chat_ID, text='Insert your identification number')
        else:
            self.bot.sendMessage(chat_ID, text='Invalid operation')


if __name__ == "__main__":
    conf = json.load(open("settings.json"))
    token = conf["telegramToken"]

    # Echo bot
    # bot=EchoBot(token)

    # SimpleSwitchBot
    # broker = conf["brokerIP"]
    # port = conf["brokerPort"]
    # topic = "orlando/alert/#"
    #ssb = SimpleSwitchBot(token, broker, port, topic)
    # sb=MQTTbot(token,broker,port,topic)

    # input("press a key to start...")
    # test=MyMQTT("testIoTBot",broker,port,None)
    # test.start()
    tst = TelegramBot(token)
    while True:
        time.sleep(1)
    # topic = "orlando/alert/temp"
    # for i in range(5):
    #     message={"alert":i,"action":i**2}
    #     test.myPublish(topic,message)
    #     time.sleep(3)

