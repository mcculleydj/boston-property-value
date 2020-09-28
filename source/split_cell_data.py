import json

with open('../resources/cell_data.json', 'r') as f:
	cells = json.load(f)

for y in range(1985, 2017):
	year = str(y)
	this_year = {}
	
	print('Creating %s_cell_data.json...' % year)

	for cell in cells:
		
		this_cell = {}
		this_cell['live'] = False

		if year in cell and 'avg_vpsf' in cell[year]:
			this_cell['avg_vpsf'] = cell[year]['avg_vpsf']
			this_cell['total_area'] = cell[year]['total_area']
			this_cell['count'] = cell[year]['count']
			if this_cell['total_area'] >= 30000 and this_cell['count'] >= 10:
				this_cell['live'] = True
			
		this_cell['lat1'] = cell['lat1']
		this_cell['lat2'] = cell['lat2']
		this_cell['lat3'] = cell['lat3']
		this_cell['lat4'] = cell['lat4']
		this_cell['lat5'] = cell['lat5']
		this_cell['lat6'] = cell['lat6']
		this_cell['lng1'] = cell['lng1']
		this_cell['lng2'] = cell['lng2']
		this_cell['lng3'] = cell['lng3']
		this_cell['lng4'] = cell['lng4']
		this_cell['lng5'] = cell['lng5']
		this_cell['lng6'] = cell['lng6']

		this_cell['border'] = False
		this_cell['bridge'] = False
		this_cell['bridge_neighbor'] = False
		
		this_year[cell['cell_id']] = this_cell 
	
	with open('../resources/' + year + '_cell_data.json', 'w') as f:
		f.write(json.dumps(this_year, indent=4, sort_keys=True, separators=(',', ': ')))

# EOF
