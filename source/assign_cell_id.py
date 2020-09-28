import pymongo
import json

print('Connecting to the DBMS...')
client = pymongo.MongoClient()
print('Connected...')

residential = client.repo.residential

residential.create_index([('loc', pymongo.GEOSPHERE)])

with open('../resources/cell_data.json', 'r') as f:
	cells = json.load(f)

for c in cells:
	print('Assigning parcels to cell %d...' % c['cell_id'])
	coords = [[
	           [c['lng1'], c['lat1']],
	           [c['lng2'], c['lat2']],
	           [c['lng3'], c['lat3']],
	           [c['lng4'], c['lat4']],
	           [c['lng5'], c['lat5']],
	           [c['lng6'], c['lat6']],
	           [c['lng1'], c['lat1']]
	         ]]
	
	documents = residential.find(
		{'loc': 
			{'$geoWithin': 
				{'$geometry': 
		            {'type': 'Polygon', 'coordinates': coords}
		        }
		    }
		})

	for d in documents:
		objId = d['_id']
		residential.update({'_id': objId}, {'$set': {'cell_id': c['cell_id']}})

# the remap dictionary along with the following
# for loop can fix obvious errors in geocoding

# cell 3355 contains a large condo complex
# which is mistakenly mapped to an adjacent cell 3354 
# which contains no buildings and covers mostly water

remap = {3354: 3355}

for c in remap:
	residential.update({'cell_id': c}, {'$set': {'cell_id': remap[c]}}, multi=True)

print('Disconnecting from the DBMS...')
client.close()
print('Disconnected...')

# EOF