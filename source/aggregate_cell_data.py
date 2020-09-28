import pymongo
import json

print('Connecting to the DBMS...')
client = pymongo.MongoClient()
print('Connected...')

residential = client.repo.residential

with open('../resources/cell_data.json', 'r') as f:
	cells = json.load(f)

with open('../resources/inflation.json', 'r') as f:
	inflation = json.load(f)

for cell in cells:
	print('Aggregating data for cell %d...' % cell['cell_id'])
	documents = list(residential.find({'cell_id': cell['cell_id']}))
	if documents:				
		for y in range(1985, 2017):							
			year = str(y)											
			total_area = 0
			vpsfs = []										
			for d in documents:
				# year in history if asmt performed and 
				# vspf in year if val >= 20000 and of res_type		
				if year in d['history'] and 'vpsf' in d['history'][year]: 		
					vpsfs.append(d['history'][year]['vpsf'])
					total_area += d['living_area']			
			if len(vpsfs) > 0:
				cell[year] = {}
				cell[year]['total_area'] = total_area		
				cell[year]['avg_vpsf'] = inflation[year] * sum(vpsfs) / len(vpsfs)				    
				cell[year]['count'] = len(vpsfs) 

with open('../resources/cell_data.json', 'w') as f:
	f.write(json.dumps(cells, sort_keys=True, indent=4, separators=(',', ': ')))

print('Disconnecting from the DBMS...')
client.close()
print('Disconnected...')

# EOF
