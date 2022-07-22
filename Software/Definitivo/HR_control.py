import random 
import json
import requests 
from MyMQTT import * 
import time 
from os.path import exists
from typing import List
from datetime import datetime

class HR_controller: 
    def __init__(self,clientID,topic,broker,port): 
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
        
    def EmergencyHRCheck(self, topic, msg):
        print("topic: {}".format(topic))
        # decompose message
        message=json.loads(msg) 
        name = message['e']['n'] 
        value = message['e']['v'] 
        
        is_response = False   
        # if (name == "oxygen"):        # non ci dovrebbe essere bisogno di queste condizioni perchè controllo il sensore prima di fare l'healthcheck
        if (value>= 60 and  value<= 100):
            #do nothing - Normal heart rate
            pass
        elif (value> 100):
            # Tachycardia
            message['e']['n'] = "Tachycardia" 
            is_response = True   
        elif (value < 60):
            # Bradycardia
            message['e']['n'] = "Bradycardia"
            is_response = True
        else:
            # sensor problem - no value given
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
        sensor_hr = conf["sensors_dict"]["heart rate"]
        
        # CALL microservice here
        t_source = topic.split('/')
        if t_source[-1] == sensor_hr:   # if the sensor is the one corresponding to the hr I'll do the ox check
            # check the value recevied in the method emergencyHealthCheck
            print(f'{name}: {value} {unit} at {time.strftime("%D %H:%M", time.localtime(int(timestamp)))}.')
            response_topic, response = self.EmergencyHRCheck(topic, msg)
            if response is not None:
                print("warning topic: {}".format(response_topic))    
                print(f'{name}: {round(value,2)} {unit} at {time.strftime("%D %H:%M", time.localtime(int(timestamp)))}.') 
                self.client.myPublish(response_topic, response)

if __name__ == '__main__': 
    conf=json.load(open("settings.json"))  
    catalogIP = conf["catalog_address"]
    broker =  conf["broker"]
    port =  conf["port"]
    baseTopic =  conf["baseTopic"]
    token = requests.get(catalogIP+'/token').text
    topic = baseTopic + "/#" 
    
    HR_control = HR_controller("PatientMonitoring_HR_Controller",topic,broker,port) 
    HR_control.run() 

    while True: 
        time.sleep(1) 