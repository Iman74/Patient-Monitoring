
import cherrypy
import requests
import json
import os
import time

def get_address():
	conf = json.load(open("settings.json"))
	addressCatalog = conf["catalog_address"]
	return addressCatalog

class WebPage:
	def __init__(self):
		pass
		
	# WebPage paths
	@cherrypy.expose
	def index(self):
		return open("template/homepage.html").read()				# Homepage
	@cherrypy.expose
	def admin_index(self):
		return open("template/admin_index.html").read()				# list of possible operations for admin
	@cherrypy.expose
	def patient_index(self):
		return open("template/patient_index.html").read() 			# list of possible operations for patients
	@cherrypy.expose
	def doctor_index(self):
		return open("template/doctor_index.html").read()			# list of possible operations for doctors
	@cherrypy.expose
	def admin_login(self):
		return open("template/admin_login.html").read()				# login as admin
	@cherrypy.expose
	def patient_login(self):
		return open("template/patient_login.html").read()			# login as patient
	@cherrypy.expose
	def doctor_login(self):
		return open("template/doctor_login.html").read()			# login as doctor
	@cherrypy.expose
	def d_doctor_update(self):
		return open("template/d_doctor_update.html").read() 		# update personal data when logged as doctor
	@cherrypy.expose
	def d_doctor_view(self):
		return open("template/d_doctor_view.html").read()  			# view personal data of doctor logged
	@cherrypy.expose
	def d_patient_registration(self):
		return open("template/d_patient_registration.html").read()  # register a patient for doctor logged
	@cherrypy.expose
	def d_patients_view(self):
		return open("template/d_patients_view.html").read()			# view all patients of doctor logged
	@cherrypy.expose
	def p_device_registration(self):
		return open("template/p_device_registration.html").read()   # register a device for patient logged
	@cherrypy.expose
	def p_devices_view(self):
		return open("template/p_devices_view.html").read()			# view all devices of patient logged
	@cherrypy.expose
	def p_patient_update(self):
		return open("template/p_patient_update.html").read()	    # update personal data when logged as patient
	@cherrypy.expose
	def p_patient_view(self):
		return open("template/p_patient_view.html").read()			# view personal data of patient logged
	@cherrypy.expose
	def view(self):
		return open("template/view.html").read()					# possible view operations as admin
	@cherrypy.expose
	def patient(self):
		return open("template/patient_view.html").read()			# view info of a specific patient
	@cherrypy.expose
	def all_patients(self):
		return open("template/all_patients.html").read()			# view all patients in the catalog
	@cherrypy.expose
	def doctor(self):
		return open("template/doctor_view.html").read()				# view info of a specific doctor
	@cherrypy.expose
	def all_doctors(self):
		return open("template/all_doctors.html").read()				# view all doctors in the catalog
	@cherrypy.expose
	def device(self):
		return open("template/device_view.html").read()				# view info of a specific device
	@cherrypy.expose
	def all_devices(self):
		return open("template/all_devices.html").read()				# view all devices in the catalog
	@cherrypy.expose
	def service(self):
		return open("template/service_view.html").read()			# view info of a specific microservice
	@cherrypy.expose
	def all_services(self):
		return open("template/all_services.html").read()			# view all microservices in the catalog
	@cherrypy.expose
	def registration(self):
		return open("template/register.html").read()				# possible register operations as admin
	@cherrypy.expose
	def update(self):
		return open("template/update.html").read()					# possible update operations as admin
	@cherrypy.expose
	def delete(self):
		return open("template/delete.html").read()					# possible delete operations as admin
	@cherrypy.expose
	def patient_registration(self):
		return open("template/patient_registration.html").read()	# register a patient
	@cherrypy.expose
	def doctor_registration(self):
		return open("template/doctor_registration.html").read()		# register a doctor
	@cherrypy.expose
	def device_registration(self):
		return open("template/device_registration.html").read()		# register a device
	@cherrypy.expose
	def ms_registration(self):
		return open("template/service_registration.html").read()	# register a microservice
	@cherrypy.expose
	def patient_update(self):
		return open("template/patient_update.html").read()			# update a patient
	@cherrypy.expose
	def doctor_update(self):
		return open("template/doctor_update.html").read()			# update a doctor
	@cherrypy.expose
	def device_update(self):
		return open("template/device_update.html").read()			# update a device
	@cherrypy.expose
	def service_update(self):
		return open("template/service_update.html").read()			# update a microservice
	@cherrypy.expose
	def user_delete(self):
		return open("template/user_delete.html").read()				# delete a user (both doctors and patients)
	@cherrypy.expose
	def device_delete(self):
		return open("template/device_delete.html").read()			# delete a device
	@cherrypy.expose
	def service_delete(self):
		return open("template/service_delete.html").read()			# delete a microservice
	
class RestAPI(object):
	exposed = True
	def __init__(self):
		self.filename = "Catalog.json"
		self.file=json.load(open(self.filename, encoding="utf-8"))
		self.settings = json.load(open("settings.json", encoding="utf-8"))
		self.file["broker"] = self.settings["broker"]
		self.file["port"] = self.settings["port"]
		self.file["telegramToken"] = self.settings["telegramToken"]
		self.file["baseTopic"] = self.settings["baseTopic"]
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
							if str(new['deviceID']) == str(doctors[doctor]["patientsList"][patient]["devicesList"][device]['deviceID']):
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
					if str(new['userID']) == str(doctors[doctor]['userID']):
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
						if str(new['userID']) == str(doctors[doctor]["patientsList"][patient]['userID']):
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
					if str(new['name']) == str(services[service]['name']):
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
							if str(uri[1]) == str(doctors[doctor]["patientsList"][patient]["userID"]):
								for device in range(len(doctors[doctor]["patientsList"][patient]["devicesList"])):
									if str(new['deviceID']) == str(doctors[doctor]["patientsList"][patient]["devicesList"][device]['deviceID']):
										founded = True
										return "A device with this ID already exists."			
					if founded != True:
						for doctor in range(len(doctors)):
							for patient in range(len(doctors[doctor]["patientsList"])):
								if str(uri[1]) == str(doctors[doctor]["patientsList"][patient]["userID"]):
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
					if str(new['userID']) == str(doctors[doctor]['userID']):
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
						if str(uri[1]) == str(doctors[doctor]['userID']):
							for patient in range(len(doctors[doctor]["patientsList"])):
								if str(new['userID']) == str(doctors[doctor]["patientsList"][patient]["userID"]):
									founded = True
									return "A patient with this ID already exists."
					if founded != True:
						for doctor in range(len(doctors)):
							if str(uri[1]) == str(doctors[doctor]['userID']):
								doctors[doctor]["patientsList"].append(new)
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

# Removes all the devices with timestamp higher than two minutes. 
def deleteOld(addressCatalog):
	doctors = requests.get(addressCatalog+"/doctors")
	doctors = doctors.json()
	for doctor in range(len(doctors['doctors'])):
		for patient in range(len(doctors['doctors'][doctor]["patientsList"])):
			devices = doctors['doctors'][doctor]["patientsList"][patient]["devicesList"]
			for device in range(len(devices)):
				if int(time.mktime(time.strptime(devices[device]['lastUpdate'],"%d-%m-%Y %H:%M:%S"))) + 60*2 < time.time():
					requests.delete(addressCatalog+'/device/'+str(devices[device]['deviceID']))
				else:
					pass	

if __name__=="__main__":
	addressCatalog = get_address()
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
	cherrypy.config.update({'server.socket_port':9090})
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
                      'tools.staticfile.filename': os.path.abspath("./css/style.css")
                    } })
		cherrypy.tree.mount(RestAPI(),'/api',{'/':{
	 		'request.dispatch':cherrypy.dispatch.MethodDispatcher(),  
 	 		'tools.sessions.on':True
	 	}})
		
		cherrypy.engine.start()
		while True:
			time.sleep(60)
			deleteOld(addressCatalog)
		cherrypy.engine.block()
	except KeyboardInterrupt:
		print("Stopping the engine")
		exit()