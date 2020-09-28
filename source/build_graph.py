import networkx
import json

from get_adjacent import get_adj

# builds a graph based on annual data
# nodes consist of all live and border cells
# edges exist between adjacent cells

def build_graph(year):
	
	# read annual data
	with open('../resources/' + year + '_cell_data.json', 'r') as f:
		cells = json.load(f)

	border_cells = {k for k in cells if cells[k]['border']}
	live_cells = {k for k in cells if cells[k]['live']}
	all_cells = border_cells.union(live_cells)
	edges = set()

	for cell in all_cells:
		adj_cells = [str(c) for c in get_adj(int(cell))]
		for adj_cell in adj_cells:
			if adj_cell in all_cells:
				edges.add(tuple(sorted((cell, adj_cell))))

	edges = list(edges)
	G = networkx.Graph()
	G.add_nodes_from(all_cells)
	G.add_edges_from(edges)

	return G

# EOF
