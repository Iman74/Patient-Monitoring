import json
import time
import requests
from pathlib import Path
import datetime 

import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup
#from telegram import ParseMode

#from MyMQTT import *

class PatientMonitoringBOT:
    #def __init__(self,token,broker,port, catalogIP ):
    def __init__(self,token,catalogIP ):
        self.token = token
        # Catalog token (is it useful)
        # self.tokenBot=requests.get("http://catalogIP/telegram_token").json()["telegramToken"]
        self.bot = telepot.Bot(self.token)
        self.chatIDs = []      #is it meaningful?
        self.catalog = catalogIP     #catalog IP address
        # First keyboard that will present to the user 2 options: register or login
        self.keyboard = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='Register', callback_data='/register')],
                            [InlineKeyboardButton(text='Login', callback_data='/login')]
                        ])
        # Patient keyboard
        self.keyboardP = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='Body Temperature', callback_data='/bodytemperature')],
                            [InlineKeyboardButton(text='Room Temperature', callback_data='/roomtemperature')],
                            [InlineKeyboardButton(text='Open Window', callback_data='/openwindow')],
                            [InlineKeyboardButton(text='Close Window', callback_data='/closewindow')]
                        ])
        # Doctor keyboard
        self.keyboardD = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='List of my patients', callback_data='/patientslist')]
                        ]) 
        
        self.data={}
        self.s={}
        
    def start(self):  #I think that I need a start to continue from the previous query
        MessageLoop(self.bot, {'chat': self.on_chat_message, 'callback_query': self.on_callback_query}).run_as_thread()
        print('Listening...')
  
    def on_chat_message(self, msg):
        content_type, chat_type, chat_ID = telepot.glance(msg)   
        #I want to check if the chat_ID is already registred inside the catalog
        message = msg['text']
        if message == "/start":            
            """Send a Welcome message when the user selects /start"""
            welcome = ("Welcome to the PatientMonitoring Bot 👩‍⚕️🩺" + "\nPlease chose an option from the menu below")               
            self.bot.sendMessage(chat_ID, text=welcome , reply_markup=self.keyboard)
            
        if "chat_ID" in list(self.data.keys()):
            
            # Managing the REGISTRATION
            if '/register' in list(self.data['chat_ID'].keys()):
                self.registration(msg, chat_ID)
                                    
            # Managing the LOGGING phase
            if '/login' in list(self.data['chat_ID'].keys()):
                self.logging(msg, chat_ID)
                                                                        
    def on_callback_query(self,msg):
        query_ID , chat_ID , query_data = telepot.glance(msg,flavor='callback_query')
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"- "+'Callback Query:', query_ID, chat_ID, query_data)
        
        if(query_data == '/register' or query_data == '/login'):
            self.data["chat_ID"]= {}
            self.data["chat_ID"][query_data]={}
            self.data["chat_ID"][query_data]['userID']=None
            self.data["chat_ID"][query_data]['password']=None
            self.data["chat_ID"][query_data]['user_type']=None

            self.bot.sendMessage(chat_ID, text='Insert your userID:')
            
        #then insert the query_data for other commands
        if query_data == '/patientslist':
            r = requests.get(self.catalog+'/patients')   # I retrieve the list of patients 
            patients= r.json()
            
            print(patients)
            # patients_list = []
            # for patient in range(len(patients["patients"])):
            #     patient_list= patient
            

   

    # REGISTRATION ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def registration(self, msg, chat_ID):
        action = '/register'
        if self.data['chat_ID']['/register']['userID']==None and self.data['chat_ID']['/register']['password']==None:
            # Store the userID 
            self.data['chat_ID']['/register']['userID'] = msg['text']       # this will return a string
            user_ID = int(self.data['chat_ID']['/register']['userID'])      # DUBBIO: TENERE USER_ID O METTERE DITETTAMENTE L'INFO IN SELF.DATA? 
            # retreive the info of the user with user_ID
            is_doctor, is_patient, user_dict, r = self.user_info(chat_ID, user_ID, action)                   
            # Check if the userID is already registered                     
            if user_dict["password"]:
                self.bot.sendMessage(chat_ID, '⚠️ This userID is already registered, \nto login you should use the "Login" button or the /login command')         
            else:
                self.bot.sendMessage(chat_ID, text='Choose a password:')
                
        elif self.data["chat_ID"]['/register']["userID"]!=None and self.data["chat_ID"]['/register']["password"]==None:
            self.data["chat_ID"]['/register']["password"]=msg['text']
            user_ID = int(self.data['chat_ID']['/register']['userID'])      # DUBBIO: TENERE USER_ID O METTERE DITETTAMENTE L'INFO IN SELF.DATA? 
            # Retreive the user_dict to update
            is_doctor, is_patient, user_dict, r = self.user_info(chat_ID, user_ID, action)   
            # update user_dict with pw and chat_ID; I'll put this dictionary inside the catalog without taking risk of overwriting the wrong user                            
            user_dict["password"]= self.data["chat_ID"]['/register']["password"]
            user_dict["telegramID"]= chat_ID
            # check if the user_ID matches any user                                              
            if is_doctor == False and is_patient == False :
                error_msg = '⚠️ The userID inserted corresponds neither to a doctor nor to a patient, there\'s something wrong...'
                self.bot.sendMessage(chat_ID, text=error_msg)                    
            # UPDATING THE CATALOG WITH PASSWORD AND CHAT_ID
            self.Catalog_update(chat_ID, is_doctor, is_patient, user_dict, r)
            del self.data['chat_ID'][action]
            print("Registration was successful")
            
    # LOGGING +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def logging(self, msg, chat_ID):
        action = '/login'
        if self.data['chat_ID']['/login']['userID']==None and self.data['chat_ID']['/login']['password']==None:
            # Store the userID 
            self.data['chat_ID']['/login']['userID'] = msg['text']     # this will return a string
            user_ID = int(self.data['chat_ID']['/login']['userID'])    # DUBBIO: TENERE USER_ID O METTERE DITETTAMENTE L'INFO IN SELF.DATA?        
            self.bot.sendMessage(chat_ID, text='Insert your password:')
        elif self.data['chat_ID']['/login']['userID']!=None and self.data['chat_ID']['/login']['password']==None: 
            self.data['chat_ID']['/login']['password']=msg['text']
            user_ID = int(self.data['chat_ID']['/login']['userID'])    # DUBBIO: TENERE USER_ID O METTERE DITETTAMENTE L'INFO IN SELF.DATA? 
            # I use the method user_info but I'm only interested in the role of the user; the user_dict will be retreived later with a GET
            is_doctor, is_patient, user_dict, r = self.user_info(chat_ID, user_ID, action)
            print(self.data['chat_ID']['/login']['password'])
            if is_doctor:
                r = requests.get(self.catalog+'/doctor/'+ str(user_ID))   # I retrieve the info of a specific doctor
                user_dict = r.json()
                if str(user_dict["password"]) == self.data['chat_ID']['/login']['password']:
                    #presentare la keyboard con le opzioni per il dottore
                    regMessage = ("Welcome back Dr. {} 👋💉💊\nThese are the features you can use, to continue select one of them")              
                    self.bot.sendMessage(chat_ID, text=regMessage.format(user_dict["name"]), reply_markup=self.keyboardD)
                    print("Log in was successful")  
                else: 
                    self.bot.sendMessage(chat_ID, text='⚠️ You inserted the wrong password, please go back to /start and try to log in again with the correct one')  
            if is_patient:
                r = requests.get(self.catalog+'/patient/'+ str(user_ID))   # I retrieve the info of a specific doctor
                user_dict = r.json()
                if self.data['chat_ID']['/login']['password']== str(user_dict["password"]) :
                    #presentare la keyboard con le opzioni per il paziente
                    regMessage = ("Welcome {} 👋 \nThese are the features you can use, to continue select one of them")              
                    self.bot.sendMessage(chat_ID, text=regMessage.format(user_dict["name"]), reply_markup=self.keyboardP)
                    print("Log in was successful")  
                else: 
                    self.bot.sendMessage(chat_ID, text='⚠️ You inserted the wrong password, please go back to /start and try to log in again with the correct one')  
            if is_doctor == False and is_patient == False :
                error_msg = '⚠️ The userID inserted corresponds neither to a doctor nor to a patient, there\'s something wrong...'
                self.bot.sendMessage(chat_ID, text=error_msg)  
            del self.data['chat_ID'][action]
                          
    # RETREIVE INFO ABOUT THE USER ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def user_info(self, chat_ID, user_ID, action):
        """This method is used to retreive information about the user with that user_ID, such as:
           - is a doctor or a patient?
           - the user_dict
           It also returns 'r' (GET request) that will be useful later in the catalog update"""
        is_doctor = False
        is_patient = False
        r = requests.get(self.catalog+'/doctors')         # I retrieve the list of doctors 
        doctors = r.json()
        # Is a doctor?
        for doctor in range(len(doctors["doctors"])):  
            if str(doctors["doctors"][doctor]["userID"]) == self.data['chat_ID'][action]['userID']:     # this way I'm sure that this will always be a string comparison
                is_doctor = True
                self.data["chat_ID"][action]['user_type'] = 'doctor'
                r = requests.get(self.catalog+'/doctor/'+ str(user_ID))   # I retrieve the info of a specific doctor
                user_dict = r.json()          
                break               
        if is_doctor == False:
            r = requests.get(self.catalog+'/patients')   # I retrieve the list of patients 
            patients= r.json()
            # Is a patient?
            for patient in range(len(patients["patients"])):
                if str(patients["patients"][patient]["userID"]) == self.data['chat_ID'][action]['userID']:
                    is_patient = True
                    self.data["chat_ID"][action]['user_type'] = 'patient'
                    r = requests.get(self.catalog+'/patient/'+ str(user_ID))
                    user_dict = r.json()
                    break                   
        if is_doctor == False and is_patient == False :
            self.bot.sendMessage(chat_ID, text='The userID inserted is not correct, please try again')
            
        return is_doctor, is_patient, user_dict, r 
    
    # CATALOG UPDATE ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def Catalog_update(self, chat_ID, is_doctor, is_patient, user_dict, r):
        self.s["chat_ID"]=requests.Session()
        if r.status_code == 200:
            r = self.s["chat_ID"].put(self.catalog+'/user',json=user_dict) 
            if r.status_code == 200:
                if is_doctor:
                    regMessage = ("Welcome Dr. {}, your registration has been successful 🎉 \nThese are the features you can use, to continue select one of them")              
                    self.bot.sendMessage(chat_ID, text=regMessage.format(user_dict["name"]))
                    # self.bot.sendMessage(chat_ID, text=regMessage.format(user_dict["name"]) , reply_markup=self.keyboardD)
                if is_patient:
                    regMessage = ("Welcome {}, your registration has been successful 🎉 \nThese are the features you can use, to continue select one of them")
                    self.bot.sendMessage(chat_ID, text=regMessage.format(user_dict["name"]))
                    # self.bot.sendMessage(chat_ID, text= regMessage.format(user_dict["name"]), reply_markup=self.keyboardP)
                del user_dict
            else:
                self.bot.sendMessage(chat_ID,'🚫 Registration cannot be completed due to some error 🚫')
        else:
                self.bot.sendMessage(chat_ID, '🚫 Registration cannot be completed due to some error 🚫')
        return regMessage
        
# P = Path(__file__).parent.absolute()    # sequence providing access to the logical ancestors of the path; absolute if it has both a root and a drive
# CONF = P / 'Telegrambot_settings.json' 
    
if __name__ == '__main__':
    conf = json.load(open("settings.json"))
    token = conf["telegramToken"]
    catalogIP = conf["catalog_address"]
    
    PMBot = PatientMonitoringBOT(token, catalogIP)
    PMBot.start()
    print("Bot started ...")
    while True:
        time.sleep(10)
        

