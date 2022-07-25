from MyMQTT import *
import time
import json
import requests

class CentralHeating:
    def __init__(self, clientID, topic,broker,port):
        self.client=MyMQTT(clientID,broker,port,self)
        self.topic=topic
        self.status=None

    def start (self):
        self.client.start()
        self.client.mySubscribe(self.topic)

    def stop (self):
        self.client.stop()
			
    def notify(self,topic,msg):
        d=json.loads(msg)
        self.status=d['e']['v']
        timestamp=d['e']['t']
        
        if self.status == 0:
            print(f'The central heating has been switched on {time.strftime("%D %H:%M", time.localtime(int(timestamp)))}')
        if self.status == 1:
            print(f'The central heating has been switched off {time.strftime("%D %H:%M", time.localtime(int(timestamp)))}')
    def register_me(self, addressCatalog): 
        info_service = {
                "name": "Central Heating",
                "endpoint": self.topic,
                "protocol": "MQTT"
        }
        #payload = json.dumps(info_sensor) 
        payload = info_service 
        r = requests.post(addressCatalog+"/microservice", json=payload)      

if __name__ == "__main__":
    conf = json.load(open("settings.json"))
    catalogIP = conf["catalog_address"]
    broker =  conf["broker"]
    port =  conf["port"]
    baseTopic =  conf["baseTopic"]
    
    topic = baseTopic + "/+/+/Heating"
    service = CentralHeating("PM_monitoring_heating",topic,broker,port)
    service.start()
    service.register_me(catalogIP)

    while True:
        time.sleep(1)
        
    service.stop()
