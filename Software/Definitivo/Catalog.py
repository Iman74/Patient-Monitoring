import cherrypy
import requests
import json
import time

class RestAPI(object):
	exposed = True
	def __init__(self):
		self.filename = "Catalog.json"
		self.file=json.load(open(self.filename, encoding="utf-8"))
		self.settings = json.load(open("settings.json", encoding="utf-8"))
		# self.file["broker"] = self.settings["broker"]
		# self.file["port"] = self.settings["port"]
		# self.file["baseTopic"] = self.settings["baseTopic"]
		self.file["telegramToken"] = self.settings["telegramToken"]
		self.file["admin"] = self.settings["admin"]
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
						if str(devices[device]['deviceID']) == str(deviceID):
							founded = True
							return json.dumps(devices[device],indent=4)
					if founded != True:
						return "Device not founded"
				else:
					raise cherrypy.HTTPError(400,"Wrong number of uri provided.")

			# VIEWS DEVICES FOR A SPECIFIC PATIENT
			elif str(uri[0])=='devices_p':
				founded = False
				userID = str(uri[1])
				if len(uri)==2:
					founded = False
					doctors = self.file["doctorsList"]
					for doctor in range(len(doctors)):
						for patient in range(len(doctors[doctor]["patientsList"])):
							if str(uri[1]) == str(doctors[doctor]["patientsList"][patient]["userID"]):
								founded = True
								return json.dumps(doctors[doctor]["patientsList"][patient]["devicesList"],indent=4)
					if founded != True:
						return "User not founded"
				else:
					raise cherrypy.HTTPError(400,"Wrong number of uri provided.")
			
			# VIEWS A SPECIFIC DOCTOR
			elif str(uri[0])=='doctor':
				if len(uri)==2:
					founded = False
					doctors = self.getDoctors()['doctors']
					userID = str(uri[1])
					for user in range(len(doctors)):
						if str(doctors[user]['userID']) == str(userID):
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
					if str(patients[user]['userID']) == str(userID):
						founded = True
						return json.dumps(patients[user],indent=4)
				if founded != True:
					return "User not founded"

			# VIEWS PATIENTS FOR A SPECIFIC DOCTOR
			elif str(uri[0])=='patients_doc':
				founded = False
				userID = str(uri[1])
				if len(uri)==2:
					founded = False
					doctors = self.file["doctorsList"]
					for doctor in range(len(doctors)):
						if str(uri[1]) == str(doctors[doctor]['userID']):
							founded = True
							return json.dumps(doctors[doctor]["patientsList"],indent=4)
					if founded != True:
						return "User not founded"
				else:
					raise cherrypy.HTTPError(400,"Wrong number of uri provided.")

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

			# elif str(uri[0]) =='broker':
			# 	broker = self.file['broker']
			# 	return broker
			# elif str(uri[0]) =='port':
			# 	port = self.file['port']
			# 	return str(port)
			elif str(uri[0]) == 'token':
				token = self.file['telegramToken']
				return str(token)
			# elif str(uri[0]) == 'base_topic':
			# 	topic = self.file['baseTopic']
			# 	return str(topic)
			elif str(uri[0])=="admin":
				return json.dumps(self.file["admin"])
			else:
				raise cherrypy.HTTPError(404,"The uri entered is incorrect.")
		else:
			raise cherrypy.HTTPError(400,"No uri provided.")

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
							if str(new['deviceID']) == doctors[doctor]["patientsList"][patient]["devicesList"][device]['deviceID']:
								doctors[doctor]["patientsList"][patient]["devicesList"][device] = new
								self.file["lastUpdate"]=time.strftime("%d-%m-%Y %H:%M:%S")
								doctors[doctor]["patientsList"][patient]["devicesList"][device]["lastUpdate"] = time.strftime("%d-%m-%Y %H:%M:%S")
								json.dump(self.file,open(self.filename,"w"),indent=4)
								founded = True
								return "Device updated"
				if founded != True:
					return "This device doesn't exists."

			# UPDATES A DOCTOR
			elif str(uri[0]) =='doctor':
				founded = False
				new = {}
				new = cherrypy.request.json
				doctors = self.file["doctorsList"]
				for doctor in range(len(doctors)):
					if str(new['userID']) == doctors[doctor]['userID']:
						doctors[doctor] = new
						self.file["lastUpdate"]=time.strftime("%d-%m-%Y %H:%M:%S")
						json.dump(self.file,open(self.filename,"w"),indent=4)
						founded = True
						return "User updated"
				if founded != True:
					return "This doctor doesn't exists."

			# UPDATES A PATIENT
			elif str(uri[0]) =='patient':
				founded = False
				new = {}
				new = cherrypy.request.json
				doctors = self.file["doctorsList"]
				for doctor in range(len(doctors)):
					for patient in range(len(doctors[doctor]["patientsList"])):
						if str(new['userID']) == doctors[doctor]["patientsList"][patient]['userID']:
							doctors[doctor]["patientsList"][patient] = new
							self.file["lastUpdate"]=time.strftime("%d-%m-%Y %H:%M:%S")
							json.dump(self.file,open(self.filename,"w"),indent=4)
							founded = True
							return "User updated"
				if founded != True:
					return "This patient doesn't exists."


			# UPDATES A SERVICE
			elif str(uri[0]) == 'microservice':
				founded = False
				services = self.file['microservices']
				new = {}
				new = cherrypy.request.json
				for service in range(len(services)):
					service_name = services[service]['name']
					if str(new['name']) == str(service_name):
						services[service] = new
						self.file['microservices'] = services
						self.file["lastUpdate"]=time.strftime("%d-%m-%Y %H:%M:%S")
						json.dump(self.file,open(self.filename,"w"),indent=4)
						founded = True
						return "Microservice updated"
				if founded != True:
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
					for doctor in range(len(doctors)):
						for patient in range(len(doctors[doctor]["patientsList"])):
							if str(uri[1]) == doctors[doctor]["patientsList"][patient]["userID"]:
								for device in range(len(doctors[doctor]["patientsList"][patient]["devicesList"])):
									if str(new['deviceID']) == doctors[doctor]["patientsList"][patient]["devicesList"][device]['deviceID']:
										founded = True
										return "A device with this ID already exists."			
					if founded != True:
						for doctor in range(len(doctors)):
							for patient in range(len(doctors[doctor]["patientsList"])):
								if str(uri[1]) == doctors[doctor]["patientsList"][patient]["userID"]:
									doctors[doctor]["patientsList"][patient]["devicesList"].append(new)
									self.file["lastUpdate"]=time.strftime("%d-%m-%Y %H:%M:%S")
									doctors[doctor]["patientsList"][patient]["devicesList"][device]['timestamp']=time.strftime("%d-%m-%Y %H:%M:%S")
									json.dump(self.file,open(self.filename,"w"),indent=4)
									return "Device registered."						
				else:
					raise cherrypy.HTTPError(400,"Wrong number of uri provided.")


			# ADDS A NEW DOCTOR
			elif str(uri[0])=='doctor':
				founded = False
				new = {}
				new = cherrypy.request.json
				doctors = self.file["doctorsList"]
				for doctor in range(len(doctors)):
					if str(new['userID']) == doctors[doctor]['userID']:
						founded = True
						return "A doctor with this ID already exists."
				if founded != True:
					doctors.append(new)
					self.file["lastUpdate"]=time.strftime("%d-%m-%Y %H:%M:%S")
					json.dump(self.file,open(self.filename,"w"),indent=4)
					return "Doctor registered."

			# ADDS A NEW PATIENT
			elif str(uri[0])=='patient':
				if len(uri)==2:
					founded = False
					new = {}
					new = cherrypy.request.json
					doctors = self.file["doctorsList"]
					for doctor in range(len(doctors)):
						if str(uri[1]) == doctors[doctor]['userID']:
							for patient in range(len(doctors[doctor]["patientsList"])):
								if str(new['userID']) == doctors[doctor]["patientsList"][patient]["userID"]:
									founded = True
									return "A patient with this ID already exists."
					if founded != True:
						for doctor in doctors:
							if str(uri[1]) == doctor['userID']:
								doctor["patientsList"].append(new)
								self.file["lastUpdate"]=time.strftime("%d-%m-%Y %H:%M:%S")
								json.dump(self.file,open(self.filename,"w"),indent=4)
								return "Patient registered."		
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
						return "A service with this ID already exists."
				if founded != True:
					services.append(new)
					self.file["microservices"] = services
					self.file["lastUpdate"]=time.strftime("%d-%m-%Y %H:%M:%S")
					json.dump(self.file,open(self.filename,"w"),indent=4)
					return "Microservice registered"				
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
						for patient in range(len(doctors[doctor]["patientsList"])):
							for device in range(len(doctors[doctor]["patientsList"][patient]["devicesList"])):
								if str(uri[1])== str(doctors[doctor]["patientsList"][patient]["devicesList"][device]['deviceID']):
									doctors[doctor]["patientsList"][patient]["devicesList"].pop(device)
									self.file["lastUpdate"]=time.strftime("%d-%m-%Y %H:%M:%S")
									json.dump(self.file,open(self.filename,"w"),indent=4)
									founded = True
									return "Device deleted"
					if founded != True:
						return "Device with this deviceID doesn't exist."
				else:
					raise cherrypy.HTTPError(400,"Wrong number of uri provided.")

			# DELETE A DOCTOR
			elif str(uri[0]) == 'doctor':
				if len(uri)==2:
					founded = False
					doctors = self.file["doctorsList"]
					for doctor in range(len(doctors)):
						if str(uri[1]) == str(doctors[doctor]['userID']):
							doctors.pop(doctor)
							json.dump(self.file,open(self.filename,"w"),indent=4)
							founded = True
							return "User deleted"
					if founded == False:
						return "This user doesn't exists."
				else:
					raise cherrypy.HTTPError(400,"Wrong number of uri provided.")

			# DELETE A PATIENT
			elif str(uri[0]) == 'patient':
				if len(uri)==2:
					founded = False
					doctors = self.file["doctorsList"]
					for doctor in range(len(doctors)):
						for patient in range(len(doctors[doctor]["patientsList"])):
							if str(uri[1]) == str(doctors[doctor]["patientsList"][patient]['userID']):
								doctors[doctor]["patientsList"].pop(patient)
								self.file["lastUpdate"]=time.strftime("%d-%m-%Y %H:%M:%S")
								json.dump(self.file,open(self.filename,"w"),indent=4)
								founded = True
								return "User deleted"
					if founded == False:
						return "This patient doesn't exists."
				else:
					raise cherrypy.HTTPError(400,"Wrong number of uri provided.")

			# DELETE A SERVICE
			elif str(uri[0]) == 'microservice':
				if len(uri)==2:
					founded = False
					services = self.file['microservices']
					for service in range(len(services)):
						if str(uri[1]).lower() == str(services[service]['name']).lower():
							services.pop(service)
							json.dump(self.file,open(self.filename,"w"),indent=4)
							founded = True
							return "Service deleted"
					if founded != True:
						return "Service with this name doesn't exist."
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

