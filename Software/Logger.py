# Logger
 
import random 
import json 
from MyMQTT import * 
import time 
 
class Raspberry_Pie_Logger: 
    def __init__(self,topic,clientID,broker,port): 
        self.clientID=clientID 
        self.topic=topic 
        self.client=MyMQTT(clientID,broker,port,self) 
        self.dict = {"e":[]} 
    def run(self): 
        self.client.start() 
        print('{} has started'.format(self.clientID)) 
        self.client.mySubscribe(self.topic) 
    def end(self): 
        self.client.stop() 
        print('{} has stopped'.format(self.clientID)) 
    def notify(self,topic,msg): 
        message=json.loads(msg) 
        name = message['e']['n'] 
        value = message['e']['value'] 
        unit = message['e']['unit'] 
        time = message['e']['timestamp'] 
        source = topic
        print(f'{source} {name}: {round(value,2)}{unit} at {time}.') 
        # message = message['e'] 
        # self.dict["e"].append(message) 
        # json.dump(self.dict,open("O2test.json","w")) 

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