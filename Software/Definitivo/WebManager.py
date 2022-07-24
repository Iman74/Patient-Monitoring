import cherrypy

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
	def service_registration(self):
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
	def doctor_delete(self):
		return open("template/doctor_delete.html").read()			# delete a doctors
	@cherrypy.expose
	def patient_delete(self):
		return open("template/patient_delete.html").read()				# delete a patient
	@cherrypy.expose
	def device_delete(self):
		return open("template/device_delete.html").read()			# delete a device
	@cherrypy.expose
	def service_delete(self):
		return open("template/service_delete.html").read()			# delete a microservice
	