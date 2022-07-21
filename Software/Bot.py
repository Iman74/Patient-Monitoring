import json
import time
import requests
from pathlib import Path
import datetime 
import copy
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup

from MyMQTT import *
from imgkitTS import *

class PatientMonitoringBOT:
    def __init__(self,token, catalogIP, clientID, broker, port, baseTopic):
        self.catalog = catalogIP     #catalog IP address
        self.token = token
        # self.token = requests.get(self.catalog+'/token')
        self.bot = telepot.Bot(self.token)
        self.chat_ID = None 
        
        #Subscriber    
        self.port = port
        self.baseTopic = baseTopic
        self.topic = baseTopic + "/+/+/Warning"        # self.topic deve essere "basetopic/#/Warning"
        self.clientID = clientID
        self.client = MyMQTT(clientID,broker,port,self)
        
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
        # Doctor keyboards
        self.keyboardD = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='List of my patients', callback_data='/listofpatients')]
                        ]) 
        self.keyboardD2 = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='Heart Rate trend - last 2 h', callback_data='/HR2')],
                            [InlineKeyboardButton(text='Oxygenation trend - last 2 h', callback_data='/OX2')],
                            [InlineKeyboardButton(text='Body Temperature - last 2 h', callback_data='/BT2')],
                            [InlineKeyboardButton(text='Enable Notifications', callback_data='/Notifications')]
                        ])
        # self.keyboardD2 = InlineKeyboardMarkup(inline_keyboard=[
        #                     [InlineKeyboardButton(text='Heart Rate trend - last 2 h', callback_data='/HR2')],
        #                     [InlineKeyboardButton(text='Heart Rate trend - last 24 h', callback_data='/HR24')],
        #                     [InlineKeyboardButton(text='Oxygenation trend - last 2 h', callback_data='/OX2')],
        #                     [InlineKeyboardButton(text='Oxygenation trend - last 24 h', callback_data='/OX24')],
        #                     [InlineKeyboardButton(text='Body Temperature - last 2 h', callback_data='/BT2')],
        #                     [InlineKeyboardButton(text='Body Temperature - last 24 h', callback_data='/BT24')]
        #                 ])
        self.keyboard_notify = InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text='Stop notifications', callback_data='/StopNotifications')]
                            ])
        
        self.data={}
        self.s={}
        
    def start(self):  #I think that I need a start to continue from the previous query
      
        MessageLoop(self.bot, {'chat': self.on_chat_message, 'callback_query': self.on_callback_query}).run_as_thread()
        print('Listening...')
        
    def start_mysub(self):
        # #parte il subscriber
        self.client.start()
        print('{} has started'.format(self.clientID))
        self.client.mySubscribe(self.topic)
        
    def stop_mysub(self):
        self.client.mySubscribe(self.topic)
        print('{} has stopped'.format(self.clientID))
        self.client.stop()       
                        
    def on_chat_message(self, msg):
        content_type, chat_type, chat_ID = telepot.glance(msg)   
        message = msg['text']
        if not self.chat_ID:
            self.chat_ID = copy.deepcopy(chat_ID)
        
        if message == "/start":            
            """Sends a Welcome message when the user selects /start"""
            welcome = ("Welcome to the PatientMonitoring Bot 👩‍⚕️🩺" + "\nPlease chose an option from the menu below")               
            self.bot.sendMessage(chat_ID, text=welcome , reply_markup=self.keyboard)
            
        elif message == '/login':          # mi permette di fare il login anche se non clicco il pusante
            self.data = self.store_data(chat_ID, message)
            
        elif 'user' in list(self.data.keys()):      
            
            # Managing the REGISTRATION
            if '/register' in list(self.data['user'].keys()):
                self.registration(msg, chat_ID)
                                    
            # Managing the LOGGING phase
            elif '/login' in list(self.data['user'].keys()):
                if self.data['user']['/login']['patient_IDs'] == None:
                    self.logging(msg, chat_ID)
                else :
                    self.data['user']['/login']['patient_ID']= message
                    self.bot.sendMessage(chat_ID, text="What do you want to see?", reply_markup=self.keyboardD2)
        else:
            self.bot.sendMessage(chat_ID, text="Command not supported, go back to the /start")
                                                                                                         
    def on_callback_query(self,msg):
        query_ID , chat_ID , query_data = telepot.glance(msg,flavor='callback_query')
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"- "+'Callback Query:', query_ID, chat_ID, query_data)
        
        if(query_data == '/register' or query_data == '/login'):
            self.data = self.store_data(chat_ID, query_data)
            
        #then insert the query_data for other commands
        if query_data == '/listofpatients':
            self.get_listofpatients(chat_ID)
        
        elif(query_data == '/HR2'):
            self.thingspeak_plot(chat_ID, '1') 
        elif(query_data == '/OX2'):            
            self.thingspeak_plot(chat_ID, '2')
        elif(query_data == '/BT2'):
            self.thingspeak_plot(chat_ID, '3')
        elif(query_data == '/Notifications'):
            self.start_mysub()
        elif(query_data == '/StopNotifications'):
            self.stop_mysub()        
            
        elif(query_data == '/bodytemperature'): 
            self.thingspeak_plot(chat_ID, '3')   
        elif(query_data == '/roomtemperature'): 
            self.thingspeak_plot(chat_ID, '4')

    def get_listofpatients(self, chat_ID):
        r = requests.get(self.catalog+'/patients_doc/{}'.format(self.data['user']['/login']['userID']))   # I retrieve the list of patients             
        patients= r.json()
        # torna qui
        if patients:    
            self.bot.sendMessage(chat_ID, text='These are your patients:')    
            patients_IDs = []
            for patient in patients:
                if patient['name']:
                    self.bot.sendMessage(chat_ID, text='{} - ID: {}'.format(patient['name'],patient['userID']))
                    patients_IDs.append(int(patient['userID']))
            # Patient Selection
            self.data['user']['/login']['patient_IDs'] = patients_IDs
            self.bot.sendMessage(chat_ID, text='Insert the ID of the patient you\'re intrested in:')
        else: 
            self.bot.sendMessage(chat_ID, text='There are no patients on your list.\n ')
            
    def thingspeak_plot(self, chat_ID, field):
        conf = json.load(open("settings.json"))
        chID = conf["thingspeak_chID"]
        n_samples='480'                 # per il trend di 2 h servono 4x60x2 = 480 
        p={'api_key': conf["read_api_key"],'results':n_samples}
        r= requests.get('https://api.thingspeak.com/channels/'+str(chID)+'/fields/'+str(field)+'.json?',params=p)
        
        try:
            feeds=json.loads(r.text)['feeds']
            ind=-1
            for j,sample in enumerate(feeds):
                if sample["field"+field] is not None:
                    ind=j
                    
            if ind==-1:
                n_samples=str(json.loads(r.text)["channel"]["last_entry_id"])
                p={'api_key':conf["thingspeak_rkey"],'results':n_samples}
                r= requests.get('https://api.thingspeak.com/channels/'+str(chID)+'/fields/'+str(field)+'.json?',params=p)
                feeds=json.loads(r.text)['feeds']
                ind=-1
                for j,sample in enumerate(feeds):
                    if sample["field"+field] is not None:
                        ind=j
            
            Value =str(json.loads(r.text)['feeds'][ind]['field'+field])
            if field == '1':
                self.bot.sendMessage(chat_ID, text='Heart Rate is: ' + round(int(Value)) + ' bpm')
            elif field == '2':
                self.bot.sendMessage(chat_ID, text='Oxygenation is: ' + Value + ' %')
            elif field == '3':
                self.bot.sendMessage(chat_ID, text='Body temperature is: ' + Value + ' °C')              
            elif field == '4':
                self.bot.sendMessage(chat_ID, text='Room temperature is: ' + Value + ' °C')
                
            self.bot.sendMessage(chat_ID, text="This is a graph with the trend for the last 2 hours:\nhttps://thingspeak.com/channels/"+str(chID)+"/charts/"+str(field))
        except:
            self.bot.sendMessage(chat_ID, text="Data not avaliable")

    def store_data(self, chat_ID, query_data):
        self.data['user']= {}
        self.data['user'][query_data]={}
        self.data['user'][query_data]['chat_ID']=None
        self.data['user'][query_data]['userID']=None
        self.data['user'][query_data]['password']=None
        self.data['user'][query_data]['user_type']=None
        self.data['user'][query_data]['patient_IDs']=None        # qui memorizzo la lista degli ID dei pazienti del dottore che sta usando il bot
        self.data['user'][query_data]['patient_ID']=None     # qui memorizzo l'ID del paziente di cui si vogliono vedere i trend   
        self.bot.sendMessage(chat_ID, text='Insert your userID:')  
        return self.data
    
    # # REGISTRATION ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def registration(self, msg, chat_ID):
        action = '/register'
        if self.data['user'][action]['userID']==None and self.data['user'][action]['password']==None:
            # Store the userID 
            self.data['user'][action]['userID'] = msg['text']       # this will return a string
            # retreive the info of the user with user_ID
            is_doctor, is_patient, user_dict, r = self.user_info(chat_ID, self.data['user'][action]['userID'], action)                   
            # Check if the userID is already registered                     
            if user_dict["password"]:
                self.bot.sendMessage(chat_ID, '⚠️ This userID is already registered, \nin order to login you should use the "Login" button or the /login command') 
                del self.data['user'][action]   #PROVA        
            else:
                self.bot.sendMessage(chat_ID, text='Choose a password:')
                
        elif self.data['user'][action]["userID"]!=None and self.data['user'][action]["password"]==None:
            self.data['user'][action]["password"]=msg['text']
            user_ID = int(self.data['user'][action]['userID'])      # DUBBIO: TENERE USER_ID O METTERE DITETTAMENTE L'INFO IN SELF.DATA? 
            # Retreive the user_dict to update
            is_doctor, is_patient, user_dict, r = self.user_info(chat_ID, self.data['user'][action]['userID'], action)   
            # update user_dict with pw and chat_ID; I'll put this dictionary inside the catalog without taking risk of overwriting the wrong user                            
            user_dict["password"]= self.data['user'][action]["password"]
            self.data['user'] = chat_ID
            user_dict["telegramID"]= chat_ID
            # check if the user_ID matches any user                                              
            if is_doctor == False and is_patient == False :
                error_msg = '⚠️ The userID inserted corresponds neither to a doctor nor to a patient, there\'s something wrong...'
                self.bot.sendMessage(chat_ID, text=error_msg)                    
            # UPDATING THE CATALOG WITH PASSWORD AND CHAT_ID
            self.Catalog_update(chat_ID, is_doctor, is_patient, user_dict, r)
            del self.data['user'][action]
            print("Registration was successful")
            
    # LOGGING +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def logging(self, msg, chat_ID):
        action = '/login'
        
        if self.data['user'][action]['userID']==None and self.data['user'][action]['password']==None:
            # Store the userID 
            self.data['user'][action]['userID'] = msg['text']     # this will return a string
            # print("username inserted: {}".format(self.data['user'][action]['userID'])) 
            self.bot.sendMessage(chat_ID, text='Insert your password:')
            
        elif self.data['user']['/login']['userID']!=None and self.data['user']['/login']['password']==None: 
            self.data['user']['/login']['password']=msg['text']
            # I use the method user_info but I'm only interested in the role of the user; the user_dict will be retreived later with a GET
            is_doctor, is_patient, user_dict, r = self.user_info(chat_ID, self.data['user']['/login']['userID'], action)
            
            if is_doctor:
                r = requests.get(self.catalog+'/doctor/'+ str(self.data['user']['/login']['userID']))   # I retrieve the info of a specific doctor
                user_dict = r.json()
                if str(user_dict["password"]) == self.data['user']['/login']['password']:
                    # self.data['user'] = chat_ID
                    #presentare la keyboard con le opzioni per il dottore
                    # print(self.data)
                    regMessage = ("Welcome back Dr. {} 👋💉💊\nThese are the features you can use, to continue select one of them")              
                    self.bot.sendMessage(chat_ID, text=regMessage.format(user_dict["name"]), reply_markup=self.keyboardD)
                    print("Log in was successful")  
                else: 
                    self.bot.sendMessage(chat_ID, text='⚠️ You inserted the wrong password, try to /login again with the correct password')  
            
            if is_patient:
                r = requests.get(self.catalog+'/patient/'+ str(self.data['user']['/login']['userID']))   # I retrieve the info of a specific doctor
                user_dict = r.json()
                if self.data['user']['/login']['password']== str(user_dict["password"]) :
                    # self.data['user'] = chat_ID
                    #presentare la keyboard con le opzioni per il paziente
                    regMessage = ("Welcome {} 👋 \nThese are the features you can use, to continue select one of them")              
                    self.bot.sendMessage(chat_ID, text=regMessage.format(user_dict["name"]), reply_markup=self.keyboardP)
                    print("Log in was successful")  
                else: 
                    self.bot.sendMessage(chat_ID, text='⚠️ You inserted the wrong password, try to /login again with the correct password')  
            
            if is_doctor == False and is_patient == False :
                error_msg = '⚠️ The userID inserted corresponds neither to a doctor nor to a patient, there\'s something wrong...'
                self.bot.sendMessage(chat_ID, text=error_msg)  
            # del self.data['user'][action]       # andare a vedere
                          
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
            if str(doctors["doctors"][doctor]["userID"]) == self.data['user'][action]['userID']:     # this way I'm sure that this will always be a string comparison
                is_doctor = True
                self.data['user'][action]['user_type'] = 'doctor'
                r = requests.get(self.catalog+'/doctor/'+ str(user_ID))   # I retrieve the info of a specific doctor
                user_dict = r.json()          
                break               
        if is_doctor == False:
            r = requests.get(self.catalog+'/patients')   # I retrieve the list of patients 
            patients= r.json()
            # Is a patient?
            for patient in range(len(patients["patients"])):
                if str(patients["patients"][patient]["userID"]) == self.data['user'][action]['userID']:
                    is_patient = True
                    self.data['user'][action]['user_type'] = 'patient'
                    r = requests.get(self.catalog+'/patient/'+ str(user_ID))
                    user_dict = r.json()
                    break                   
        if is_doctor == False and is_patient == False :
            self.bot.sendMessage(chat_ID, text='The userID inserted is not correct, please try again')
            
        return is_doctor, is_patient, user_dict, r 
    
    # CATALOG UPDATE ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def Catalog_update(self, chat_ID, is_doctor, is_patient, user_dict, r):
        self.s['user']=requests.Session()
        if r.status_code == 200:
            r = self.s['user'].put(self.catalog+'/user',json=user_dict) 
            if r.status_code == 200:
                if is_doctor:
                    regMessage = ("Welcome Dr. {}, your registration has been successful 🎉 \nThese are the features you can use, to continue select one of them")              
                    # self.bot.sendMessage(chat_ID, text=regMessage.format(user_dict["name"]))
                    self.bot.sendMessage(chat_ID, text=regMessage.format(user_dict["name"]) , reply_markup=self.keyboardD)
                if is_patient:
                    regMessage = ("Welcome {}, your registration has been successful 🎉 \nThese are the features you can use, to continue select one of them")
                    # self.bot.sendMessage(chat_ID, text=regMessage.format(user_dict["name"]))
                    self.bot.sendMessage(chat_ID, text= regMessage.format(user_dict["name"]), reply_markup=self.keyboardP)
                del user_dict
            else:
                self.bot.sendMessage(chat_ID,'🚫 Registration cannot be completed due to some error 🚫')
        else:
                self.bot.sendMessage(chat_ID, '🚫 Registration cannot be completed due to some error 🚫')
        return regMessage
    
    # NOTIFICATION ********************************************************************************************************************************************
    def notify(self,topic,message):
        msg = json.loads(message)
        chat_ID = self.chat_ID
        if chat_ID: 
            patient_ID = topic.split('/')[1]
            if patient_ID == self.data['user']['/login']['patient_ID']:
            # OPZIONE 1 ********************************************************************
            # alert = msg['e']['n'].split('/')[-1]
            # if alert == "Tachycardia" or alert == "Bradycardia":
            #     alert = msg['e']['n'].split('/')[-1]
            #     action = "contact your patient to make an appointment for a visit."
            #     tosend = f"ATTENTION!\n{alert} detected, you sholud {action}"
            #     self.bot.sendMessage(chat_ID, text=tosend)  #commentato per test
            # elif alert == "Warning/Hypoxia":
            #     alert = alert.split('/')[-1]
            #     action = "contact your patient as soon as possible."
            #     tosend = f"ATTENTION!\n{alert} detected, you sholud {action}"
                
            # elif alert == "Fever" or  alert == "High Fever" or alert == "Hypothermia":
            #     alert = msg['e']['n'].split('/')[-1]
            #     action = "contact your patient as soon as possible."
            #     tosend = f"ATTENTION!\n{alert} detected, you sholud {action}" 
            #     self.bot.sendMessage(chat_ID, text=tosend)
            # OPZIONE 2 ********************************************************************  
                self.SendAlert(msg,chat_ID)
    
    def SendAlert(self, msg, chat_ID):
        alert = msg['e']['n'].split('/')[-1]
        action = "contact your patient as soon as possible."
        tosend = f"ATTENTION!\n{alert} detected, you sholud {action}"
        self.bot.sendMessage(chat_ID, text=tosend, reply_markup=self.keyboard_notify) 
    
if __name__ == '__main__':
    conf = json.load(open("settings.json"))
    conf = json.load(open("settings.json"))
    catalogIP = conf["catalog_address"]
    broker = requests.get(catalogIP+'/broker').text
    port = int(requests.get(catalogIP+'/port').text)
    baseTopic = requests.get(catalogIP+'/base_topic').text
    token = conf["telegramToken"]
    clientID = "PatientMonitoring_22"
    
    PMBot = PatientMonitoringBOT(token, catalogIP, clientID, broker, port, baseTopic)
    PMBot.start()
    print("Bot started ...")
    
    while True:
        time.sleep(10)