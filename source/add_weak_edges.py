import json
import networkx

from get_adjacent import get_adj
from cells_within import cells_within

def label_bridge_neighbors(year):

	with open('../resources/' + year + '_cell_data.json', 'r') as f:
		cells = json.load(f)

	with open('../resources/' + year + '_edge_map.json', 'r') as f:
		edge_map = json.load(f)

	live_cells = {k for k in cells if cells[k]['live']}

	for cell in live_cells:
		edges = edge_map[cell]
		for edge in edges:
			if cells[edge]['bridge'] == True:
				cells[cell]['bridge_neighbor'] = True

	with open('../resources/' + year + '_cell_data.json', 'w') as f:
		f.write(json.dumps(cells, indent=4, sort_keys=True, separators=(',', ':')))

for y in range(1985, 2017):
	year = str(y)
	print('Detecting bridge_neighbors for %s...' % year)	
	label_bridge_neighbors(year)

# builds a graph based on annual data
# nodes consist of only live cells
# edges exist between adjacent live cells

def build_live_graph(year):
	
	# read annual data
	with open('../resources/' + year + '_cell_data.json', 'r') as f:
		cells = json.load(f)

	live_cells = {k for k in cells if cells[k]['live']}
	edges = set()

	for cell in live_cells:
		adj_cells = [str(c) for c in get_adj(int(cell))]
		for adj_cell in adj_cells:
			if adj_cell in live_cells:
				edges.add(tuple(sorted((cell, adj_cell))))

	nodes = list(live_cells)
	edges = list(edges)
	G = networkx.Graph()
	G.add_nodes_from(nodes)
	G.add_edges_from(edges)

	return G

def build_graph_from_edge_map(year):
	
	with open('../resources/' + year + '_edge_map.json', 'r') as f:
		edge_map = json.load(f)

	edges = set()

	# no need to include nodes without edges
	# because no path will exist if no edges exist

	for cell in edge_map:
		adj_cells = edge_map[cell]
		for adj_cell in adj_cells:
			edges.add(tuple(sorted((cell, adj_cell))))

	edges = list(edges)
	G = networkx.Graph()
	G.add_edges_from(edges)

	return G

def detect_weak_edges(year):
	
	G = build_graph_from_edge_map(year)
	G_live = build_live_graph(year)

	with open('../resources/' + year + '_cell_data.json', 'r') as f:
		cells = json.load(f)

	with open('../resources/' + year + '_edge_map.json', 'r') as f:
		edge_map = json.load(f)

	for cell in cells:
		if cells[cell]['bridge']: 
			del edge_map[cell]

	for cell in edge_map:
		adj_cells = edge_map[cell]
		edge_map[cell] = {}
		edge_map[cell]['strong'] = []
		edge_map[cell]['weak'] = []
		edge_map[cell]['strong'] = [adj_cell for adj_cell in adj_cells if cells[adj_cell]['live']]

	bridge_neighbors = {k for k in cells if cells[k]['bridge_neighbor']}
	bridge_cells = {k for k in cells if cells[k]['bridge']}

	for cell in bridge_neighbors:
		radius = 2
		while (len(edge_map[cell]['strong']) +
			   len(edge_map[cell]['weak'])) < 6 and radius < 9:

			neighborhood = cells_within([cell], cell, set(), radius)
			
			for neighbor in neighborhood:
				if (neighbor in bridge_neighbors and 
					neighbor not in edge_map[cell]['weak'] and
					(len(edge_map[neighbor]['strong']) + 
				     len(edge_map[neighbor]['weak'])) < 6):

					path = networkx.shortest_path(G, cell, neighbor)[1:-1]
					bridge_only = [cells[path_cell]['bridge'] for path_cell in path]
					if all(bridge_only):
						if networkx.has_path(G_live, cell, neighbor):
							if len(networkx.shortest_path(G_live, cell, neighbor)) > 10: # extra two for source, target inclusion 
								edge_map[cell]['weak'].append(neighbor)
								edge_map[neighbor]['weak'].append(cell)
								if (len(edge_map[cell]['strong']) +
									len(edge_map[cell]['weak'])) >= 6:
									break
						else:
							edge_map[cell]['weak'].append(neighbor)
							edge_map[neighbor]['weak'].append(cell)
							if (len(edge_map[cell]['strong']) +
								len(edge_map[cell]['weak'])) >= 6:
								break
			radius += 1

	with open('../resources/' + year + '_edge_map_final.json', 'w') as f:
		f.write(json.dumps(edge_map, indent=4, sort_keys=True, separators=(',', ':')))

for y in range(1985, 2017):
	year = str(y)
	print('Detecting weak edges for %s...' % year)	
	detect_weak_edges(year)

# EOF