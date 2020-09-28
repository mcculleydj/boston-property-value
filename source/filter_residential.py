import pymongo

print('Connecting to the DBMS...')
client = pymongo.MongoClient()
print('Connected...')

parcels_w_loc = client.repo.parcels_w_loc
residential = client.repo.residential

print('Filtering out parcels with less than 300 square feet of living area...')

documents = parcels_w_loc.find({'living_area': {'$gte': 300}})
count = documents.count()

print('Filtering out unwanted property types...')

residential_codes = {'101', # single-family
					 '102', # condo
					 '104', # two-family
					 '105', # three-family
					 '111'} # four-to-six unit apartment

index = 1

for d in documents:
	if d['p_code'][:3] in residential_codes:
		residential.insert_one(d)
	print('Completed %d of %d parcels...' % (index, count))
	index += 1

print('Disconnecting from the DBMS...')
client.close()
print('Disconnected...')

# EOF
