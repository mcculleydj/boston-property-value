import numpy as np
import matplotlib.pyplot as plt
import json

def plot_feature(year):

	with open('../resources/' + year + '_features.json', 'r') as f:
		features = json.load(f)

	pct_incrs = [features[cell]['pct_incr'] for cell in features]
	pct_incrs_arr = np.array(pct_incrs)
	t1 = np.percentile(pct_incrs_arr, 85)
	t2 = np.percentile(pct_incrs_arr, 70)
	t3 = np.percentile(pct_incrs_arr, 55)
	t4 = np.percentile(pct_incrs_arr, 40)
	t5 = np.percentile(pct_incrs_arr, 25)
	

	thresholds = [(t1, 'red'),
	              (t2, 'orange'),
	              (t3, 'yellow'),
	              (t4, 'green'),
	              (t5, 'cyan')]


	# thresholds = [(1.7, 'red'),
	#               (1.2, 'orange'),
	#               (.7, 'yellow'),
	#               (.2, 'green'),
	#               (-.3, 'cyan')]

	for (t, c) in thresholds:
		X1 = []
		X2 = []

		rmv_cells = []

		for cell in features:
			if features[cell]['pct_incr'] >= t:
				rmv_cells.append(cell)
				X1.append(features[cell]['early_net_flow'])
				X2.append(features[cell]['base_val'])

		for cell in rmv_cells:
			del features[cell]

		plt.scatter(X1, X2, color=c, marker='o')

	X1 = []
	X2 = []

	for cell in features:
		X1.append(features[cell]['early_net_flow'])
		X2.append(features[cell]['base_val'])

	plt.scatter(X1, X2, color='blue', marker='o')
	plt.title(year + ': early_net_flow vs base_val')
	figManager = plt.get_current_fig_manager()
	figManager.window.showMaximized()
	plt.show()

	# with open('../resources/' + year + '_features.json', 'r') as f:
	# 	features = json.load(f)

	# for (t, c) in thresholds:
	# 	X1 = []
	# 	X2 = []

	# 	rmv_cells = []

	# 	for cell in features:
	# 		if features[cell]['pct_incr'] >= t:
	# 			rmv_cells.append(cell)
	# 			X1.append(features[cell]['flushed'])
	# 			X2.append(features[cell]['base_val'])

	# 	for cell in rmv_cells:
	# 		del features[cell]

	# 	plt.scatter(X1, X2, color=c, marker='o')

	# X1 = []
	# X2 = []

	# for cell in features:
	# 	X1.append(features[cell]['flushed'])
	# 	X2.append(features[cell]['base_val'])

	# plt.scatter(X1, X2, color='blue', marker='o')
	# plt.title(year + ': flushed vs base_val')
	# figManager = plt.get_current_fig_manager()
	# figManager.window.showMaximized()
	# plt.show()

	# with open('../resources/' + year + '_features.json', 'r') as f:
	# 	features = json.load(f)

	# for (t, c) in thresholds:
	# 	X1 = []
	# 	X2 = []

	# 	rmv_cells = []

	# 	for cell in features:
	# 		if features[cell]['pct_incr'] >= t:
	# 			rmv_cells.append(cell)
	# 			X1.append(features[cell]['net_flow'])
	# 			X2.append(features[cell]['base_val'])
		
	# 	for cell in rmv_cells:
	# 		del features[cell]
		
	# 	plt.scatter(X1, X2, color=c, marker='o')

	# 	X1 = []
	# 	X2 = []

	# for cell in features:
	# 	X1.append(features[cell]['net_flow'])
	# 	X2.append(features[cell]['base_val'])

	# plt.scatter(X1, X2, color='blue', marker='o')
	# plt.title(year + ': net_flow vs base_value')
	# plt.show()


	# SINGLE FEATURE:

	# with open('../resources/' + year + '_features.json', 'r') as f:
	# 	features = json.load(f)

	# X = []
	# Y = []

	# for cell in features:
	# 	X.append(features[cell]['throughput'])
	# 	Y.append(features[cell]['pct_incr'])

	# plt.scatter(X, Y)
	# plt.title(year + ': throughput vs pct_incr')
	# figManager = plt.get_current_fig_manager()
	# figManager.window.showMaximized()
	# plt.show()

	# X = []
	# Y = []

	# for cell in features:
	# 	X.append(features[cell]['inflow'])
	# 	Y.append(features[cell]['pct_incr'])

	# plt.scatter(X, Y)
	# plt.title(year + ': inflow vs pct_incr')
	# figManager = plt.get_current_fig_manager()
	# figManager.window.showMaximized()
	# plt.show()

	# X = []
	# Y = []

	# for cell in features:
	# 	X.append(features[cell]['early_net_flow'])
	# 	Y.append(features[cell]['pct_incr'])

	# plt.scatter(X, Y)
	# plt.title(year + ': early_net_flow vs pct_incr')
	# figManager = plt.get_current_fig_manager()
	# figManager.window.showMaximized()
	# plt.show()

for y in range(1990, 2017):
	year = str(y)
	plot_feature(year)