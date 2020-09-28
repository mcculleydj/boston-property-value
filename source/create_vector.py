import json

# 86-01 training data; 01-16 testing data
spans = [('1986', '2001'), ('2001', '2016')]

vector_data = {}

for (base_year, curr_year) in spans:

	with open('../resources/' + base_year + '_cell_state.json', 'r') as f:
		base_state = json.load(f)

	with open('../resources/' + base_year + '_cell_data.json', 'r') as f:
		base_cells = json.load(f)

	with open('../resources/' + curr_year + '_cell_data.json', 'r') as f:
		curr_cells = json.load(f)

	base_live_cells = {c for c in base_cells if base_cells[c]['live']}
	curr_live_cells = {c for c in curr_cells if curr_cells[c]['live']}
	
	# can only consider cells that were live in both the model year
	# and observation year
	common_live_cells = base_live_cells.intersection(curr_live_cells)

	features = {}

	for cell in common_live_cells:
		
		features[cell] = {}

		epochs = len(base_state[cell]['flow_hist'])
		first_third = epochs // 3
		mid_third = 2 * epochs // 3

		# dynamic features
		features[cell]['max_flow']  = max(base_state[cell]['flow_hist'])
		features[cell]['min_flow']  = min(base_state[cell]['flow_hist'])
		features[cell]['init_flow'] = sum(base_state[cell]['flow_hist'][:5])

		features[cell]['early_flow'] = sum(base_state[cell]['flow_hist'][:first_third])
		features[cell]['mid_flow'] = sum(base_state[cell]['flow_hist'][first_third:mid_third])
		features[cell]['late_flow'] = sum(base_state[cell]['flow_hist'][mid_third:epochs])

		features[cell]['net_flow']  = sum(base_state[cell]['flow_hist'])
		features[cell]['outflow']   = sum(f for f in base_state[cell]['flow_hist'] if f < 0)
		features[cell]['inflow']    = sum(f for f in base_state[cell]['flow_hist'] if f > 0)
		features[cell]['abs_flow']  = sum([abs(f) for f in base_state[cell]['flow_hist']])
		features[cell]['flushed']   = base_state[cell]['total_flushed']
		
		# static features
		features[cell]['count']      = base_cells[cell]['count']
		features[cell]['str_edges']  = len(base_state[cell]['strong_edges'])
		features[cell]['weak_edges'] = len(base_state[cell]['weak_edges'])
		features[cell]['total_area'] = base_cells[cell]['total_area']
		features[cell]['value']      = base_state[cell]['init_val']

		# mixed features
		features[cell]['flush_ratio'] = (base_state[cell]['init_val'] / 
			                             base_state[cell]['total_flushed'])

	# classify observations

	with open('../resources/' + base_year + '_cell_data_iter.json', 'r') as f:
		base_cells_iter = json.load(f)

	with open('../resources/' + curr_year + '_cell_data_iter.json', 'r') as f:
		curr_cells_iter = json.load(f)

	vector_data[curr_year] = {}

	# require a 25 percentile increase to qualify as a target cell
	threshold = len(common_live_cells) / 4

	print ('Length common_live_cells:', len(common_live_cells))
	print ('Delta rank required to be a target cell:', threshold)

	cell_base_rank = {}

	for cell in base_cells_iter:
		if 'rank' in cell:
			cell_base_rank[cell['cell_id']] = cell['rank']

	cell_curr_rank = {}

	for cell in curr_cells_iter:
		if 'rank' in cell:
			cell_curr_rank[cell['cell_id']] = cell['rank']

	num_target_cells = 0

	for cell in features:
		features[cell]['rank'] = cell_base_rank[cell]
		delta_rank = cell_base_rank[cell] - cell_curr_rank[cell]
		vector_data[curr_year][cell] = delta_rank
		if delta_rank >= threshold:
			features[cell]['target'] = 1
			num_target_cells += 1
		else:
			features[cell]['target'] = 0

	base_vals = [base_cells[cell]['avg_vpsf'] for cell in common_live_cells]
	curr_vals = [curr_cells[cell]['avg_vpsf'] for cell in common_live_cells]

	base_vals.sort(reverse=True)
	curr_vals.sort(reverse=True)

	vector_data[curr_year]['base_vals'] = base_vals
	vector_data[curr_year]['curr_vals'] = curr_vals

	print('Number of target cells for the span [%s, %s]: %d\n' %
	      (base_year, curr_year, num_target_cells))

	with open('../resources/span_' + 
		      base_year + '_' + 
		      curr_year + '_features.json', 'w') as f:
		f.write(json.dumps(features, sort_keys=True, indent=4, separators=(',', ': ')))

with open('../resources/span_' + 
	      spans[0][0] + '_' + 
	      spans[0][1] + '_features.json', 'r') as f:
	features_trn = json.load(f)

with open('../resources/span_' + 
	      spans[1][0] + '_' + 
	      spans[1][1] + '_features.json', 'r') as f:
	features_tst = json.load(f)

target_cells_trn = []

for cell in features_trn:
	if features_trn[cell]['target'] == 1:
		target_cells_trn.append(cell)

target_cells_tst = []

for cell in features_tst:
	if features_tst[cell]['target'] == 1:
		target_cells_tst.append(cell)

overlap = [c for c in target_cells_trn if c in target_cells_tst]

vector_data['overlap'] = overlap

print('Number of overlapping cells between training and test sets:', len(overlap))

with open('../resources/vector_data.json', 'w') as f:
	f.write(json.dumps(vector_data, sort_keys=True, indent=4, separators=(',', ': ')))

# EOF