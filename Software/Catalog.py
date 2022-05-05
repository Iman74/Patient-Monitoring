import cherrypy
import json
import time 
import requests

class Catalog:
	exposed=True
	def __init__(self):
		self.filename = "Catalog.json"
		self.file=json.load(open(self.filename, encoding="utf-8"))
		self.settings = json.load(open("settings.json", encoding="utf-8"))
		self.file["broker"] = self.settings["broker"]
		self.file["port"] = self.settings["port"]
		self.file["telegramToken"] = self.settings["telegramToken"]
		self.file["baseTopic"] = self.settings["baseTopic"]
		json.dump(self.file,open(self.filename,"w"),indent=4)

	def GET(self,*uri,**params):
		if len(uri) != 0:
			# LISTS ALL DEVICE
			if str(uri[0])=='devices':
				devices = self.getDevices()
				return json.dumps(devices,indent=4)
		
			# LISTS ALL DOCTORS
			elif str(uri[0])=='doctors':
				doctors = self.getDoctors()
				return json.dumps(doctors,indent=4)

			# LISTS ALL PATIENTS	
			elif str(uri[0])=='patients':
				patients = self.getPatients()
				return json.dumps(patients,indent=4)

			# LISTS ALL MICROSERVICES
			elif str(uri[0])=='microservices':
				return json.dumps(self.file['microservices'],indent=4)

			# VIEWS A SPECIFIC DEVICE
			elif str(uri[0])=='device':
				if len(uri) == 2:
					founded = False
					devices = self.getDevices()['devices']
					deviceID = str(uri[1])
					for device in range(len(devices)):
						if str(devices[device]['deviceID']) == deviceID:
							founded = True
							return json.dumps(devices[device],indent=4)
					if founded != True:
						return "Device not founded"
				else:
					raise cherrypy.HTTPError(400,"Wrong number of uri provided.")

			# VIEWS A SPECIFIC DOCTOR
			elif str(uri[0])=='doctor':
				if len(uri)==2:
					founded = False
					doctors = self.getDoctors()['doctors']
					userID = str(uri[1])
					for user in range(len(doctors)):
						if str(doctors[user]['userID']) == userID:
							founded = True
							return json.dumps(doctors[user],indent=4)
					if founded != True:
						return "User not founded"
				else:
					raise cherrypy.HTTPError(400,"Wrong number of uri provided.")

			# VIEWS A SPECIFIC PATIENT
			elif str(uri[0])=='patient':
				founded = False
				patients = self.getPatients()['patients']
				userID = str(uri[1])
				for user in range(len(patients)):
					if str(patients[user]['userID']) == userID:
						founded = True
						return json.dumps(patients[user],indent=4)
				if founded != True:
					return "User not founded"

			# VIEWS A SPECIFIC MICROSERVICE
			elif str(uri[0])=='microservice':
				founded = False
				services = self.file['microservices']
				name = str(uri[1])
				for service in range(len(services)):
					if str(services[service]['name']).lower() == name:
						founded = True
						return json.dumps(services[service],indent=4)
				if founded != True:
					return "Microservice not founded"

			elif str(uri[0]) =='broker':
				broker = self.file['broker']
				return broker
			elif str(uri[0]) =='port':
				port = self.file['port']
				return str(port)
			elif str(uri[0]) == 'token':
				token = self.file['telegramToken']
				return str(token)
			elif str(uri[0]) == 'base_topic':
				topic = self.file['baseTopic']
				return str(topic)
			else:
				raise cherrypy.HTTPError(404,"The uri entered is incorrect.")
		else:
			return "Homepage."

	@cherrypy.tools.json_in()
	def PUT(self,*uri,**params):  
		if len(uri) != 0:
			# UPDATES A DEVICE
			if str(uri[0])=='device':
				founded = False
				new = {}
				new = cherrypy.request.json
				doctors = self.file["doctorsList"]
				for doctor in range(len(doctors)):
					for patient in range(len(doctors[doctor]["patientsList"])):
						for device in range(len(doctors[doctor]["patientsList"][patient]["devicesList"])):
							if new['deviceID'] == doctors[doctor]["patientsList"][patient]["devicesList"][device]['deviceID']:
								doctors[doctor]["patientsList"][patient]["devicesList"][device] = new
								self.file["lastUpdate"]=time.strftime("%d-%m-%Y %H:%M:%S")
								doctors[doctor]["patientsList"][patient]["devicesList"][device]["lastUpdate"] = time.strftime("%d-%m-%Y %H:%M:%S")
								json.dump(self.file,open(self.filename,"w"),indent=4)
								founded = True
								return "Device updated"
								break
							else:
								pass

				if founded == False:
					return "This device doesn't exists."

			# UPDATES A USER
			elif str(uri[0]) =='user':
				founded = False
				new = {}
				new = cherrypy.request.json
				doctors = self.file["doctorsList"]
				try:
					for doctor in range(len(doctors)):
						if new['userID'] == doctors[doctor]['userID']:
							doctors[doctor] = new
							json.dump(self.file,open(self.filename,"w"))
							founded = True
							return "User updated"
							break
						else:
							for patient in range(len(doctors[doctor]["patientsList"])):
								if new['userID'] == doctors[doctor]["patientsList"][patient]['userID']:
									doctors[doctor]["patientsList"][patient] = new
									self.file["lastUpdate"]=time.strftime("%d-%m-%Y %H:%M:%S")
									json.dump(self.file,open(self.filename,"w"),indent=4)
									founded = True
									return "User updated"
									raise StopIteration
				except StopIteration:
					pass

				if founded == False:
					return "This user doesn't exists."

			# UPDATES A SERVICE
			elif str(uri[0]) == 'microservice':
				founded = False
				services = self.file['microservices']
				new = {}
				new = cherrypy.request.json
				for service in range(len(services)):
					if new['name'] == services[service]['name']:
						services[service] = new
						self.file['microservices'] = services
						self.file["lastUpdate"]=time.strftime("%d-%m-%Y %H:%M:%S")
						json.dump(self.file,open(self.filename,"w"),indent=4)
						founded = True
						return "Microservice updated"
						break
					else:
						pass
				if founded == False:
					return "This microservice doesn't exists."

			else:
				raise cherrypy.HTTPError(404,"The uri entered is incorrect.")
		else: 
			raise cherrypy.HTTPError(400,"No uri provided.")
			

	@cherrypy.tools.json_in()
	#@cherrypy.tools.json_out()
	def POST(self,*uri,**params): 
		if len(uri) != 0:
			# ADDS A NEW DEVICE
			if str(uri[0])=='device':
				if len(uri) == 2:
					founded = False
					new = {}
					new = cherrypy.request.json
					doctors = self.file["doctorsList"]
					try:
						for doctor in range(len(doctors)):
							for patient in range(len(doctors[doctor]["patientsList"])):
								if str(uri[1]) == str(doctors[doctor]["patientsList"][patient]["userID"]):
									for device in range(len(doctors[doctor]["patientsList"][patient]["devicesList"])):
										if new['deviceID'] == doctors[doctor]["patientsList"][patient]["devicesList"][device]['deviceID']:
											founded = True
											raise StopIteration
					except StopIteration:
						pass
										
					if founded != True:
						for doctor in range(len(doctors)):
							for patient in range(len(doctors[doctor]["patientsList"])):
								if str(uri[1]) == str(doctors[doctor]["patientsList"][patient]["userID"]):
									doctors[doctor]["patientsList"][patient]["devicesList"].append(new)
									self.file["lastUpdate"]=time.strftime("%d-%m-%Y %H:%M:%S")
									doctors[doctor]["patientsList"][patient]["devicesList"][device]['timestamp']=time.strftime("%d-%m-%Y %H:%M:%S")
									json.dump(self.file,open(self.filename,"w"),indent=4)
									return json.dumps(doctors[doctor]["patientsList"][patient]["devicesList"],indent=4)
					else:
						return "A device with this ID already exists."
				else:
					raise cherrypy.HTTPError(400,"Wrong number of uri provided.")


			# ADDS A NEW DOCTOR
			elif str(uri[0])=='doctor':
				founded = False
				new = {}
				new = cherrypy.request.json
				doctors = self.file["doctorsList"]
				for doctor in range(len(doctors)):
					if str(new['userID']) == str(doctors[doctor]['userID']):
						founded = True
						break
				if founded != True:
					doctors.append(new)
					self.file["lastUpdate"]=time.strftime("%d-%m-%Y %H:%M:%S")
					json.dump(self.file,open(self.filename,"w"),indent=4)
					return json.dumps(doctors,indent=4)
				else:
					return "A doctor with this ID already exists."

			# ADDS A NEW PATIENT
			elif str(uri[0])=='patient':
				if len(uri)==2:
					founded = False
					new = {}
					new = cherrypy.request.json
					doctors = self.file["doctorsList"]
					for doctor in range(len(doctors)):
						if str(uri[1]) == str(doctors[doctor]['userID']):
							for patient in range(len(doctors[doctor]["patientsList"])):
								if str(new['userID']) == str(doctors[doctor]["patientsList"][patient]["userID"]):
									founded = True
					if founded != True:
						for doctor in range(len(doctors)):
							if str(uri[1]) == str(doctors[doctor]['userID']):
								doctors[doctor]["patientsList"].append(new)
								self.file["lastUpdate"]=time.strftime("%d-%m-%Y %H:%M:%S")
								json.dump(self.file,open(self.filename,"w"),indent=4)
						return json.dumps(doctors[doctor]["patientsList"],indent=4)
					else:
						return "A patient with this ID already exists."
				else:
					raise cherrypy.HTTPError(400,"Wrong number of uri provided.")

			# ADDS A NEW SERVICE
			elif str(uri[0])=='microservice':
				founded = False
				services = self.file['microservices']
				new = {}
				new = cherrypy.request.json
				for service in range(len(services)):
					if str(new['name']) == str(services[service]['name']).lower():
						founded = True
						break
				if founded != True:
					services.append(new)
					self.file["microservices"] = services
					self.file["lastUpdate"]=time.strftime("%d-%m-%Y %H:%M:%S")
					json.dump(self.file,open(self.filename,"w"),indent=4)
					return json.dumps(services,indent=4)
				else:
					return "A service with this ID already exists."
			else:
				raise cherrypy.HTTPError(404,"The uri entered is incorrect.")
		else: 
			raise cherrypy.HTTPError(400,"No uri provided.")


	def DELETE(self,*uri,**params): 
		if len(uri) != 0:
			# DELETE A DEVICE
			if str(uri[0]) == 'device':
				if len(uri)==2:
					founded = False
					doctors = self.file["doctorsList"]
					for doctor in range(len(doctors)):
						try:
							for patient in range(len(doctors[doctor]["patientsList"])):
								for device in range(len(doctors[doctor]["patientsList"][patient]["devicesList"])):
									if str(uri[1])== str(doctors[doctor]["patientsList"][patient]["devicesList"][device]['deviceID']):
										doctors[doctor]["patientsList"][patient]["devicesList"].pop(device)
										self.file["lastUpdate"]=time.strftime("%d-%m-%Y %H:%M:%S")
										json.dump(self.file,open(self.filename,"w"),indent=4)
										founded = True
										return "Device deleted"
										raise StopIteration
										
						except StopIteration:
							break
					if founded != True:
						print("Device with this deviceID doesn't exist.")
				else:
					raise cherrypy.HTTPError(400,"Wrong number of uri provided.")

			# DELETE A USER
			elif str(uri[0]) == 'user':
				if len(uri)==2:
					founded = False
					doctors = self.file["doctorsList"]
					for doctor in range(len(doctors)):
						if str(uri[1]) == str(doctors[doctor]['userID']):
							doctors.pop(doctor)
							json.dump(self.file,open(self.filename,"w"),indent=4)
							founded = True
							return "User deleted"
							break
						else:
							try:
								for patient in range(len(doctors[doctor]["patientsList"])):
									if str(uri[1]) == str(doctors[doctor]["patientsList"][patient]['userID']):
										doctors[doctor]["patientsList"].pop(patient)
										self.file["lastUpdate"]=time.strftime("%d-%m-%Y %H:%M:%S")
										json.dump(self.file,open(self.filename,"w"),indent=4)
										founded = True
										return "User deleted"
										raise StopIteration
							except StopIteration:
								pass

					if founded == False:
						return "This user doesn't exists."
				else:
					raise cherrypy.HTTPError(400,"Wrong number of uri provided.")

			# DELETE A SERVICE
			elif str(uri[0]) == 'microservice':
				if len(uri)==2:
					founded = False
					services = self.file['microservices']
					for service in range(len(services)):
						if str(uri[1]) == str(services[service]['name']).lower():
							services.pop(service)
							json.dump(self.file,open(self.filename,"w"),indent=4)
							founded = True
							return "Service deleted"
							break
					if founded != True:
						print("Service with this name doesn't exist.")
				else:
					raise cherrypy.HTTPError(400,"Wrong number of uri provided.")
			else:
				raise cherrypy.HTTPError(404,"The uri entered is incorrect.")
		else: 
			raise cherrypy.HTTPError(400,"No uri provided.")

	def getDevices(self):
		devices = {"devices":[]}
		for doctor in range(len(self.file["doctorsList"])):
			for patient in range(len(self.file["doctorsList"][doctor]["patientsList"])):
				for device in range(len(self.file["doctorsList"][doctor]["patientsList"][patient]["devicesList"])):
					devices["devices"].append(self.file["doctorsList"][doctor]["patientsList"][patient]["devicesList"][device])
		return devices

	def getDoctors(self):
		doctors = {"doctors": []}
		for doctor in range(len(self.file["doctorsList"])):
			doctors["doctors"].append(self.file["doctorsList"][doctor])
		return doctors

	def getPatients(self):
		patients = {"patients": []}
		for doctor in range(len(self.file["doctorsList"])):
			for patient in range(len(self.file["doctorsList"][doctor]["patientsList"])):
				patients["patients"].append(self.file["doctorsList"][doctor]["patientsList"][patient])
		return patients
				
# Removes all the devices with timestamp higher than two minutes. 
# 	def deleteOld(self):
# 		#file=json.load(open(self.filename, encoding="utf-8"))
# 		devices = self.file['devicesList']
# 		for device in range(len(devices)):
# 			if int(time.mktime(time.strptime(devices[device]['lastUpdate'],"%d-%m-%Y %H:%M:%S"))) + 60*2 < time.time():
# 				del devices[device]
# 				self.file['devicesList'] = devices
# 				json.dump(self.file,open(self.filename,"w"))
# 			else:
# 				pass

def addDev(json_file=0):
	if json_file:
		new = json_file
	else:
		new = {
				"deviceID": "",
				"deviceName": "",
				"measureType": "",
				"availableServices": "",
				"servicesDetails": []
				}
		new["deviceID"] = input("Insert the deviceID: ")
		new["deviceName"] = input("Insert the device name: ")
		new["measureType"] = (input("Write all types of measurements by separating them with a space: ")).split(" ")
		new["availableServices"] = (input("Write all services available by separating them with a space: ")).split(" ")
		
		for service in range(len(new["availableServices"])):
			newS = {
					"serviceType": new["availableServices"][service],
					"serviceIP": "",
					}
			if "MQTT" == new["availableServices"][service]:
				topic = (input("Write all the topics of service "+str(service)+" by separating them with a space: ")).split(" ")
				newS["topic"] = topic
				newS["serviceType"] = "MQTT"
			elif "REST" == new["availableServices"][service]:
				newS["serviceType"] = "REST"
			newS["serviceIP"] = input("What is the IP of the service "+str(service)+"?")
			new["servicesDetails"].append(newS)
	return new

def addDoc(json_file=0):
	if json_file:
		new = json_file
	else:
		new = {
			"name": "",
		  	"userID": "",
		  	"password": "",
		  	"telegramID": "",
			"patientsList": []
		}
		new["name"] = input("Insert name and surname: ")
		new["userID"] =  input("Insert the userID: ")
		new["password"] = input("Insert the password: ")
		new["telegramID"] = input("Insert the telegramID: ")
	return new


def addPatient(json_file=0):
	if json_file:
		new = json_file
	else:
		new = {
				"name": "" ,
				"userID": "",
				"password": "",
				"telegramID": "",
				"thingspeak_chID": "",
				"thingspeak_rkey": "",
				"thingspeak_wkey": "",
				"devicesList": []
				}
		new["name"] = input("Insert name and surname: ")
		new["userID"] =  input("Insert the userID: ")
		new["password"] =  input("Insert the password: ")
		new["telegramID"] = input("Insert the telegramID: ")
		new["thingSpeak_chID"] =  input("Insert the Thingspeak channel ID: ")
		new["thingSpeak_rkey"] = input("Insert the Thingspeak read API: ")
		new["thingSpeak_wkey"] =  input("Insert the Thingspeak write API: ")
		while True:
			command = input("Do you want to add a new device?\n y:\t yes\n n:\t no\n")
			if command == 'yes':
				new["deviceList"].append(upDev())
			elif command == 'no':
				break
			else:
				print("This command doesn't exists, retry:\n")
	return new

def addServ(json_file=0):
	if json_file:
		new = json_file
	else:
		new = {
				"name":"",
				"endpoint":"",
				"protocol": "",
		}
		new["name"] = input("Insert the name: ")
		new["endpoint"] =  input("Insert the endpoint: ")
		new["protocol"] =  input("Insert the protocol: ")
	return new

def upDev(addressCatalog,json_file=0):
	if json_file:
		new = json_file
	else:
		deviceID = input("Insert the deviceID: ")
		new = requests.get(addressCatalog+'/device/'+deviceID)
		while True:
			command = input("What param do you want to update?\n n:\t name\n m:\t measure type\n a:\t available services\n d:\t service details\
				\n q:\t quit\n")
			if command == 'n':
				new["deviceName"] = (input("Insert the device name: ")).split(" ")
			elif command == 'm':
				new["measureType"] = (input("Write all types of measurements by separating them with a space: ")).split(" ")
			elif command == 'a':
				new["availableServices"] =( input("Write all services available by separating them with a space: ")).split(" ")
				# HERE WE WANT ALSO ADD DETAILS OF THE NEW SERVICES?
			elif command == 'd':
				service == input("Write the name of the service you want to update details.")
				newS = {
							"serviceType": service,
							"serviceIP": "",
							}
				if "MQTT" == new["availableServices"][service]:
					topic = (input("Write all the topics of service "+str(service)+" by separating them with a space: ")).split(" ")
					newS["topic"] = topic
					newS["serviceType"] = "MQTT"
				elif "REST" == new["availableServices"][service]:
					newS["serviceType"] = "REST"
				newS["serviceIP"] = input("What is the IP of the service "+str(service)+"?")
				new["servicesDetails"].append(newS)
			elif command == 'q':
				break
			else:
				print("This command doesn't exists, retry:\n")
	return new


def upUser(addressCatalog,json_file=0):
	if json_file:
		new = json_file
	else:
		while True:
			command = input("Doctor or patient?\n d:\t doctor\n p:\t patient\n q:\t quit\n")
			if command == 'd':
				userID = input("Insert the userID: ")
				new = requests.get(addressCatalog+"/doctor/"+userID)
				new = new.json()
				command = input("What param do you want to update?\n n:\t name\n p:\t password\n q:\t quit\n")
				if command == 'n':
					new["name"] = input("Insert name and surname: ")
				elif command == 'p':
					new["password"] = input("Insert the new password: ")
				elif command == 'q':
					break
				else:
					print("This command doesn't exists, retry:\n")
			elif command == 'p':
				userID = input("Insert the userID: ")
				new = requests.get(addressCatalog+"/patient/"+userID)
				new = new.json()
				command = input("What param do you want to update?\n n:\t name\n pw:\t password\n tel:\t telegramID\n ch:\t Thingspeak channel ID\n\
			 rkey:\t thingspeak_rkey\n wkey:\t thingspeak_wkey\n d:\t devices list\n q:\t quit\n")
				if command == 'n':
					new["name"] = input("Insert name and surname: ")
				elif command == "pw":
					new["password"] = input("Insert the new password: ")
				elif command == 'tel':
					new["telegramID"] = input("Insert the telegramID: ")
				elif command == 'ch':
					ch =  input("Insert the Thingspeak channel ID: ")
				elif command == 'rkey':
					thingSpeak_rkey = input("Insert the Thingspeak read API: ")
				elif command == 'wkey':
					thingSpeak_wkey =  input("Insert the Thingspeak write API: ")
				elif command == 'd':
					new["deviceList"].append(upDev())
				elif command == 'q':
					break
				else:
					print("This command doesn't exists, retry.\n")
			elif command == 'q':
				break
			else:
				print("This command doesn't exists, retry.\n")			
	return new

def upServ(addressCatalog,json_file=0):
	if json_file:
		new = json_file
	else:
		name = input("Insert the name: ")		
		new = requests.get(addressCatalog+"/microservice/"+name)
		new = new.json()
		while True:
			command = input("What param do you want to update?\n e:\t endpoint\n p:\t protocol\n q:\t quit")
			if command == 'e':
				new["endpoint"] =  input("Insert the endpoint: ")
			elif command =='p':
				new["protocol"] =  input("Insert the protocol: ")
			elif command == 'q':
				break
			else:
				print("This command doesn't exists, retry:\n")
	return new

def main():
	settings = json.load(open("settings.json", encoding="utf-8"))
	addressCatalog = settings["catalog_address"]
	print("Welcome in the Catalog Adaptor.\n")
	while True: 
		command=input('Do you want to update, add or delete an entry?\n Available commands:\n a:\t add\n u:\t update\n d:\t delete\n q:\t quit\n')
		# ADD
		if command =='a':
			command=input("What do you want to add?\n u:\t user\n d:\t device\n s:\t service\n q:\t quit\n")
			if command == 'u':
				command = input("Doctor or patient?\n d:\t doctor\n p:\t patient\n q:\t quit\n")
				if command == 'd':
					command=input("Do you want to enter user parameters via command line or json?\
						\n cm:\t command line\n j:\t json\n q:\t quit\n")
					if command == 'j':
						filename_new=input("Insert name of the json: ")
						new_user=json.load(open(fielename_new, encoding="utf-8"))
						payload = addDoc(new_user)
						r = requests.post(addressCatalog+"/doctor", json=payload)
						# print the response of the request 
						print(r.text)

					elif command == 'cm':
						payload = addDoc()
						r = requests.post(addressCatalog+"/doctor", json=payload)
						print(r.text)
					elif command == 'q':
						break
					else:
						print("This command doesn't exists, retry:\n")
				elif command == 'p':
					userID = input("Enter the user ID of the doctor to whom this patient has to be added: ")
					command=input("Do you want to enter user parameters via command line or json?\
						\n cm:\t command line\n j:\t json\n q:\t quit\n")
					if command == 'j':
						filename_new=input("Insert name of the json: ")
						new_user=json.load(open(fielename_new, encoding="utf-8"))
						payload = addDoc(new_user)
						r = requests.post(addressCatalog+"/patient/"+userID, json=payload)
						print(r.text)

					elif command == 'cm':
						payload = addDoc()
						r = requests.post(addressCatalog+"/patient/"+userID, json=payload)
						print(r.text)
					elif command == 'q':
						break
					else:
						print("This command doesn't exists, retry:\n")
				elif command == 'q':
					break

				else:
					print("This command doesn't exists, retry:\n")

			elif command == 'd':
				userID = input("Enter the user ID of the patient to whom this device has to be added: ")
				command=input("Do you want to enter device parameters via command line or json?\
					\n cm:\t command line\n j:\t json\n q:\t quit\n")
				if command == 'j':
					filename_new=input("Insert name of the json: ")
					new_dev=json.load(open(fielename_new, encoding="utf-8"))
					payload = addDev(new_dev)
					r = requests.post(addressCatalog+"/device/"+userID,json=payload)
					print(r.text)
				elif command == 'cm':
					payload = addDev()
					r = requests.post(addressCatalog+"/device/"+userID, json=payload)
					print(r.text)
				elif command == 'q':
					break
					
				else:
					print("This command doesn't exists, retry:\n")

			elif command == 's':
				command=input("Do you want to enter microservice parameters via command line or json?\
					\n cm:\t command line\n j:\t json\n q:\t quit")
				if command == 'j':
					filename_new=input("Insert name of the json: ")
					new_Serv=json.load(open(fielename_new, encoding="utf-8"))
					payload = addServ(new_serv)
					r = requests.post(addressCatalog+"/microservice", json=payload)
					print(r.text)
				elif command == 'cm':
					payload = addServ(new_serv)
					r = requests.post(addressCatalog+"/microservice", json=payload)
					print(r.text)
				elif command == 'q':
					break
					
				else:
					print("This command doesn't exists, retry:\n")

			elif command == 'q':
				break
			else:
				print("This command doesn't exists, retry:\n")

		elif command =='u':
			command=input("What do you want to update?\n u:\t user\n d:\t device\n s:\t service\n q:\t quit\n")
			if command == 'u':
				command=input("Do you want to enter user parameters via command line or json?\
					\n cm:\t command line\n j:\t json\n q:\t quit\n")
				if command == 'j':
					filename_new=input("Insert name of the json: ")
					new_user=json.load(open(fielename_new, encoding="utf-8"))
					payload = upUser(addressCatalog,new_user)
					r = requests.put(addressCatalog+"/user", json=payload)
					print(r.text)
				elif command == 'cm':

					payload = upUser(addressCatalog)
					r = requests.put(addressCatalog+"/user", json=payload)
					print(r.text)
				elif command == 'q':
					break

				else:
					print("This command doesn't exists, retry:\n")
			elif command == 'd':
				command=input("Do you want to enter device parameters via command line or json?\
					\n cm:\t command line\n j:\t json\n q:\t quit\n")
				if command == 'j':
					filename_new=input("Insert name of the json: ")
					new_dev=json.load(open(fielename_new, encoding="utf-8"))
					payload,userID = upDev(addressCatalog,new_dev)
					r = requests.put(addressCatalog+"/device", json=payload)
					print(r.text)
				elif command == 'cm':
					payload,userID = upDev(addressCatalog)
					r = requests.put(addressCatalog+"/device", json=payload)
					print(r.text)
				elif command == 'q':
					break
					
				else:
					print("This command doesn't exists, retry:\n")
			elif command == 's':
				command=input("Do you want to enter microservice parameters via command line or json?\
					\n cm:\t command line\n j:\t json\n q:\t quit\n")
				if command == 'j':
					filename_new=input("Insert name of the json: ")
					new_Serv=json.load(open(fielename_new, encoding="utf-8"))
					payload = upServ(addressCatalog,new_serv)
					r = requests.put(addressCatalog+"/microservice", json=payload)
					print(r.text)
				elif command == 'cm':
					payload = upServ(addressCatalog)
					r = requests.put(addressCatalog+"/microservice", json=payload)
					print(r.text)
			elif command == 'q':
				break
			else:
				print("This command doesn't exists, retry:\n")
		elif command =='a':
			command=input("What do you want to delete?\n u:\t user\n d:\t device\n s:\t service\n q:\t quit\n")
			if command == 'u':
				userID = input("Enter the userID of the user you want to delete: ")
				r = requests.delete(addressCatalog+"/user/"+userID)
				print(r.text)
			elif command == 'd':
				deviceID = input("Enter the userID of the device you want to delete: ")
				r = requests.delete(addressCatalog+"/device/"+deviceID)
				print(r.text)
			elif command == 's':
				serviceID = input("Enter the userID of the microservice you want to delete: ")
				r = requests.delete(addressCatalog+"/microservice/"+serviceID)
				print(r.text)
			elif command == 'q':
				break
			else:
				print("This command doesn't exists, retry:\n")

		elif command == 'q':
			print("Goodbye!")
			break
		else:
			print("This command doesn't exists, retry:\n")
	return

if __name__=="__main__":

	conf={
		'/':{
			'request.dispatch':cherrypy.dispatch.MethodDispatcher(),  
 			'tools.sessions.on':True   
		}
	}

	catalog = Catalog()
	cherrypy.tree.mount(catalog,'/',conf)
	cherrypy.config.update({'server.socket_port':9090})
	cherrypy.config.update(conf)
	cherrypy.engine.start()
	main()
	cherrypy.engine.block()
