import pymongo
import re
import requests
import json
import time

print('Connecting to the DBMS...')
client = pymongo.MongoClient()
print('Connected...')

parcels = client.repo.parcels
parcels_w_loc = client.repo.parcels_w_loc
parcels_wo_loc = client.repo.parcels_wo_loc
parcels_misloc = client.repo.parcels_misloc

# add_loc strips away the latitude and longitude fields
# and builds the loc field consistent with MongoDB's convention

def add_loc(document, lng, lat):
	document['loc'] = {}
	document['loc']['type'] = 'Point'
	document['loc']['coordinates'] = [lng, lat]
	del document['latitude']
	del document['longitude']
	return document

print('Geocoding parcels with missing location data...')

START = 0

documents = parcels.find(
	{'$or': [{'latitude': '#N/A'}, 
		     {'longitude': '#N/A'}]
	}, no_cursor_timeout=True).skip(START)

count = documents.count()

#######################################
# Google Geocoding API Pricing:
# Free for first 2,500 queries per day
# $0.50 per additional 1,000 queries
#######################################

url = 'https://maps.googleapis.com/maps/api/geocode/json?key='
api_key = '<ENTER API KEY HERE>'

index = START + 1

for d in documents:
	
	address = re.sub(r' ', '+', d['address'])

	if not address[0].isdigit():
		print('Address does not begin with a street number...')
		print('Parcel', d['pid'], 'located at', d['address'], 'was NOT successfully geocoded...')
		print('Adding parcel to parcels_wo_loc...')
		parcels_wo_loc.insert_one(d)
		print('Completed', index, 'of', count, 'parcels with missing location data...')
		index += 1
		continue

	query = api_key + '&address=' + address
	request = requests.get(url + query)
	result = json.loads(request.text)

	if result['status'] == 'OK':

		lat = result['results'][0]['geometry']['location']['lat']
		lng = result['results'][0]['geometry']['location']['lng']

		# determine if result is located in Boston

		in_boston = False
		address_components = result['results'][0]['address_components']
		for component in address_components:
			if component['short_name'] == 'Boston':
				in_boston = True
				break

		if in_boston:
			print('Parcel', d['pid'], 'located at', d['address'], 'was found in Boston...')
			print('Adding parcel to parcels_w_loc...')
			parcels_w_loc.insert_one(add_loc(d, lng, lat))
		else:
			print('Parcel', d['pid'], 'located at', d['address'], 'was NOT found in Boston...')
			print('Adding parcel to parcels_misloc...')
			parcels_misloc.insert_one(add_loc(d, lng, lat))

	else:

		print('Geocode request failed with', result['status'], 'status code...')
		print('Parcel', d['pid'], 'located at', d['address'], 'was NOT successfully geocoded...')
		print('Adding parcel to parcels_wo_loc...')
		parcels_wo_loc.insert_one(d)
	
	print('Completed', index, 'of', count, 'parcels with missing location data...')
	
	time.sleep(.05) # max throughput is 50 queries per second
	index += 1

documents.close()

print('Adding parcels with existing location data...')

START = 0
index = START + 1

documents = parcels.find({
		 		'$and': [
		 			{'latitude': {'$ne': '#N/A'}}, 
		 			{'longitude': {'$ne': '#N/A'}}]
		 	}, no_cursor_timeout=True).skip(START)

count = documents.count()

for d in documents:
	lng = float(d['longitude'])
	lat = float(d['latitude'])
	parcels_w_loc.insert_one(add_loc(d, lng, lat))
	print('Adding %d of %d documents with existing location data to parcels_w_loc...' 
		  % (index, count))
	index += 1

documents.close()

print('Disconnecting from the DBMS...')
client.close()
print('Disconnected...')

# EOF
