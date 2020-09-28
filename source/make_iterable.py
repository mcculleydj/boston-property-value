import json
import math

def make_iterable(year):

	# read annual data
	with open('../resources/' + year + '_cell_data.json', 'r') as f:
		cells = json.load(f)

	with open('../resources/' + year + '_cell_state.json', 'r') as f:
		state = json.load(f)

	iterable_data = []
	vals = []
	
	# flatten cell_id and then append each cell
	for cell in cells:
		this_cell = {}
		for k in cells[cell]:
			this_cell[k] = cells[cell][k]
		this_cell['cell_id'] = cell
		if this_cell['live']:
			this_cell['5yr_pct_incr']  = "N/A"
			this_cell['10yr_pct_incr'] = "N/A"
			this_cell['15yr_pct_incr'] = "N/A"
			this_cell['20yr_pct_incr'] = "N/A"
			this_cell['25yr_pct_incr'] = "N/A"
			this_cell['30yr_pct_incr'] = "N/A"

			this_cell['net_flow'] = sum(state[this_cell['cell_id']]['flow_hist'])
			this_cell['max_flow'] = max(state[this_cell['cell_id']]['flow_hist'])
			this_cell['min_flow'] = min(state[this_cell['cell_id']]['flow_hist'])
			this_cell['flushed']  = state[this_cell['cell_id']]['total_flushed']

			vals.append(this_cell['avg_vpsf'])

		iterable_data.append(this_cell)

	vals.sort(reverse=True)

	if year >= '1990':
		with open('../resources/' + str(int(year)-5) + '_cell_data.json', 'r') as f:
			base_cells_5yr = json.load(f)
	if year >= '1995':
		with open('../resources/' + str(int(year)-10) + '_cell_data.json', 'r') as f:
			base_cells_10yr = json.load(f)
	if year >= '2000':
		with open('../resources/' + str(int(year)-15) + '_cell_data.json', 'r') as f:
			base_cells_15yr = json.load(f)
	if year >= '2005':
		with open('../resources/' + str(int(year)-20) + '_cell_data.json', 'r') as f:
			base_cells_20yr = json.load(f)
	if year >= '2010':
		with open('../resources/' + str(int(year)-25) + '_cell_data.json', 'r') as f:
			base_cells_25yr = json.load(f)
	if year >= '2015':
		with open('../resources/' + str(int(year)-30) + '_cell_data.json', 'r') as f:
			base_cells_30yr = json.load(f)

	for cell in iterable_data:

		# rank
		if cell['live']:
			cell['rank'] = vals.index(cell['avg_vpsf'])

			# pct_incrs
			cid = cell['cell_id']
			if year >= '1990':
				if base_cells_5yr[cid]['live']:
					base_val = base_cells_5yr[cid]['avg_vpsf']
					curr_val = cell['avg_vpsf']
					cell['5yr_pct_incr'] = (curr_val - base_val) / base_val
			if year >= '1995':
				if base_cells_10yr[cid]['live']:
					base_val = base_cells_10yr[cid]['avg_vpsf']
					curr_val = cell['avg_vpsf']
					cell['10yr_pct_incr'] = (curr_val - base_val) / base_val			
			if year >= '2000':
				if base_cells_15yr[cid]['live']:
					base_val = base_cells_15yr[cid]['avg_vpsf']
					curr_val = cell['avg_vpsf']
					cell['15yr_pct_incr'] = (curr_val - base_val) / base_val
			if year >= '2005':
				if base_cells_20yr[cid]['live']:
					base_val = base_cells_20yr[cid]['avg_vpsf']
					curr_val = cell['avg_vpsf']
					cell['20yr_pct_incr'] = (curr_val - base_val) / base_val
			if year >= '2010':
				if base_cells_25yr[cid]['live']:
					base_val = base_cells_25yr[cid]['avg_vpsf']
					curr_val = cell['avg_vpsf']
					cell['25yr_pct_incr'] = (curr_val - base_val) / base_val
			if year >= '2015':
				if base_cells_30yr[cid]['live']:
					base_val = base_cells_30yr[cid]['avg_vpsf']
					curr_val = cell['avg_vpsf']
					cell['30yr_pct_incr'] = (curr_val - base_val) / base_val

	with open('../resources/' + year + '_cell_data_iter.json', 'w') as f:
		f.write(json.dumps(iterable_data, sort_keys=True, indent=4, separators=(',', ':')))

def add_metadata(year):

	# read annual data
	with open('../resources/' + year + '_cell_data_iter.json', 'r') as f:
		cells = json.load(f)

	vpsfs = [cell['avg_vpsf'] for cell in cells if cell['live']]

	n_parcels = 0

	for cell in cells:
		if cell['live']:
			n_parcels += cell['count']

	avg_avg_vpsf = sum(vpsfs) / len(vpsfs)

	step = (max(vpsfs) - min(vpsfs)) // 8
	start = math.floor(min(vpsfs))
	domain = []
	for i in range(8):
		domain.append(start + i * step)

	avg_5yr_pct_incr  = 'N/A'
	avg_10yr_pct_incr = 'N/A'
	avg_15yr_pct_incr = 'N/A'
	avg_20yr_pct_incr = 'N/A'
	avg_25yr_pct_incr = 'N/A'
	avg_30yr_pct_incr = 'N/A'

	if year >= '1990':
		all_5yr_pct_incr = [cell['5yr_pct_incr'] for cell in cells 
		                    if cell['live'] and cell['5yr_pct_incr'] != 'N/A']
		if len(all_5yr_pct_incr) > 0:
			avg_5yr_pct_incr = sum(all_5yr_pct_incr) / len(all_5yr_pct_incr)
	if year >= '1995':
		all_10yr_pct_incr = [cell['10yr_pct_incr'] for cell in cells 
		                     if cell['live'] and cell['10yr_pct_incr'] != 'N/A']
		if len(all_10yr_pct_incr) > 0:
			avg_10yr_pct_incr = sum(all_10yr_pct_incr) / len(all_10yr_pct_incr)		
	if year >= '2000':
		all_15yr_pct_incr = [cell['15yr_pct_incr'] for cell in cells 
		                     if cell['live'] and cell['15yr_pct_incr'] != 'N/A']
		if len(all_15yr_pct_incr) > 0:
			avg_15yr_pct_incr = sum(all_15yr_pct_incr) / len(all_15yr_pct_incr)
	if year >= '2005':
		all_20yr_pct_incr = [cell['20yr_pct_incr'] for cell in cells 
		                     if cell['live'] and cell['20yr_pct_incr'] != 'N/A']
		if len(all_20yr_pct_incr) > 0:
			avg_20yr_pct_incr = sum(all_20yr_pct_incr) / len(all_20yr_pct_incr)
	if year >= '2010':
		all_25yr_pct_incr = [cell['25yr_pct_incr'] for cell in cells 
		                     if cell['live'] and cell['25yr_pct_incr'] != 'N/A']
		if len(all_25yr_pct_incr) > 0:
			avg_25yr_pct_incr = sum(all_25yr_pct_incr) / len(all_25yr_pct_incr)
	if year >= '2015':
		all_30yr_pct_incr = [cell['30yr_pct_incr'] for cell in cells 
		                     if cell['live'] and cell['30yr_pct_incr'] != 'N/A']
		if len(all_30yr_pct_incr) > 0:
			avg_30yr_pct_incr = sum(all_30yr_pct_incr) / len(all_30yr_pct_incr)

	# append metadata as the last item in the list
	cells.append({'avg_avg_vpsf': avg_avg_vpsf, 
		          'totalVpsf': sum(vpsfs),
		          'min_vpsf': min(vpsfs), 
		          'max_vpsf': max(vpsfs), 
		          'domain': domain,
		          'num_cells': len(vpsfs),
		          'num_parcels': n_parcels,
				  'avg_5yr_pct_incr': avg_5yr_pct_incr,
				  'avg_10yr_pct_incr': avg_10yr_pct_incr,
				  'avg_15yr_pct_incr': avg_15yr_pct_incr,
				  'avg_20yr_pct_incr': avg_20yr_pct_incr,
				  'avg_25yr_pct_incr': avg_25yr_pct_incr,
				  'avg_30yr_pct_incr': avg_30yr_pct_incr})

	with open('../resources/' + year + '_cell_data_iter.json', 'w') as f:
		f.write(json.dumps(cells, indent=4, separators=(',', ': ')))

for y in range(1985, 2017):
	year = str(y)
	print('Generating %s_cell_data_iter.json...' % year)
	make_iterable(year)

for y in range(1985, 2017):
	year = str(y)
	print('Adding metadata to %s_cell_data_iter.json...' % year)
	add_metadata(year)

# EOF
