import json
import networkx

from get_adjacent import get_adj
from build_graph import build_graph

# sets border_cell flag to True
# for all cells adjacent to live cells on the first call
# or all cells adjacent to border cells on subsequent calls

def add_layer(year):

	# read annual data
	with open('../resources/' + year + '_cell_data.json', 'r') as f:
		cells = json.load(f)

	live_cells = {k for k in cells if cells[k]['live']}
	current_border_cells = {k for k in cells if cells[k]['border']}	
	all_cells = live_cells.union(current_border_cells)
	new_border_cells = set()

	# if current_border_cells is non-empty (only consider border cells)
	if current_border_cells:
		for cell in current_border_cells:
			adj_cells = [str(c) for c in get_adj(int(cell))]
			border_cells = {cell for cell in adj_cells if cell not in all_cells}
			new_border_cells = new_border_cells.union(border_cells)
	
	# if current_border_cells is empty (only consider live cells)
	else:
		for cell in live_cells:
			adj_cells = [str(c) for c in get_adj(int(cell))]
			border_cells = {cell for cell in adj_cells if cell not in live_cells}
			new_border_cells = new_border_cells.union(border_cells)

	# set flag
	for cell in new_border_cells:
		cells[str(cell)]['border'] = True

	# write annual data
	with open('../resources/' + year + '_cell_data.json', 'w') as f:
		f.write(json.dumps(cells, indent=4, sort_keys=True, separators=(',', ':')))

# for all years add layers until the graph is connected

for y in range(1985, 2017):
	year = str(y)
	print('Connecting graph for %s...' % year)
	G = build_graph(year)
	layer = 1
	while not networkx.is_connected(G):
		print('\tAdding border layer #%d...' % layer)
		add_layer(year)
		G = build_graph(year)
		layer += 1

# EOF
