#OXYGEN SENSOR PUB
 
import random 
import json 
from MyMQTT import * 
import time 
 
class OxygenSensor: 
     
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
                {'n': 'oxygen', 'value': '', 'timestamp': '', 'unit': '%'}, 
        } 
     
    def publish(self,range_): 
      
        message = self.__message 
        if range_ == "normal": 
            message['bn'] = '/'.join((self.clientID,self.sensorID,range_)) 
            message['e']['value'] = round(random.uniform(95,100), 0)        #the second argument is the number of decimals 
            message['e']['timestamp'] = time.strftime("%H:%M:%S") 
            self.client.myPublish(self.topic,message) 
            print("published") 
        elif range_ == "hypoxia": 
            message['bn'] = '/'.join((self.clientID,self.sensorID,range_)) 
            message['e']['value'] = round(random.uniform(85,94), 0) 
            message['e']['timestamp'] = time.strftime("%H:%M:%S") 
            self.client.myPublish(self.topic,message) 
            print("published") 
        elif range_ == "acute_respiratory_failure": 
            message['bn'] = '/'.join((self.clientID,self.sensorID,range_)) 
            message['e']['value'] = round(random.uniform(50, 84), 0)   #don't know if the minimum should be changed!!
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
    sensor = OxygenSensor("/oxygen","annalisa", "sensor4",broker, port) 
    sensor.start() 
    command=input('Available range:\nnormal\nhypoxia\nacute_respiratory_failure\nquit\n') 
     
    condition = False  
    while command !='quit': 
        if command=='normal' or command=='hypoxia' or command=='acute_respiratory_failure': 
            condition = True 
            range_ = command 
            break 
        else: 
            print('Wrong range') 
 
 
    while condition == True: 
        sensor.publish(range_) 
        time.sleep(5) 
    sensor.stop() 
