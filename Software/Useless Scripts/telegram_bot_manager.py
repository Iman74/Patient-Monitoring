import json
import time

import requests
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup
from dataclasses import dataclass
from dataclasses_json import dataclass_json, config
from typing import List
from os.path import exists

from MyMQTT import *

@dataclass_json
@dataclass(frozen=True)
class _TelegramPatient:
    patientID: str 
    chatID: str 
@dataclass_json
@dataclass(frozen=True)
class _TelegramDatabase:
    patients: List[_TelegramPatient]

class TelegramBot:
    exposed=True
    def __init__(self, token):
        # Local token
        self.tokenBot = token
        # Catalog token
        # self.tokenBot=requests.get("http://catalogIP/telegram_token").json()["telegramToken"]
        self.bot = telepot.Bot(self.tokenBot)
        self.chatIDs=[]
        self.telegramPatientsCatalog = "Telegram_Patients.json"
        #queries
        self.pIDquery = ""
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
                chatState = self.IsChatRegistred(chat_ID)
                if (chatState== ""):
                    #Registre new patient
                    buttons=[[InlineKeyboardButton(text=f'Patient🧑', callback_data=f'patient'),InlineKeyboardButton(text=f'Doctor🩺', callback_data=f'doctor')]]
                    keyboard=InlineKeyboardMarkup(inline_keyboard=buttons)
                    self.bot.sendMessage(chat_ID, text='Select the category you belong to', reply_markup=keyboard)
                else:
                    #Registred patient
                    text = 'Hi '  + str(chatState)
                    self.bot.sendMessage(chat_ID, text=text)
            elif self.pIDquery:
                # print(message)
                #check patient id and registration
                self.RegisterChat(message, chat_ID)
            else:
                self.bot.sendMessage(chat_ID, text="Command is not supported!")
        else:
                self.bot.sendMessage(chat_ID, text="Message format is not supported! Use only text")


    def RegisterChat(self, patientID, chatID):
        #check if the file is existed
        file_exists = exists(self.telegramPatientsCatalog)
        if(file_exists):
            # read current database
            with open(self.telegramPatientsCatalog, "r") as jsonFile:
                try:
                    patientsCatalog = _TelegramDatabase.from_json(json.load(jsonFile))
                    patientExisted = False
                    for patient in patientsCatalog.patients:
                        if (patient.patientID == patientID and
                            patient.chatID == chatID):
                            #previously registred
                            patientExisted = True
                    if patientExisted == False:
                        newpatient = _TelegramPatient(patientID, chatID)
                        patientsCatalog.patients.append(newpatient)
                        print(f'new patient registred')
                        text = str(patientID) + ' Registred'
                        self.bot.sendMessage(chatID, text=text)

                except Exception as e:
                    print(e)
        else:
            #initialize the Catalog
            newpatient = _TelegramPatient(patientID, chatID)
            patientsCatalog = _TelegramDatabase([newpatient])
            text = str(patientID) + ' Registred'
            self.bot.sendMessage(chatID, text=text)
            print(f'telegram patients Catalog initailized')
        # save Changes to database
        with open(self.telegramPatientsCatalog, "w") as jsonFile:
            try:
                json.dump(patientsCatalog.to_json(indent=4), jsonFile)
            except Exception as e:
                print(e)

    def IsChatRegistred(self, chatID):
            #check if the file is existed
            file_exists = exists(self.telegramPatientsCatalog)
            if(file_exists):
                # read current database
                with open(self.telegramPatientsCatalog, "r") as jsonFile:
                    try:
                        patientsCatalog = _TelegramDatabase.from_json(json.load(jsonFile))
                        for patient in patientsCatalog.patients:
                            if (patient.chatID == chatID):
                                #previously registred
                                return patient.patientID
                        return ""

                    except Exception as e:
                        print(e)
                        return ""
            else:
                return ""

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
        print(query_ID, chat_ID, query_data)
        if query_data=="patient":
            self.pIDquery = self.bot.sendMessage(chat_ID, text='Insert your identification number')

        elif query_data=="doctor":
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

