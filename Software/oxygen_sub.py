# OXYGEN SUB
 
import random 
import json 
from MyMQTT import * 
import time 
 
class OxygenManager: 
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
		value = message['e']['value'] 
		unit = message['e']['unit'] 
		time = message['e']['timestamp'] 
		print(f'{self.clientID} measured an oxygen level of {value} {unit} at time {time}.') 
		message = message['e'] 
		self.dict["e"].append(message) 
		json.dump(self.dict,open("O2test.json","w")) 
 
if __name__ == '__main__': 
	conf=json.load(open("settings.json")) 
	broker=conf["broker"] 
	port=conf["port"] 
	topic ="/oxygen" 
	test = OxygenManager(topic,"annalisa",broker,port) 
	test.run() 
 
	while True: 
		time.sleep(1) 
 
	test.end()