#ThingSpeak adaptor

import json
from MyMQTT import *
import requests
from datetime import datetime
import time


def get_broker(catalog_url):
	#get message broker, port and baseTopic from Catalog
	broker = requests.get(catalog_url+'/broker').text
	port = int(requests.get(catalog_url+'/port').text)
	baseTopic = requests.get(catalog_url+'/base_topic').text
	return (broker, port, baseTopic)

#REST client to obtain data from the Catalog
class GetData_From_Catalog:

	def __init__(self, Catalog, baseTopic):
		self.Catalog=Catalog
		self.s=requests.Session()
		self.baseTopic=[baseTopic]
		self.patients={}
		self.topics=[]
		self.sensorsID=[]
		self.patientsID=[]
		self.TOPIC=[]
		self.top=[]

	def get_patients(self):
		#get active patients from Catalog
		r=self.s.get(self.Catalog+'/patients')
		self.patients=json.loads(r.text)['patients']
		for i in range (len(self.patients)):
			if bool(self.patients[i]["devicesList"])==False:
			#check if the devices list of each patient is empty
				self.patients.remove(self.patients[i])
		return self.patients

	def get_devices(self):
		#get mqtt devices from active patients
		for i in range (len(self.patients)):
			for j in range (len(self.patients[i-1]["devicesList"])):
				for k in range(len(self.patients[i-1]["devicesList"][j-1]["servicesDetails"])):
					if (self.patients[i-1]["devicesList"][j-1]["servicesDetails"][k-1]["serviceType"]!="MQTT")==True:
						#check if the devices support mqtt connection
						self.patients.remove(self.patients[i-1]["devicesList"][j-1])
		return self.patients

	def get_topics_ID(self):
		for i in range (len(self.patients)):
			for j in range (len(self.patients[i-1]["devicesList"])):
				for k in range(len(self.patients[i-1]["devicesList"][j-1]["servicesDetails"])):
					self.sensorsID.append(self.patients[i-1]["devicesList"][j-1]["deviceID"])
					self.topics.extend(self.patients[i-1]["devicesList"][j-1]["servicesDetails"][k-1]["topic"])
					self.patientsID.append(self.patients[i-1]["userID"])
					#saving topics, sensorID and patientID
		self.patientsID=set(self.patientsID)
		self.patientsID=list(self.patientsID)
		return self.sensorsID, self.patientsID, self.topics

	def gen_topics(self):
		for a in range (len(self.baseTopic)):
			for b in range (len(self.patientsID)):
				for c in range (len(self.sensorsID)):
					bt=str(self.baseTopic[a])
					pid=str(self.patientsID[b])
					sid=str(self.sensorsID[c])
					self.TOPIC.append(bt+'/'+pid+'/'+sid)
		for t in range(len(self.topics)):
			self.top.append(self.TOPIC[t]+self.topics[t])
		return self.top


#MQTT subscriber to obtain sensors' data
class ThingSpeak_subscriber:

	def __init__(self,topic,clientID,broker,port):
		self.clientID=clientID
		self.topic=topic
		self.client=MyMQTT(clientID,broker,port,self)
		self.fieldname=""
		self.value=""
		self.payload = {
		"write_api_key": "N14TC42Q5HCUTOMH",
			"updates": []
			}

	def run(self):
		self.client.start()
		print('{} has started'.format(self.clientID))
		for i in range (len(self.topic)):
			self.client.mySubscribe(self.topic[i])
	def end(self):
		for i in range (len(self.topic)):
			self.client.mySubscribe(self.topic[i])
		self.client.stop()
		print('{} has stopped'.format(self.clientID))

	def notify(self,topic,msg):
		message=json.loads(msg)
		current_time = datetime.now()
		timestamp=int(current_time.timestamp())
		#now=datetime.now()
		if message['e']['n']=='heart rate':
			self.fieldname='field1'
			self.value=float(message['e']['v'])
			self.time=int(message['e']['t'])
		elif message['e']['n']=='oxygen':
			self.fieldname='field2'
			self.value=float(message['e']['v'])
			self.time=int(message['e']['t'])
		elif message['e']['n']=='body temperature':
			self.fieldname='field3'
			self.value=float(message['e']['v'])
			self.time=int(message['e']['t'])
		else:
			self.fieldname='field4'
			self.value=float(message['e']['v'])
			self.time=int(message['e']['t'])
		# ThingSpeak requires ISO 8601 timestamp
		msg = {"created_at": datetime.fromtimestamp(self.time).isoformat(), 
		self.fieldname: self.value}
		if self.time<(timestamp+15):
			msg.update({self.fieldname : self.value})
			#if self.payload['updates'][0]['created_at']!=msg:
				#self.payload['updates'].append(msg)
			#else:
				#self.payload['updates'].update({self.fieldname : self.value})
			self.payload['updates'].append(msg)

	def save_data(self):
		database=self.payload
		self.payload={
		"write_api_key": "N14TC42Q5HCUTOMH",
			"updates": []
			}
		return(database)


if __name__ == "__main__":
	conf = json.load(open("thingspeak_settings.json"))
	QoS=conf["QoS"]
	catalog_url=conf["catalog_address"]
	broker, port, baseTopic=get_broker(catalog_url)
	
	client=GetData_From_Catalog(catalog_url, baseTopic)
	client.get_patients()
	client.get_devices()
	client.get_topics_ID()
	topic=client.gen_topics()

	TS_sub=ThingSpeak_subscriber(topic,'TS'+str(1234), broker, port)
	TS_sub.run()
	while True:
		print(TS_sub.save_data())
		time.sleep(15)
	TS_sub.end()
