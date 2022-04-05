# PUBLISHER (BODY TEMPERATURE)

import random
import json
from MyMQTT import *
import time

class MyPublisher:
    
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
                {'n': 'body temperature', 'value': '', 'timestamp': '', 'unit': '°C'},
        }
    
    def publish(self,range_):
     
        message = self.__message
        if range_ == "hypothermia":
            message['bn'] = '/'.join((self.clientID,self.sensorID,range_))
            message['e']['value'] = round(random.uniform(33,35.5), 1)        #the second argument is the number of decimals
            message['e']['timestamp'] = time.strftime("%H:%M:%S")
            self.client.myPublish(self.topic,message)
            print("published")
        elif range_ == "normal":
            message['bn'] = '/'.join((self.clientID,self.sensorID,range_))
            message['e']['value'] = round(random.uniform(35.6,37.4), 1)
            message['e']['timestamp'] = time.strftime("%H:%M:%S")
            self.client.myPublish(self.topic,message)
            print("published")
        elif range_ == "fever":
            message['bn'] = '/'.join((self.clientID,self.sensorID,range_))
            message['e']['value'] = round(random.uniform(37.5, 39.4), 1)
            message['e']['timestamp'] = time.strftime("%H:%M:%S")
            self.client.myPublish(self.topic,message)
            print("published")
        elif range_ == "highfever":
            message['bn'] = '/'.join((self.clientID,self.sensorID,range_))
            message['e']['value'] = round(random.uniform(39.5, 42), 1)
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
    sensor = MyPublisher("/bodytemperature","saras", "sensor1",broker, port)
    sensor.start()
    command=input('Available range:\nhypothermia\nnormal\nfever\nhighfever\nquit\n')
    
    condition = False 
    while command !='quit':
        if command=='hypothermia' or command=='normal' or command=='fever' or command=='highfever':
            condition = True
            range_ = command
            break
        else:
            print('Wrong range')


    while condition == True:
        sensor.publish(range_)
        time.sleep(5)
    sensor.stop()
