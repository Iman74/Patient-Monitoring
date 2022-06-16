
import cherrypy
import requests
import json
import os
import socket
import time

def get_address():
	conf = json.load(open("settings.json"))
	addressCatalog = conf["catalog_address"]
	return addressCatalog

class WebPage:
	def __init__(self):
		self.Catalog=get_address()
	@cherrypy.expose
	def index(self):
		return open("template/homepage.html").read()
	@cherrypy.expose
	def response(self):
		return open("template/response.html").read()
	@cherrypy.expose
	def registration(self):
		return open("template/register.html").read()
	@cherrypy.expose
	def update(self):
		return open("template/update.html").read()
	@cherrypy.expose
	def delete(self):
		return open("template/delete.html").read()
	@cherrypy.expose
	def patient_registration(self):
		return open("template/patient_registration.html").read()
	@cherrypy.expose
	def doctor_registration(self):
		return open("template/doctor_registration.html").read()
	@cherrypy.expose
	def device_registration(self):
		return open("template/device_registration.html").read()
	@cherrypy.expose
	def ms_registration(self):
		return open("template/ms_registration.html").read()
	@cherrypy.expose
	def patient_update(self):
		return open("template/patient_update.html").read()
	@cherrypy.expose
	def doctor_update(self):
		return open("template/doctor_update.html").read()
	@cherrypy.expose
	def device_update(self):
		return open("template/device_update.html").read()
	@cherrypy.expose
	def ms_update(self):
		return open("template/ms_update.html").read()
	@cherrypy.expose
	def user_delete(self):
		return open("template/user_delete.html").read()
	@cherrypy.expose
	def device_delete(self):
		return open("template/device_delete.html").read()
	@cherrypy.expose
	def service_delete(self):
		return open("template/service_delete.html").read()
	
class RestAPI(object):
	exposed = True
	def __init__(self):
		self.filename = "Catalog.json"
		self.file=json.load(open(self.filename, encoding="utf-8"))
		self.settings = json.load(open("settings.json", encoding="utf-8"))
		self.file["broker"] = self.settings["broker"]
		self.file["port"] = self.settings["port"]
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

			elif str(uri[0]) =='ip':
				IP = self.file['broker']
				return IP
			elif str(uri[0]) =='port':
				port = self.file['port']
				return str(port)
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
									doctors[doctor]["patientsList"][patient]["devicesList"][-1]["lastUpdate"]=time.strftime("%d-%m-%Y %H:%M:%S")
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
						return "Device with this deviceID doesn't exist."
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
						if str(uri[1]).lower() == str(services[service]['name']).lower():
							services.pop(service)
							json.dump(self.file,open(self.filename,"w"),indent=4)
							founded = True
							return "Service deleted"
							break
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
			
if __name__=="__main__":
	conf={
		'/':{
	 		'request.dispatch':cherrypy.dispatch.MethodDispatcher(),  
 	 		'tools.sessions.on':True
	 	},
	 	'global':{
	 		'request.dispatch':cherrypy.dispatch.MethodDispatcher(),  
 	 		'tools.sessions.on':True   
	 	}
       }
	cherrypy.config.update({'server.socket_port':9292})
	cherrypy.config.update({'global':{
	 		'request.dispatch':cherrypy.dispatch.MethodDispatcher(),  
 	 		'tools.sessions.on':True   
	 	}})
	try:
		cherrypy.tree.mount(WebPage(),'/',{		"/img": {"tools.staticdir.on": True,
				"tools.staticdir.dir": os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")},
		"/css": {"tools.staticdir.on": True,
              	"tools.staticdir.dir": os.path.join(os.path.dirname(os.path.abspath(__file__)), "css")},
       '/style.css':
                    { 'tools.staticfile.on':True,
                      'tools.staticfile.filename': os.path.abspath("./css/style.css"),
                    } })
		cherrypy.tree.mount(RestAPI(),'/api',{'/':{
	 		'request.dispatch':cherrypy.dispatch.MethodDispatcher(),  
 	 		'tools.sessions.on':True
	 	}})
		
		cherrypy.engine.start()
		while True:
			pass
		cherrypy.engine.block()
	except KeyboardInterrupt:
		print("Stopping the engine")
		exit()