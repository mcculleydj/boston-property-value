import json
import operator
import math
import numpy as np

# 15 year spans
spans = ('1986', '2001', '2016')

for i in range(len(spans) - 1):

	base_year = spans[i]
	curr_year = spans[i + 1]

	with open('../resources/' + base_year + '_cell_state.json', 'r') as f:
		base_state = json.load(f)

	with open('../resources/' + base_year + '_cell_data.json', 'r') as f:
		base_cells = json.load(f)

	with open('../resources/' + curr_year + '_cell_data.json', 'r') as f:
		curr_cells = json.load(f)

	base_live_cells = {c for c in base_cells if base_cells[c]['live']}
	curr_live_cells = {c for c in curr_cells if curr_cells[c]['live']}

	live_cells = base_live_cells.intersection(curr_live_cells)

	features = {}

	for cell in live_cells:
		
		features[cell] = {}

		# dynamic

		features[cell]['max_flow']  = max(base_state[cell]['flow_hist'])
		features[cell]['min_flow']  = min(base_state[cell]['flow_hist'])
		features[cell]['init_flow'] = sum(base_state[cell]['flow_hist'][:10])
		features[cell]['net_flow']  = sum(base_state[cell]['flow_hist'])
		features[cell]['outflow']   = sum(f for f in base_state[cell]['flow_hist'] if f < 0)
		features[cell]['inflow']    = sum(f for f in base_state[cell]['flow_hist'] if f > 0)
		features[cell]['abs_flow']  = sum([abs(f) for f in base_state[cell]['flow_hist']])
		features[cell]['flushed']   = base_state[cell]['total_flushed']
		
		# static

		features[cell]['count']      = base_cells[cell]['count']
		features[cell]['str_edges']  = len(base_state[cell]['strong_edges'])
		features[cell]['weak_edges'] = len(base_state[cell]['weak_edges'])
		features[cell]['total_area'] = base_cells[cell]['total_area']
		features[cell]['value']      = base_state[cell]['init_val']

		# mixed

		features[cell]['flush_ratio'] = (base_state[cell]['init_val'] / 
			                             base_state[cell]['total_flushed'])

	# define target cells

	val_thr_pct = 33
	inc_thr_pct = 95

	base_vals = []
	pct_incrs = []
	cell_pct_incr = {}

	for cell in live_cells:
		base_val = base_cells[cell]['avg_vpsf']
		curr_val = curr_cells[cell]['avg_vpsf']
		pct_incr = (curr_val - base_val) / base_val
		base_vals.append(base_val)
		pct_incrs.append(pct_incr)
		cell_pct_incr[cell] = pct_incr

	base_vals_arr = np.array(base_vals)
	val_thr = np.percentile(base_vals_arr, val_thr_pct)

	print('Value threshold:', val_thr)

	pct_incrs_arr = np.array(pct_incrs)
	inc_thr = np.percentile(pct_incrs_arr, inc_thr_pct)

	print('Performance threshold:', inc_thr)

	lv_cells = [c for c in live_cells if base_cells[c]['avg_vpsf'] < val_thr]
	hp_cells = [c for c in live_cells if cell_pct_incr[c] > inc_thr]

	print ('len(lv_cells):', len(lv_cells))
	print ('len(hp_cells):', len(hp_cells))

	overlap = [c for c in lv_cells if c in hp_cells]

	print('len(overlap lv - hp):', len(overlap))

	hplv_cells = [c for c in live_cells 
                  if base_cells[c]['avg_vpsf'] < val_thr 
                  and cell_pct_incr[c] > inc_thr]

	print('Number of target cells:', len(hplv_cells))
	print()

	for cell in features:
		features[cell]['target'] = 0

	for cell in hplv_cells:
		features[cell]['target'] = 1

	with open('../resources/' + 
		      base_year[-2:] + '_' + 
		      curr_year[-2:] + '_features.json', 'w') as f:
		f.write(json.dumps(features, sort_keys=True, indent=4, separators=(',', ': ')))

with open('../resources/' + 
	      spans[0][-2:] + '_' + 
	      spans[1][-2:] + '_features.json', 'r') as f:
	features_trn = json.load(f)

with open('../resources/' + 
	      spans[1][-2:] + '_' + 
	      spans[2][-2:] + '_features.json', 'r') as f:
	features_tst = json.load(f)

hplv_cells_trn = []

for cell in features_trn:
	if features_trn[cell]['target'] == 1:
		hplv_cells_trn.append(cell)

hplv_cells_tst = []

for cell in features_tst:
	if features_tst[cell]['target'] == 1:
		hplv_cells_tst.append(cell)

overlap = [c for c in hplv_cells_trn if c in hplv_cells_tst]

# print('Overlapping HPLV cells between training and tesing set:')
# for c in overlap:
# 	print(c)

print('Number of overlapping cells between training and test sets:', len(overlap))

#EOF