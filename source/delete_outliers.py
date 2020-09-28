import pymongo
import numpy
import json

print('Connecting to the DBMS...')
client = pymongo.MongoClient()
print('Connected...')

residential = client.repo.residential
outliers = client.repo.outliers

# https://en.wikipedia.org/wiki/Outlier
# Tukey's Test (q1 and q3 are the first and third quartile):
# any observation outside the range [q1 - 1.5(q3 - q1), q3 + 1.5(q3 - q1)]
# is considered and outlier and vspf is removed from that year's record

for y in range(1985, 2017):
	year = str(y)
	documents = list(residential.find({'history.' + year + '.vpsf': {'$exists': True}}))
	vpsfs = numpy.array([d['history'][year]['vpsf'] for d in documents])
	
	q1 = numpy.percentile(vpsfs, 25)
	q3 = numpy.percentile(vpsfs, 75)
	lower_bound = q1 - 1.5 * (q3 - q1)
	upper_bound = q3 + 1.5 * (q3 - q1)
	
	count = 0

	for d in documents:
		vpsf = d['history'][year]['vpsf']
		if vpsf > upper_bound or vpsf < lower_bound:
			del d['history'][year]['vpsf']
			residential.update({'_id': d['_id']}, 
				               {'$set': {'history': d['history']}})
			outliers.insert_one({'year': year, 
		                		 'lower_bound': lower_bound, 
		                		 'upper_bound': upper_bound, 
		                		 'pid': d['pid'],
		                		 'vpsf': vpsf})
			count += 1
	
	print('For the year', year, 'removing', count, 'outliers...')

print('Disconnecting from the DBMS...')
client.close()
print('Disconnected...')

# EOF
