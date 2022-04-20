import json
import time

import requests
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup

from MyMQTT import *


class TelgramBot:
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
        MessageLoop(self.bot, {'chat': self.on_chat_message}).run_as_thread()

    def on_chat_message(self, msg):
        content_type, chat_type, chat_ID = telepot.glance(msg)
        self.chatIDs.append(chat_ID)
        if content_type == "text":
            message = msg['text']
            if message=="/start":
                self.bot.sendMessage(chat_ID, text="Welcome")
            else:
                self.bot.sendMessage(chat_ID, text="Command is not supported !")
        else:
                self.bot.sendMessage(chat_ID, text="Massage format is not supported ! use only text")
        
    def notify(self,topic,message):
        print(message)
        msg=json.loads(message)
        
        alert=msg["alert"]
        action=msg["action"]
        tosend=f"ATTENTION!!!\n{alert}, you should {action}"
        for chat_ID in self.chatIDs:
            self.bot.sendMessage(chat_ID, text=tosend)

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
    tst = TelgramBot(token)
    while True:
        time.sleep(1)
    # topic = "orlando/alert/temp"
    # for i in range(5):
    #     message={"alert":i,"action":i**2}
    #     test.myPublish(topic,message)
    #     time.sleep(3)

