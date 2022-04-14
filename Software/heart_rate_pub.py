#HEART RATE SENSOR PUB
 
import random 
import json 
from MyMQTT import * 
import time 
import numpy as np
 
class HeartRateSensor: 
     
    def __init__(self, topic, clientID, sensorID, broker, port):   #(self, topic, clientID, roomID, patientID, sensorID, broker, port): 
        #self.patientID = str(patientID) 
        #self.roomID = str(roomID) 
        self.sensorID = str(sensorID) 
        self.clientID = str(clientID) 
         
        self.topic = topic 
        self.client = MyMQTT(self.sensorID, broker, port, None) 
        self.__message = { 
            'bn': '', 
            'e': 
                {'n': 'heartrate', 'value': '', 'timestamp': '', 'unit': 'bpm'}, 
        } 
     
    def publish(self,range_): 
      
        message = self.__message 
        if range_ == "bradycardia": 
            message['bn'] = '/'.join((self.clientID,self.sensorID,range_)) 
            message['e']['value'] = np.random.exponential(scale=3,size=None)+40 
            message['e']['timestamp'] = time.strftime("%H:%M:%S") 
            self.client.myPublish(self.topic,message) 
            print("published") 
        elif range_ == "normal": 
            message['bn'] = '/'.join((self.clientID,self.sensorID,range_)) 
            loc, scale=80, 3
            message['e']['value'] = np.random.logistic(loc, scale,size=None) 
            message['e']['timestamp'] = time.strftime("%H:%M:%S") 
            self.client.myPublish(self.topic,message) 
            print("published") 
        elif range_ == "tachycardia": 
            message['bn'] = '/'.join((self.clientID,self.sensorID,range_)) 
            message['e']['value'] = np.random.exponential(scale=15,size=None)+100
            message['e']['timestamp'] = time.strftime("%H:%M:%S") 
            self.client.myPublish(self.topic,message) 
            print("published") 
 
    def start(self): 
        self.client.start() 
 
    def stop(self): 
        self.client.stop() 
         
         
if __name__ == "__main__": 
    conf = json.load(open("settings.json")) 
    broker = conf["broker"] 
    port = conf["port"] 
    sensor = HeartRateSensor("/heartrate","annalisa", "sensor3",broker, port) 
    sensor.start() 
    command=input('Available range:\nbradycardia\nnormal\ntachycardia\nquit\n') 
     
    condition = False  
    while command !='quit': 
        if command=='bradycardia' or command=='normal' or command=='tachycardia': 
            condition = True 
            range_ = command 
            break 
        else: 
            print('Wrong range') 
 
 
    while condition == True: 
        sensor.publish(range_) 
        time.sleep(5) 
    sensor.stop() 
