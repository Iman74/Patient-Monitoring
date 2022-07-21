import random 
import json 
from MyMQTT import * 
import time 
from os.path import exists
from typing import List
from datetime import datetime

class OX_Controller: 
    def __init__(self,clientID,topic,broker,port): 
        self.clientID=clientID 
        self.topic=topic 
        self.client=MyMQTT(clientID,broker,port,self) 
        self.message_window = {
                                "bn": "",
                                "e": {"n": "window","v": "","t": "","u": "bool"}
                            } 
    def run(self): 
        self.client.start() 
        print('{} has started'.format(self.clientID)) 
        self.client.mySubscribe(self.topic) 

    def end(self): 
        self.client.stop() 
        print('{} has stopped'.format(self.clientID)) 
        
    def EmergencyOxCheck(self, topic, msg):
        print("topic: {}".format(topic))
        # decompose message
        message=json.loads(msg) 
        name = message['e']['n'] 
        value = message['e']['v'] 
        
        is_response = False   
        # if (name == "oxygen"):        # non ci dovrebbe essere bisogno di queste condizioni perchè controllo il sensore prima di fare l'healthcheck
        if (value >= 95 and  value <= 100):
            # do nothing all right 
            pass   
        elif (value > 85 and  value <= 94):
            # hypoxia
            # print("hypoxia: " +str(name)+" "+str( value))
            message['e']['n']  = "Hypoxia"
            is_response = True
        elif (value >= 0 and  value <= 84):
            # sensor problem - wrong value given
            # print("sensor problem : " +name)
            message['e']['n']  ="Sensor Error"
            is_response = True
        else:
            # sensor problem - no value given
            # print("sensor problem : " +name )
            message['e']['n'] = "Value Error"
            is_response = True
    
        # If an emergency has been detected      
        if is_response == True:
            message['e']['n']= "Warning/" +message['e']['n']
            message['e']['t'] = time.time()
            return topic+"/Warning", message
        
        else:
            return None, None        
        
    def notify(self,topic,msg): 
        message=json.loads(msg) 
        name = message['e']['n'] 
        value = message['e']['v']      
        unit = message['e']['u']      
        timestamp = message['e']['t'] 
        # I take the sensor code
        conf = json.load(open("settings.json"))
        sensor_ox = conf["sensors_dict"]["oxygen"]
        
        # CALL microservice here
        t_source = topic.split('/')
        if t_source[-1] == sensor_ox:   # if the sensor is the one corresponding to the ox I'll do the ox check
            # check the value recevied in the method emergencyHealthCheck
            print(f'{name}: {round(value,2)} {unit} at {time.strftime("%D %H:%M", time.localtime(int(timestamp)))}.')
            response_topic, response = self.EmergencyOxCheck(topic, msg)
            if response is not None:
                print("warning topic: {}".format(response_topic))    
                print(f'{name}: {round(value,2)} {unit} at {time.strftime("%D %H:%M", time.localtime(int(timestamp)))}.') 
                self.client.myPublish(response_topic, response)
                self.RoomAdjust(topic)
            
    def RoomAdjust(self,topic):
        self.window_adjust(topic)
    
    def window_adjust(self,topic):
        action = int(input("Type:\n\
                        0: if you want to open the window\n\
                        1: if you want to close the window\n"))
        
        if action == 0:
            payload = self.message_window.copy()
            payload['e']['v'] = 0              # Open
            payload['e']['t'] = time.time()
            self.client.myPublish(topic+"/Window", payload)
            print("Window Opened")
            
        if action == 1:
            payload = self.message_window.copy()
            payload['e']['v'] = 1              # Closed
            payload['e']['t'] = time.time()
            self.client.myPublish(topic+"/Window", payload)
            print("Window closed")
                
if __name__ == '__main__': 
    conf=json.load(open("settings.json")) 
    broker = conf["broker"] 
    port = conf["port"] 
    baseTopic = conf["baseTopic"]
    topic = baseTopic + "/#" 
    
    OX_Control = OX_Controller("PatientMonitoring_OX_Controller",topic,broker,port) 
    OX_Control.run() 

    while True: 
        time.sleep(1) 