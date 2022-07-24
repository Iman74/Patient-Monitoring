import cherrypy
import json
import time
import os
import requests
from Catalog import RestAPI
from WebManager import WebPage

def get_address():
	conf = json.load(open("settings.json"))
	addressCatalog = conf["catalog_address"]
	return addressCatalog
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