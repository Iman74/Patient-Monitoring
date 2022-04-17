# PUBLISHER (ROOM TEMPERATURE)

import random
import json
from MyMQTT import *
import time

class RoomTempratureSensor:
    
    def __init__(self, baseTopic, patientID, sensorID, broker, port):   #(self, topic, patientID, roomID, patientID, sensorID, broker, port):
        self.sensorID = str(sensorID)
        self.patientID = str(patientID)
        self.topic = '/'.join((baseTopic, self.patientID ,self.sensorID))
        self.client = MyMQTT(self.patientID + self.sensorID, broker, port, self)
        self.__message = {
            'bn': '/'.join((self.patientID,self.sensorID)), 
            'e':
                {'n': 'room temperature', 'value': '', 'timestamp': '', 'unit': '°C'},
        }
    
    def publish(self,range_):
     
        message = self.__message
        if range_ == "cold room":
            # message['bn'] = '/'.join((self.patientID, self.sensorID ,range_))
            message['e']['value'] = round(random.uniform(16,19.9), 1)        #the second argument is the number of decimals
            message['e']['timestamp'] = time.strftime("%H:%M:%S")
            self.client.myPublish(self.topic,message)
            print("published")
        elif range_ == "normal room":
            # message['bn'] = '/'.join((self.patientID,self.sensorID,range_))
            message['e']['value'] = round(random.uniform(20,22), 1)
            message['e']['timestamp'] = time.strftime("%H:%M:%S")
            self.client.myPublish(self.topic,message)
            print("published")
        elif range_ == "hot room":
            # message['bn'] = '/'.join((self.patientID,self.sensorID,range_))
            message['e']['value'] = round(random.uniform(22.1, 25), 1)
            message['e']['timestamp'] = time.strftime("%H:%M:%S")
            self.client.myPublish(self.topic,message)
            print("published")

    def notify(self,topic,msg):
        payload=json.loads(msg)
        print(json.dumps(payload,indent=4))

    def start(self):
        self.client.start()

    def stop(self):
        self.client.stop()
        
        
if __name__ == "__main__":
    conf = json.load(open("settings.json"))
    broker = conf["broker"]
    port = conf["port"]
    baseTopic = conf["baseTopic"]
    sensorID = "s_"+"0x02"
    patientID = "p_"+"0x01"
    sensor = RoomTempratureSensor(baseTopic, patientID, sensorID, broker, port)
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
