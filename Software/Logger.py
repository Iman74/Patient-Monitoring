# Logger
 
import random 
import json 
from MyMQTT import * 
import time 
from dataclasses import dataclass
from dataclasses_json import dataclass_json, config
from os.path import exists
from typing import List

@dataclass_json
@dataclass(frozen=True)
class _SensorData:
    value: str 
    timestamp: str 
@dataclass_json
@dataclass(frozen=True)
class _Sensor:
    name: str 
    unit: str 
    sensorID: str
    data: List[_SensorData]
@dataclass_json
@dataclass(frozen=True)
class _Patient:
    patientID: str 
    sensors: List[_Sensor]
@dataclass_json
@dataclass(frozen=True)
class _Database:
    patients: List[_Patient]


class Raspberry_Pie_Logger: 
    def __init__(self,topic,clientID,broker,port): 
        self.clientID=clientID 
        self.topic=topic 
        self.client=MyMQTT(clientID,broker,port,self) 
        self.databaseName = "Patients_DataBase.json"
        # self._dict = { 
        #     'patient': '', 
        #     'sensorsLog': 
        #         {'name': '', 'unit': '', 'data':
        #                                                 {'value': '', 'timestamp': ''}}, 
        # } 

    def run(self): 
        self.client.start() 
        print('{} has started'.format(self.clientID)) 
        self.client.mySubscribe(self.topic) 

    def end(self): 
        self.client.stop() 
        print('{} has stopped'.format(self.clientID)) 

    def updateDatabase(self, patientID, sensorID, sensorName, sensorUnit, value, timestamp):

        newData = _SensorData(value, timestamp)

        #check if the file is existed
        file_exists = exists(self.databaseName)
        if(file_exists):
            # read current database
            with open(self.databaseName, "r") as jsonFile:
                try:
                    database = _Database.from_json(json.load(jsonFile))
                    patientExisted = False
                    for patient in database.patients:
                        if patient.patientID == patientID:
                            #Patient is existed
                            patientExisted = True
                            sensorExisted = False
                            for sensor in patient.sensors:
                                if (sensor.sensorID == sensorID and 
                                    sensor.name == sensorName and
                                    sensor.unit == sensorUnit):
                                    #Sensor is existed for the patient
                                    sensorExisted = True
                                    sensor.data.append(newData)
                            if sensorExisted == False:
                                #Sensor is not existed for this patient, add sensor
                                newsensor = _Sensor(sensorName, sensorUnit, sensorID, [newData])
                                patient.sensors.append(newsensor)
                                print(f'sensor "{sensorID}" added') 
                    if patientExisted == False:
                        #Patient is not existed, add patient
                        newsensor = _Sensor(sensorName, sensorUnit, sensorID, [newData])
                        newpatient = _Patient(patientID, [newsensor])
                        database.patients.append(newpatient)
                        print(f'patient "{patientID}" added') 
                except Exception as e:
                    print(e)
           

        else:
            #initialize the database
            newsensor = _Sensor(sensorName, sensorUnit, sensorID, [newData])
            newpatient = _Patient(patientID, [newsensor])
            database = _Database([newpatient])
            print(f'Database initailized')

        # save Changes to database
        with open(self.databaseName, "w") as jsonFile:
            try:
                json.dump(database.to_json(indent=4), jsonFile)
            except Exception as e:
                print(e)



    def notify(self,topic,msg): 
        message=json.loads(msg) 
        name = message['e']['n'] 
        value = message['e']['value'] 
        unit = message['e']['unit'] 
        time = message['e']['timestamp'] 
        source = message['bn'].split('/')
        patientID = source[-2]
        sensorID =source[-1]
        print(f'{topic} {name}: {round(value,2)}{unit} at {time}.') 
        #save
        self.updateDatabase(patientID, sensorID, name, unit, value, time)
        
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