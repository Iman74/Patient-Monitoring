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

    def emergencyHealthCheck(self, topic, msg):
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
        
        is_response = False
        if (name == "oxygen"):
            if (value >= 95 and  value <= 100):
            # do nothing all right 
                pass   
            elif (value > 85 and  value <= 94):
                # #hypoxia
                # print("hypoxia: " +str(name)+" "+str( value))
                massage['e']['n']  = "Hypoxia"
                is_response = True
            elif (value >= 0 and  value <= 84):
                #sensor problem
                # print("sensor problem : " +name)
                massage['e']['n']  ="Sensor Error"
                is_response = True
            else:
                #sensor problem
                # print("sensor problem : " +name )
                massage['e']['n'] = "Value Error"
                is_response = True
        elif (name == "room temperature"):
            if (value>= 20.0 and  value<= 22.0):
                #do nothing all right    Normal Room
                pass
            elif (value> 22.0 and value< 50.0):
                #Hot Room
                # print("hypoxia: " +name +" "+ value)
                massage['e']['n'] = "Hot Room"
                # is_response = True
            elif (value < 20.0 and value > -10.0):
                #cold Room
                # print("sensor problem : " +name )
                massage['e']['n'] = "Cold Room"
                # is_response = True
            else:
                #sensor problem
                # print("sensor problem : " +name )
                massage['e']['n'] = "Value Error"
                is_response = True
        elif (name == "heartrate"):
            if (value>= 60 and  value<= 100):
                #do nothing all right    Normal heart rate
                pass
            elif (value> 100):
                #Hot Room
                # print("hypoxia: " +name +" "+ value)
                massage['e']['n'] = "Tachycardia" 
                is_response = True
            elif (value< 60):
                #cold Room
                # print("sensor problem : " +name )
                massage['e']['n'] = "Bradycardia"
                is_response = True
            else:
                #sensor problem
                # print("sensor problem : " +name )
                massage['e']['n'] = "Value Error"
                is_response = True
        elif (name == "body temperature"):
            if (value>= 35.6 and  value<= 37.4):
                #do nothing all right    Normal Room
                pass
            elif (value>= 37.5 and  value<= 39.4):
                #Hot Room
                # print("hypoxia: " +name +" "+ value)
                massage['e']['n'] = "Fever"
                is_response = True
            elif (value>= 39.5 and  value<= 42):
                #cold Room
                # print("sensor problem : " +name )
                massage['e']['n'] = "High Fever"  
                is_response = True              
            elif (value>= 33.0 and  value<= 35.5):
                #cold Room
                # print("sensor problem : " +name )
                massage['e']['n'] = "Hypothermia"
                is_response = True
            else:
                #sensor problem
                # print("sensor problem : " +name )
                massage['e']['n'] = "Value Error"
                is_response = True
        #
        if is_response == True:
            massage['e']['n']= "Warning/" +massage['e']['n']
            massage['e']['t'] = time.time()
            # json.dumps(massage)
            return topic+"/Warning", massage
        else:
            return None, None
    def roomAdjustments(self, topic, msg):
        # print("Emergency Health Check")
        # decompose massage
        massage=json.loads(msg) 
        name = massage['e']['n'] 
        value = massage['e']['v'] 
        # unit = massage['e']['unit'] 
        # time = massage['e']['timestamp'] 
        source = massage['bn'].split('/')
        patientID = source[-2]
        # sensorID =source[-1]
        is_response = False
        response_massage = { 
                'bn': patientID +"/" +"RoomCommand", 
                'e': 
                    {'n': '', 'v': '', 't': '', 'u': ''}
            } 
        if (name == "room temperature"):
            if (value>= 20.0 and  value<= 22.0):
                #do nothing all right    Normal Room
                pass
            elif (value> 22.1 and value<= 25.0):
                #warm Room
                massage['e']['n']= "HeatingSystem"
                massage['e']['v'] = 0
                massage['e']['u'] = "bool Off(0)/On(0)"
                is_response = True
            elif (value> 25.0):
                #Hot Room
                massage['e']['n']= "Windows"
                massage['e']['v'] = 0
                massage['e']['u'] = "bool (Open(0)/Close(1)"
                is_response = True
            elif (value< 19.9 and value>= 17):
                #chill Room
                massage['e']['n']= "Windows"
                massage['e']['v'] = 1
                massage['e']['u'] = "bool (Open(0)/Close(1)"
                is_response = True
            elif (value< 17):
                #cold Room
                massage['e']['n']= "HeatingSystem"
                massage['e']['v'] = 1
                massage['e']['u'] = "bool Off(0)/On(0)"
                is_response = True
            else:
                #sensor problem
                pass
                # print("sensor problem : " +name )
                # massage['e']['n'] = " (Value Error)"
                # is_response = True
        #
        if is_response == True:
            response_massage['e']['t'] = time.strftime("%d-%m-%Y %H:%M:%S")
            # json.dumps(response_massage)
            t_source = topic.split('/')
            t_source.pop() #remove sensor id
            topic = "/".join(t_source)
            return topic+"/RoomCommand", massage
        else:
            return None, None
    def notify(self,topic,msg): 
        massage=json.loads(msg) 
        name = massage['e']['n'] 
        value = massage['e']['v'] 
        unit = massage['e']['u'] 
        time = massage['e']['t'] 
        # patientID = source[-2]
        # sensorID =source[-1]
        print(f'{topic} {name}: {round(value,2)}{unit} at {time}.') 
        #process massege
        t_source = topic.split('/')
        # CALL microservices here
        if t_source[-1] != "Warning" and t_source[-1] != "RoomCommand":
            response_topic, response = self.emergencyHealthCheck(topic, msg)
            if response is not None:
                self.client.myPublish(response_topic, response)
            response_topic, response = self.roomAdjustments(topic, msg)
            if response is not None:
                self.client.myPublish(response_topic, response)
        
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