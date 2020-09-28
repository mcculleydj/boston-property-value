import pymongo
import requests
import json

print('Connecting to the DBMS...')
client = pymongo.MongoClient()
print('Connected...')

asmts_2016 = client.repo.asmts_2016

N = 169199  	# number of assessment records
LIMIT = 50000  	# single Socrata API call record return limit

print('Fetching parcel IDs, latitudes, and longitudes...')

url = 'https://data.cityofboston.gov/resource/g5b5-xrwi.json'
select = '&$select=pid,latitude,longitude'
limit = '$limit=' + str(LIMIT)

records = []	# accumulator for records in the database

for i in range(0, 1 + N // LIMIT):
    offset = '&$offset=' + str(i * LIMIT)
    query  = '?' + limit + offset + select
    result = requests.get(url + query)
    records += json.loads(result.text)

result = asmts_2016.insert_many(records)

print('Inserted', len(result.inserted_ids),
	  'parcels into asmts_2016...')

print('Filtering out duplicate parcels...')

duplicates = asmts_2016.aggregate([
	{
		'$group': {
		  	'_id': {
		    	'pid': '$pid',
		    	'lat': '$latitude',
		    	'lng': '$longitude'
		  	},
		  	'uniqueIds': {
		    	'$addToSet': "$_id" 
		  	},
		  	'count': {
		    	'$sum': 1
		  	} 
		}
	}, 
	{
		'$match': { 
		  	'count': {
		    	'$gt': 1
		   	}
		}
	}])

number_removed = 0

for d in duplicates:
	for i in range(d['count'] - 1):
		asmts_2016.delete_one({'_id': d['uniqueIds'][i]})
		number_removed += 1

print('Removed %d duplicate parcels...' % number_removed)

print('Disconnecting from the DBMS...')
client.close()
print('Disconnected...')

# EOF