from get_adjacent import get_adj

# recursively discovers the cells within
# n hops from center_cell

def cells_within(cells, center_cell, cell_set, n):
	if n > 0:
		new_cells = []
		for cell in cells:
			adj_cells = [str(c) for c in get_adj(int(cell))]
			for adj_cell in adj_cells:
				if adj_cell not in cell_set:
					cell_set.add(adj_cell)
					new_cells.append(adj_cell)
		return cells_within(new_cells, center_cell, cell_set, n - 1)
	else:
		cell_set.remove(center_cell)
		return cell_set

# EOF
