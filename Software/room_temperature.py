# PUBLISHER (ROOM TEMPERATURE)

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
                {'n': 'room temperature', 'value': '', 'timestamp': '', 'unit': '°C'},
        }
    
    def publish(self,range_):
     
        message = self.__message
        if range_ == "cold room":
            message['bn'] = '/'.join((self.clientID,self.sensorID,range_))
            message['e']['value'] = round(random.uniform(16,19.9), 1)        #the second argument is the number of decimals
            message['e']['timestamp'] = time.strftime("%H:%M:%S")
            self.client.myPublish(self.topic,message)
            print("published")
        elif range_ == "normal room":
            message['bn'] = '/'.join((self.clientID,self.sensorID,range_))
            message['e']['value'] = round(random.uniform(20,22), 1)
            message['e']['timestamp'] = time.strftime("%H:%M:%S")
            self.client.myPublish(self.topic,message)
            print("published")
        elif range_ == "hot room":
            message['bn'] = '/'.join((self.clientID,self.sensorID,range_))
            message['e']['value'] = round(random.uniform(22.1, 25), 1)
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
    sensor = MyPublisher("/roomtemperature","saras", "sensor1",broker, port)
    sensor.start()
    command=input('Available range:\ncold room\nnormal room\nhot room\nquit\n')
    
    condition = False 
    while command !='quit':
        if command=='cold room' or command=='normal room' or command=='hot room':
            condition = True
            range_ = command
            break
        else:
            print('Wrong range')


    while condition == True:
        sensor.publish(range_)
        time.sleep(5)
    sensor.stop()
