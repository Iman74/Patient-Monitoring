import json
import time
import random
import requests
import numpy as np
from MyMQTT import *

# Here the sensor search itself in the Catalog to see to which patient own.
def find_me(deviceID):
    founded = False
    settings = json.load(open("settings.json", encoding="utf-8"))
    addressCatalog = settings["catalog_address"]
    patients = requests.get(addressCatalog+'/patients')
    patients = patients.json()
    patients = patients['patients']
    for patient in range(len(patients)):
        try:
            for device in range(len(patients[patient]["devicesList"])):
                if str(deviceID) == str(patients[patient]["devicesList"][device]["deviceID"]):
                    patientID = patients[patient]['userID']
                    founded = True
                    return str(patientID)
                    raise StopIteration
        except StopIteration:
            break

def update_me(deviceID,info_sensor):
    settings = json.load(open("settings.json", encoding="utf-8"))
    addressCatalog = settings["catalog_address"]
    #payload = json.dumps(info_sensor)
    payload = info_sensor
    r = requests.put(addressCatalog+"/device", json=payload)
    # update to stay "alive" in the catalog and update the timestamp


def HeartRateSensor(range_,sensorID,broker):
    info_sensor = {
                "deviceID": sensorID,
                "deviceName": "SensorHR",
                "measureType": "heartrate",
                "availableServices": "MQTT",
                "servicesDetails": [{
                                    "serviceType": "MQTT",
                                    "serviceIP": broker,
                                    "topic": [
                                        "/heartRate"
                                    ]}
                                ],
                            "lastUpdate": ""
                }
    patientID = find_me(sensorID)
    update_me(sensorID,info_sensor)
    # check if patientID has been acquired correctly
    if patientID:
        message = { 
                'bn': '/'.join((patientID,sensorID)), 
                'e': 
                    {'n': 'heartrate', 'v': '', 't': '', 'u': 'bpm'}
            } 
        condition = False  
        while range_ !='quit': 
            if range_=='bradycardia' or range_=='normal' or range_=='tachycardia': 
                condition = True 
                break 
            else: 
                print('Wrong range')

        if range_ == "bradycardia": 
            message['e']['v'] = np.random.exponential(scale=3,size=None)+40 
            message['e']['t'] = time.time()
        elif range_ == "normal": 
            loc, scale=80, 3
            message['e']['v'] = np.random.logistic(loc, scale,size=None) 
            message['e']['t'] = time.time()
        elif range_ == "tachycardia": 
            message['e']['v'] = np.random.exponential(scale=15,size=None)+100
            message['e']['t'] = time.time()
        return message
    else:
        return "Device not registered for any patient"
def RoomTempratureSensor(range_,sensorID,broker):
    info_sensor = {
                "deviceID": sensorID,
                "deviceName": "SensorRT",
                "measureType": "temperature",
                "availableServices": "MQTT",
                "servicesDetails": [{
                                    "serviceType": "MQTT",
                                    "serviceIP": broker,
                                    "topic": [
                                        "/roomTemperature"
                                    ]}
                                ],
                            "lastUpdate": ""
                }
    patientID = find_me(sensorID)
    update_me(sensorID,info_sensor)
    # check if patientID has been acquired correctly
    if patientID:
        message = { 
                'bn': '/'.join((patientID,sensorID)),
                'e':
                    {'n': 'room temperature', 'v': '', 't': '', 'u': '°C'}
            }
        
        condition = False 
        while range_ !='quit':
            if range_=='cold room' or range_=='normal room' or range_=='hot room':
                condition = True
                break
            else:
                print('Wrong range')

        if range_ == "cold room":
            message['e']['v'] = round(random.uniform(16,19.9), 1)        #the second argument is the number of decimals
            message['e']['t'] = time.time()
        elif range_ == "normal room":
            message['e']['v'] = round(random.uniform(20,22), 1)
            message['e']['t'] = time.time()
        elif range_ == "hot room":
            message['e']['v'] = round(random.uniform(22.1, 25), 1)
            message['e']['t'] = time.time()
        return message
    else:
        return "Device not registered for any patient"

def OxygenSensor(range_,sensorID,broker):
    info_sensor = {
                "deviceID": sensorID, 
                "deviceName": "SensorO",
                "measureType": "heartrate",
                "availableServices": "MQTT",
                "servicesDetails": [{
                                    "serviceType": "MQTT",
                                    "serviceIP": broker,
                                    "topic": [
                                        "/oxygen"
                                    ]}
                                ],
                            "lastUpdate": ""
                }
    patientID = find_me(sensorID)
    update_me(sensorID,info_sensor)
    # check if patientID has been acquired correctly
    if patientID:
        message = { 
                'bn': '/'.join((patientID,sensorID)), 
                'e': 
                    {'n': 'oxygen', 'v': '', 't': '', 'u': '%'}
            }
        condition = False  
        while range_ !='quit': 
            if range_=='normal' or range_=='hypoxia' or range_=='acute_respiratory_failure': 
                condition = True 
                break 
            else: 
                print('Wrong range') 
        if range_ == "normal": 
            message['e']['v'] = round(random.uniform(95,100), 0)        #the second argument is the number of decimals 
            message['e']['t'] = time.time()
        elif range_ == "hypoxia": 
            message['e']['v'] = round(random.uniform(85,94), 0) 
            message['e']['t'] = time.time() 
        elif range_ == "acute_respiratory_failure": 
            message['e']['v'] = round(random.uniform(50, 84), 0)   #don't know if the minimum should be changed!!
            message['e']['t'] = time.time() 
        return message
    else:
        return "Device not registered for any patient"
def BodyTempratureSensor(range_,sensorID,broker):
    info_sensor = {
                "deviceID": sensorID,
                "deviceName": "SensorBT",
                "measureType": "temperature",
                "availableServices": "MQTT",
                "servicesDetails": [{
                                    "serviceType": "MQTT",
                                    "serviceIP": broker,
                                    "topic": [
                                        "/bodyTemperature"
                                    ]}
                                ],
                            "lastUpdate": ""
                }
    patientID = find_me(sensorID)
    update_me(sensorID,info_sensor)
    # check if patientID has been acquired correctly
    if patientID:
        message = { 
                'bn': '/'.join((patientID,sensorID)),
                'e':
                    {'n': 'body temperature', 'v': '', 't': '', 'u': '°C'}
            }
        condition = False 
        while range_ !='quit':
            if range_=='hypothermia' or range_=='normal' or range_=='fever' or range_=='highfever':
                condition = True
                break
            else:
                print('Wrong range')

        if range_ == "hypothermia":
            message['e']['v'] = round(random.uniform(33,35.5), 1)        #the second argument is the number of decimals
            message['e']['t'] = time.time()
        elif range_ == "normal":
            message['e']['v'] = round(random.uniform(35.6,37.4), 1)
            message['e']['t'] = time.time()
        elif range_ == "fever":
            message['e']['v'] = round(random.uniform(37.5, 39.4), 1)
            message['e']['t'] = time.time()
        elif range_ == "highfever":
            message['e']['v'] = round(random.uniform(39.5, 42), 1)
            message['e']['t'] = time.time()
        return message
    else:
        return "Device not registered for any patient"

class Publisher:
    def __init__(self, baseTopic, topic, broker, port):
        self.topic = topic
        self.client = MyMQTT(baseTopic, broker, port, None)
        self.__message = {
                            "bn": "",
                            "e": {
                                "n": "","v": "","t": "","u": ""
                            }
                        }

    def publish(self,message_h,message_o,message_bT,message_rT):
        for t in self.topic:
            message = self.__message

            if t == "/roomTemperature":
                patientID, sensorID = message_rT['bn'].split('/')
                message = self.__message
                message['bn'] = '/'.join((patientID,sensorID,t))
                message['e']['n'] = 'room temperature'
                message['e']['v'] = message_rT['e']['v']
                message['e']['t'] = message_rT['e']['t']
                message['e']['u'] = 'C'

            elif t == "/bodyTemperature":
                patientID, sensorID = message_bT['bn'].split('/')
                message = self.__message
                message['bn'] = '/'.join((patientID,sensorID,t))
                message['e']['n'] = 'body temperature'
                message['e']['v'] = message_bT['e']['v']
                message['e']['t'] = message_bT['e']['t']
                message['e']['u'] = 'C'

            elif t == "/heartRate":
                patientID, sensorID = message_h['bn'].split('/')
                message = self.__message
                message['bn'] = '/'.join((patientID,sensorID,t))
                message['e']['n'] = 'heart rate'
                message['e']['v'] = message_h['e']['v']
                message['e']['t'] = message_h['e']['t']
                message['e']['u'] = 'bpm'

            elif t == "/oxygen":
                patientID, sensorID = message_o['bn'].split('/')
                message = self.__message
                message['bn'] = '/'.join((patientID,sensorID,t))
                message['e']['n'] = 'oxygen'
                message['e']['v'] = message_o['e']['v']
                message['e']['t'] = message_o['e']['t']
                message['e']['u'] = '%'
            topic_ = '/'.join((baseTopic,patientID,sensorID))
            # topic_ = topic_+t
            # json.dumps(message)
            self.client.myPublish(topic_,message)
            print(f"\nPublished on {topic_}")

    def start(self):
        self.client.start()

    def stop(self):
        self.client.stop()


if __name__ == "__main__":
    conf = json.load(open("settings.json"))
    addressCatalog = conf["catalog_address"]
    broker =  conf["broker"]
    port =  conf["port"]
    baseTopic =  conf["baseTopic"]

    sensorID_o = "s_"+"0x01"
    sensorID_rT = "s_"+"0x02"
    sensorID_h = "s_"+"0x03"
    sensorID_bT = "s_"+"0x04"

    sensor = Publisher(baseTopic,["/roomTemperature","/bodyTemperature",
                          "/heartRate","/oxygen"], broker, port)
    sensor.start()
    range_h="normal"
    range_rT="cold room"
    range_bT="normal"
    range_o="hypoxia"
    # range_h=input('\nAvailable range:\nbradycardia\nnormal\ntachycardia\nquit\n') 
    # range_rT = input('\nAvailable range:\ncold room\nnormal room\nhot room\nquit\n')
    # range_bT = input('\nAvailable range:\nhypothermia\nnormal\nfever\nhighfever\nquit\n')
    # range_o = input('\nAvailable range:\nnormal\nhypoxia\nacute_respiratory_failure\nquit\n') 
    while True:
        message_h = HeartRateSensor(range_h,sensorID_h,broker)
        message_rT = RoomTempratureSensor(range_rT,sensorID_rT,broker)
        message_bT = BodyTempratureSensor(range_bT,sensorID_bT,broker)
        message_o = OxygenSensor(range_o,sensorID_o,broker)
        if message_o == "Device not registered for any patient" or message_rT == "Device not registered for any patient" or message_bT == "Device not registered for any patient" or message_h == "Device not registered for any patient":
            print('A sensor is not registered in the catalog.')
            break  
        sensor.publish(message_h,message_o,message_bT,message_rT)
        time.sleep(5) #ThingSpeak can load data max every 15 seconds
    sensor.stop()


