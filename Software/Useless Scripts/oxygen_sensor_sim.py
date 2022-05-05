#OXYGEN SENSOR 
 
import random 
import json 
from MyMQTT import * 
import time 
 
class OxygenSensor: 
     
    def __init__(self, baseTopic, patientID, sensorID, broker, port):   #(self, topic, patientID, roomID, patientID, sensorID, broker, port): 
        self.sensorID = str(sensorID) 
        self.patientID = str(patientID) 
        self.topic = self.topic = '/'.join((baseTopic, self.patientID ,self.sensorID))
        self.client = MyMQTT(self.patientID + self.sensorID, broker, port, self) 
        self.__message = { 
            'bn': '/'.join((self.patientID,self.sensorID)), 
            'e': 
                {'n': 'oxygen', 'value': '', 'timestamp': '', 'unit': '%'}, 
        } 
     
    def publish(self,range_): 
      
        message = self.__message 
        if range_ == "normal": 
            # message['bn'] = '/'.join((self.patientID,self.sensorID,range_)) 
            message['e']['value'] = round(random.uniform(95,100), 0)        #the second argument is the number of decimals 
            message['e']['timestamp'] = time.time()
            self.client.myPublish(self.topic,message) 
            print("published") 
        elif range_ == "hypoxia": 
            # message['bn'] = '/'.join((self.patientID,self.sensorID,range_)) 
            message['e']['value'] = round(random.uniform(85,94), 0) 
            message['e']['timestamp'] = time.time() 
            self.client.myPublish(self.topic,message) 
            print("published") 
        elif range_ == "acute_respiratory_failure": 
            # message['bn'] = '/'.join((self.patientID,self.sensorID,range_)) 
            message['e']['value'] = round(random.uniform(50, 84), 0)   #don't know if the minimum should be changed!!
            message['e']['timestamp'] = time.time() 
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
    sensorID = "s_"+"0x01"
    patientID = "p_"+"0x01"
    sensor = OxygenSensor(baseTopic, patientID, sensorID, broker, port) 
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
