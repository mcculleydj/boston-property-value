import json
import networkx

from get_adjacent import get_adj
from build_graph import build_graph
from cells_within import cells_within

# radius determining if a path through border cells

RADIUS = 8

# flags border cells as bridge cells
# if the cell lies on the shortest path between two live cells
# and that path is less than RADIUS hops (a choice based on studying the graph)

def detect_bridge_cells(year):
	
	G = build_graph(year)

	# read annual data
	with open('../resources/' + year + '_cell_data.json', 'r') as f:
		cells = json.load(f)

	border_cells = {k for k in cells if cells[k]['border']}
	live_cells = {k for k in cells if cells[k]['live']}
	all_cells = border_cells.union(live_cells)

	bridge_cells = set()

	for cell in live_cells:
		neighborhood = cells_within([cell], cell, set(), RADIUS)
		for neighbor in neighborhood:
			if neighbor in live_cells:
				path = networkx.shortest_path(G, cell, neighbor)[1:-1]
				for path_cell in path:
					if path_cell in border_cells:
						bridge_cells.add(path_cell)
	
	for cell in bridge_cells:
		cells[cell]['bridge'] = True

	# write annual data
	with open('../resources/' + year + '_cell_data.json', 'w') as f:
		f.write(json.dumps(cells, indent=4, sort_keys=True, separators=(',', ':')))

for y in range(1985, 2017):
	year = str(y)
	print('Detecting bridge cells for %s...' % year)	
	bridge_cells = detect_bridge_cells(year)

# EOF
