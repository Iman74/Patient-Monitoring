# Logger
 
import random 
import json 
from MyMQTT import * 
import time 
from dataclasses import dataclass
from dataclasses_json import dataclass_json, config
from os.path import exists
from typing import List


class Raspberry_Pie_Logger: 
    def __init__(self,topic,clientID,broker,port): 
        self.clientID=clientID 
        self.topic=topic 
        self.client=MyMQTT(clientID,broker,port,self) 


    def run(self): 
        self.client.start() 
        print('{} has started'.format(self.clientID)) 
        self.client.mySubscribe(self.topic) 

    def end(self): 
        self.client.stop() 
        print('{} has stopped'.format(self.clientID)) 

    def emergencyHealthCheck(self, msg):
        # print("Emergency Health Check")
        # decompose massage
        massage=json.loads(msg) 
        name = massage['e']['n'] 
        value = massage['e']['v'] 
        # unit = massage['e']['unit'] 
        # time = massage['e']['timestamp'] 
        # source = massage['bn'].split('/')
        # patientID = source[-2]
        # sensorID =source[-1]
        if (name == "oxygen"):
            if (value >= 95 and  value <= 100):
            # do nothing all right 
                pass   
            elif (value > 85 and  value <= 94):
                # #hypoxia
                # print("hypoxia: " +str(name)+" "+str( value))
                massage['e']['n']  += " (Hypoxia)"
                return massage
            elif (value >= 0 and  value <= 84):
                #sensor problem
                # print("sensor problem : " +name)
                massage['e']['n']  +=" (Sensor Error)"
                return massage
            else:
                #sensor problem
                # print("sensor problem : " +name )
                massage['e']['n']+= " (Value Error)"
                return massage
        elif (name == "room temperature"):
            if (value>= 20.0 and  value<= 22.0):
                #do nothing all right    Normal Room
                pass
            elif (value> 22.1):
                #Hot Room
                # print("hypoxia: " +name +" "+ value)
                massage['e']['n']+= " (Hot Room)"
                return massage
            elif (value< 19.9):
                #cold Room
                # print("sensor problem : " +name )
                massage['e']['n']+= " (Cold Room)"
                return massage
            else:
                #sensor problem
                # print("sensor problem : " +name )
                massage['e']['n']+= " (Value Error)"
                return massage
        elif (name == "heartrate"):
            if (value>= 60 and  value<= 100):
                #do nothing all right    Normal heart rate
                pass
            elif (value> 100):
                #Hot Room
                # print("hypoxia: " +name +" "+ value)
                massage['e']['n']+= " (Tachycardia)" 
                return massage
            elif (value< 60):
                #cold Room
                # print("sensor problem : " +name )
                massage['e']['n']+= " (Bradycardia)"
                return massage
            else:
                #sensor problem
                # print("sensor problem : " +name )
                massage['e']['n']+= " (Value Error)"
                return massage
        elif (name == "body temperature"):
            if (value>= 35.6 and  value<= 37.4):
                #do nothing all right    Normal Room
                pass
            elif (value>= 37.5 and  value<= 39.4):
                #Hot Room
                # print("hypoxia: " +name +" "+ value)
                massage['e']['n']+= " (Fever)"
                return massage
            elif (value>= 39.5 and  value<= 42):
                #cold Room
                # print("sensor problem : " +name )
                massage['e']['n']+= " (High Fever)"  
                return massage              
            elif (value>= 33.0 and  value<= 35.5):
                #cold Room
                # print("sensor problem : " +name )
                massage['e']['n']+= " (Hypothermia)"
                return massage
            else:
                #sensor problem
                # print("sensor problem : " +name )
                massage['e']['n']+= " (Value Error)"
                return massage

    def notify(self,topic,msg): 
        # massage=json.loads(msg) 
        # name = massage['e']['n'] 
        # value = massage['e']['v'] 
        # unit = massage['e']['u'] 
        # time = massage['e']['t'] 
        # patientID = source[-2]
        # sensorID =source[-1]
        # print(f'{topic} {name}: {round(value,2)}{unit} at {time}.') 
        #process massege
        source = topic.split('/')
        if source[-1] != "Warning":
            response = self.emergencyHealthCheck(msg)
            if response is not None:
                self.client.myPublish(topic+"/Warning",response)
        
if __name__ == '__main__': 
    conf=json.load(open("settings.json")) 
    broker = conf["broker"] 
    port = conf["port"] 
    baseTopic = conf["baseTopic"]
    topic = baseTopic + "/#" 
    RP_Logger = Raspberry_Pie_Logger(topic,"Logger",broker,port) 
    RP_Logger.run() 

    while True: 
        time.sleep(1) 

    test.end()