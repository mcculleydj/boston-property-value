import json
import networkx as nx
import matplotlib.pyplot as plt
import graphviz

with open('../resources/2016_edge_map_final.json', 'r') as f:
	edge_map = json.load(f)

with open('../resources/cell_centers.json', 'r') as f:
	centers = json.load(f)

edges = set()


# node_list = ['5667',
#              '5669',
#              '5579',
#              '5580',
#              '5581',
#              '5487',
#              '5488',
#              '5489',
#              '5391',
#              '5396',
#              '5397',
#              '5208',
#              '5210',
#              '5211',
#              '5117',
#              '5118']

G = nx.Graph()

for node in edge_map:
	# if node in node_list:
	strong_edges = edge_map[node]['strong']
	weak_edges = edge_map[node]['weak']

	for adj_node in strong_edges:
		# if adj_node in node_list:
		G.add_edge(node, adj_node, weight=1)

	for adj_node in weak_edges:
		# if adj_node in node_list:
		G.add_edge(node, adj_node, weight=0)

estrong = [(u,v) for (u,v,d) in G.edges(data=True) if d['weight'] > 0.5]
eweak = [(u,v) for (u,v,d) in G.edges(data=True) if d['weight'] <= 0.5]

init_pos = {}
fixed = [node for node in edge_map]

for cell in centers:
	center = centers[cell]
	center = [coord for coord in center]
	init_pos[cell] = center

pos = nx.spring_layout(G, dim=2, k=.1, pos=init_pos, fixed=fixed, 
	                iterations=50, weight='weight', scale=1.0)

plt.figure(figsize=(4, 4))
frame = plt.gca()
frame.axes.get_xaxis().set_visible(False)
frame.axes.get_yaxis().set_visible(False)

nx.draw_networkx_nodes(G, pos, node_size=10)

nx.draw_networkx_edges(G, pos, edgelist=estrong, width=1)
nx.draw_networkx_edges(G, pos, edgelist=eweak, 
	                   width=1, alpha=0.5, edge_color='b', 
	                   style='dashed')


plt.show()

# plt.savefig('../visuals/graph.tif', format='tif', dpi=1200)
