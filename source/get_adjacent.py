# get_adj is brittle and succeeds only due to an underlying
# understanding of the raw cell map produced by generate_cells.py

# given a cell, returns a list of the six adjacent cells

def get_adj(cell_id):

	isEven = (cell_id // 92) % 2 == 0
	adj_cells = []
	
	if isEven:
		adj_cells.append(cell_id + 1)		# top
		adj_cells.append(cell_id + 92)		# top_right
		adj_cells.append(cell_id + 91)		# bot_right
		adj_cells.append(cell_id - 1)		# bot
		adj_cells.append(cell_id - 93)		# bot_left
		adj_cells.append(cell_id - 92)		# top_left
	else:
		adj_cells.append(cell_id + 1)		# top
		adj_cells.append(cell_id + 93)		# top_right
		adj_cells.append(cell_id + 92)		# bot_right
		adj_cells.append(cell_id - 1)		# bot
		adj_cells.append(cell_id - 92)		# bot_left
		adj_cells.append(cell_id - 91)		# top_left
	
	return adj_cells

# EOF
