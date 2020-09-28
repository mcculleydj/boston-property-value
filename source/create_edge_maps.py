import json

from get_adjacent import get_adj

def build_edge_map(year):
	
	#read annual data
	with open('../resources/' + year + '_cell_data.json', 'r') as f:
		cells = json.load(f)

	bridge_cells = {cell for cell in cells if cells[cell]['bridge']}
	live_cells = {cell for cell in cells if cells[cell]['live']}
	all_cells = bridge_cells.union(live_cells)

	edge_map = {}

	for cell in all_cells:
		adj_cells = [str(cell) for cell in get_adj(int(cell))]
		edge_list = []
		for adj_cell in adj_cells:
			if adj_cell in all_cells:
				edge_list.append(adj_cell)
		edge_map[cell] = edge_list

	# write edge map
	with open('../resources/' + year + '_edge_map.json', 'w') as f:
		f.write(json.dumps(edge_map, sort_keys=True, indent=4, separators=(',', ': ')))

for y in range(1985, 2017):
	year = str(y)
	print('Building edge map for %s...' % year)
	build_edge_map(year)

# EOF