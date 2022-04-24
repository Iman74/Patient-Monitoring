import requests
import json
from datetime import datetime
import time


def postCh(api, ch_id):   #create a new channel
		name_ch = "User "+str(ch_id)
		# in a second moment it could be changed with the name of the user 
		payload = {
					"api_key": api,
					"id": ch_id,
					"name": name_ch,
					"field1": "heartRate",
					"field2": "spO2",
					"field3": "bodyTemperature",
					"field4": "roomTemperature",
					"public_flag": False
					}
		try:
			r = requests.post("https://api.thingspeak.com/channels.json", params = payload)
			r.raise_for_status()
			#print(f"Channel for the user ... created.")
			r = r.json()
			ch_id = r["id"]
			return ch_id
		except requests.exceptions.HTTPError as err:
			raise SystemExit(err)


def sendAll(database, w_api):
	print("Database loading...")
	
	payload = {
			"write_api_key": "N14TC42Q5HCUTOMH",
			"updates": []
			}
	for patient in range(len(database["patients"])):
		'''TO ADD: get ch_id for each patient
		ch_id = get_id(database["patients"][patient]["id"])  # function to get the channel id from the catalog that corresponds 
		to the id in the database '''
		ch_id = "1710399"
		# the request returns error if there is twice the same timestamp, so we have to gather values with same timestamp:
		repeatition = [] # list of index of repeatition of the same timestamp
		
		payload, last_added = create_json(database,patient,payload)
	
	url = "https://api.thingspeak.com/channels/"+str(ch_id)+"/bulk_update.json"
	headers = {
			'Content-Type': 'application/json'
	}
	try:
		r = requests.post(url,headers = headers, data = json.dumps(payload))
		r.raise_for_status()
		print("Database loaded.")
		return last_added
	except requests.exceptions.HTTPError as err:
		raise SystemExit(err)


def postData(last_added, database, w_api):

	print("Searching for updates...")
	payload = {
		"write_api_key": "N14TC42Q5HCUTOMH",
			"updates": []
			}
	# check for the last timestamp saved
	for patient in range(len(database["patients"])):
		'''TO ADD: get ch_id for each patient
		ch_id = get_id(database["patients"][patient]["id"])  function to get the channel id from the catalog that corresponds 
		to the id in the database '''
		ch_id = "1710399"
		# the request returns error if there is twice the same timestamp, so we have to gather values with same timestamp:
		repeatition = [] # list of index of repeatition of the same timestamp

		for value in reversed(range(len(database["patients"][patient]["values"]))):
			if last_added == database["patients"][patient]["values"][value]:
				# post starts just after this value
				starting_point = value+1
				break
		payload, last_added = create_json(database,patient,payload,starting_point)

	# check if there are updates
	if payload["updates"]:
		url = "https://api.thingspeak.com/channels/"+str(ch_id)+"/bulk_update.json"
		headers = {
	  				'Content-Type': 'application/json'
		}
		try:
			r = requests.post(url,headers = headers, data = json.dumps(payload))
			r.raise_for_status()
			print("Data updated.")
		except requests.exceptions.HTTPError as err:
			raise SystemExit(err)	
	else:
		print("There aren't updates.")


def create_json(database,patient,payload,starting_point=0):
	repeatition = []
	global last_added
	for value in range(starting_point,len(database["patients"][patient]["values"])):
		if database["patients"][patient]["values"][value]['n'] == 'heartRate':
			fieldName = "field1"
		elif database["patients"][patient]["values"][value]['n'] == 'oxygen':
			fieldName = "field2"
		elif database["patients"][patient]["values"][value]['n'] == 'bodyTemperature':
			fieldName = "field3"
		else:
			fieldName = "field4"
		# check for the same timestamp:
		for value2 in range(len(database["patients"][patient]["values"])):
			if database["patients"][patient]["values"][value2]['t'] == database["patients"][patient]["values"][value]['t'] and value != value2:
				repeatition.append(value2)
		# put values with the same timestamp together:
		if value in repeatition:
			for index in range(len(payload["updates"])):
				# find the same timestamp
				if payload["updates"][index]["created_at"] == datetime.fromtimestamp(int(database["patients"][patient]["values"][value]["t"])).isoformat():
					payload["updates"][index][fieldName] = float(database["patients"][patient]["values"][value]["v"])
					last_added = database["patients"][patient]["values"][value]

		else:
			# ThingSpeak requires ISO 8601 timestamp
			msg = {"created_at": datetime.fromtimestamp(int(database["patients"][patient]["values"][value]["t"])).isoformat(), 
					fieldName: float(database["patients"][patient]["values"][value]["v"])}
			payload["updates"].append(msg)
			last_added = database["patients"][patient]["values"][value]
	return payload, last_added



if __name__=="__main__":


	'''need of Catalog to get api and channel_id for each user
	cat=json.load(open("Catalog.json"))

	api = "2MV1G6IJKDPPCC1P"'''

	database = json.load(open("database_v2.json"))
	w_api = "N14TC42Q5HCUTOMH"
	'''TO ADD: check if each patient in catalog has his own channel on TS, if not:
		ch_id = postCh(api, ch_id)
		add ch_id to catalog
		add function to get w_api for each channel having his ch_id '''

	last_added = {}
	last_added = sendAll(database,w_api)
	while True:
		time.sleep(15)
		database = json.load(open("database_v2.json"))
		postData(last_added, database,w_api)


''' w_api for each channel: we have to write it manually... maybe through command line? 
Otherwise we could create four channel for four user (TS free has the limit of four channel)
and use them for our project.'''
