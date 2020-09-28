import json

def run_model(year):

	with open('../resources/' + year + '_cell_data.json', 'r') as f:
		 cells = json.load(f)

	with open('../resources/' + year + '_edge_map_final.json', 'r') as f:
		 edges = json.load(f)

	live_cells = {cell for cell in cells if cells[cell]['live']}
	cell_state = {}
	
	total_value = sum([cells[cell]['avg_vpsf'] for cell in live_cells])
	tv_for_flush = total_value * .00001

	strong_flow_const = .1
	weak_flow_const   = .07
	flush_const 	  = .000006 * tv_for_flush

	for cell in cells:
		if cells[cell]['live']:
			cell_state[cell] = {}
			cell_state[cell]['val'] = cells[cell]['avg_vpsf']
			cell_state[cell]['init_val'] = cells[cell]['avg_vpsf']
			cell_state[cell]['count'] = cells[cell]['count']
			cell_state[cell]['strong_edges'] = edges[cell]['strong']
			cell_state[cell]['weak_edges'] = edges[cell]['weak']
			cell_state[cell]['strong_flow'] = [0 for _ in edges[cell]['strong']]
			cell_state[cell]['weak_flow'] = [0 for _ in edges[cell]['weak']]
			cell_state[cell]['flush'] = cells[cell]['total_area'] * flush_const
			cell_state[cell]['total_flushed'] = 0
			cell_state[cell]['flow_hist'] = []

	epoch = 0

	termination_threshold = .1 * total_value

	print('\nExecuting flow/flush algorithm for %s...\n' % year)

	while total_value > termination_threshold:
		print('\tEpoch %d: %.0f total value remaining...' % (epoch, total_value))
				
		# update flow vectors and initialize another flow_hist element
		for i in live_cells:
			strong_ties = cell_state[i]['strong_edges']
			weak_ties = cell_state[i]['weak_edges']
			strong_flow = []
			weak_flow = []
			cell_state[i]['flow_hist'].append(0)
			
			for j in strong_ties:
				diff = cell_state[i]['val'] - cell_state[j]['val']
				if diff > 0:
					strong_flow.append(diff * strong_flow_const)
				else:
					strong_flow.append(0)
			for j in weak_ties:
				diff = cell_state[i]['val'] - cell_state[j]['val']
				if diff > 0:
					weak_flow.append(diff * weak_flow_const)
				else:
					weak_flow.append(0)

			if cell_state[i]['val'] >= sum(strong_flow) + sum(weak_flow):
				cell_state[i]['strong_flow'] = strong_flow
				cell_state[i]['weak_flow'] = weak_flow
			else:
				if sum(strong_flow) < .01 or sum(weak_flow) < .01:
					cell_state[i]['strong_flow'] = [0 for _ in strong_ties]
					cell_state[i]['weak_flow'] = [0 for _ in weak_ties]
				else:
					strong_val = cell_state[i]['val'] * sum(strong_flow) / (sum(strong_flow) + sum(weak_flow))
					weak_val = cell_state[i]['val'] * sum(weak_flow) / (sum(strong_flow) + sum(weak_flow))
					cell_state[i]['strong_flow'] = [(strong_val * f / sum(strong_flow)) for f in strong_flow]
					cell_state[i]['weak_flow'] = [(weak_val * f / sum(weak_flow)) for f in weak_flow]
		
		# outflow
		for i in live_cells:
			strong_ties = cell_state[i]['strong_edges']
			weak_ties = cell_state[i]['weak_edges']
			k = 0 # flow_index
			for j in strong_ties:
				cell_state[j]['val'] += cell_state[i]['strong_flow'][k]
				cell_state[j]['flow_hist'][epoch] += cell_state[i]['strong_flow'][k]
				cell_state[i]['val'] -= cell_state[i]['strong_flow'][k]
				cell_state[i]['flow_hist'][epoch] -= cell_state[i]['strong_flow'][k]
				k += 1
			k = 0 # flow_index
			for j in weak_ties:
				cell_state[j]['val'] += cell_state[i]['weak_flow'][k]
				cell_state[j]['flow_hist'][epoch] += cell_state[i]['weak_flow'][k]
				cell_state[i]['val'] -= cell_state[i]['weak_flow'][k]
				cell_state[i]['flow_hist'][epoch] -= cell_state[i]['weak_flow'][k]
				k += 1

		# flush
		for i in live_cells:
			if cell_state[i]['val'] >= cell_state[i]['flush']:
				cell_state[i]['total_flushed'] += cell_state[i]['flush']
				cell_state[i]['val'] -= cell_state[i]['flush']
				total_value -= cell_state[i]['flush']
			else:
				cell_state[i]['total_flushed'] += cell_state[i]['val']
				total_value -= cell_state[i]['val']
				cell_state[i]['val'] = 0

		epoch += 1

	with open('../resources/' + year + '_cell_state.json', 'w') as f:
		f.write(json.dumps(cell_state, sort_keys=True, indent=4, separators=(',', ': ')))

for year in range(1985, 2017):
	run_model(str(year))

# EOF
