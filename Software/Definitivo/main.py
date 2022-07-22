import cherrypy
import json
import time
import os
from Catalog import RestAPI
from WebManager import WebPage

def get_address():
	conf = json.load(open("settings.json"))
	addressCatalog = conf["catalog_address"]
	return addressCatalog

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
			RestAPI.deleteOld(addressCatalog)
		cherrypy.engine.block()
	except KeyboardInterrupt:
		print("Stopping the engine")
		exit()