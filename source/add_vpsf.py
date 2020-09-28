import pymongo

print('Connecting to the DBMS...')
client = pymongo.MongoClient()
print('Connected...')

residential = client.repo.residential

documents = residential.find()
count = documents.count()

res_types = {'Residential Condo Unit',
 			 'One Family',
 			 'Two Family',
 			 'Three Family',
 			 'Four to Six Family'}

index = 1

for d in documents:
	for year in d['history']:
		hst = d['history'][year]
		val = hst['value']
		typ = hst['type']
		if typ in res_types and val >= 20000:
			vpsf = val / d['living_area']
			hst['vpsf'] = vpsf
			residential.update({'_id': d['_id']}, 
							   {'$set': {'history.' + year: hst}})
	print('Completed %d of %d parcels...' % (index, count))
	index += 1

print('Disconnecting from the DBMS...')
client.close()
print('Disconnected...')

# EOF
