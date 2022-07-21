from MyMQTT import *
import time
import json
import requests

class Window:
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
            print(f'The window has been opened at time {time.strftime("%D %H:%M", time.localtime(int(timestamp)))}')
        if self.status == 1:
            print(f'The window has been closed at time {time.strftime("%D %H:%M", time.localtime(int(timestamp)))}')

if __name__ == "__main__":
    conf = json.load(open("settings.json"))
    catalogIP = conf["catalog_address"]
    broker = requests.get(catalogIP+'/broker').text
    port = int(requests.get(catalogIP+'/port').text)
    baseTopic = requests.get(catalogIP+'/base_topic').text
    
    topic = baseTopic + "/+/+/Window"
    test = Window("PM_monitoring_window",topic,broker,port)
    test.start()
    
    while True:
        time.sleep(1)
        
	# test.stop()
