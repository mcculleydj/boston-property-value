import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import pml_plot

from sklearn.cross_validation import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.externals import joblib
from sklearn.linear_model import LogisticRegression
from sklearn import svm
from sklearn.neural_network import MLPClassifier

for y in range(1990, 2017):
	year = str(y)

	with open('../resources/' + year + '_cell_data_iter.json', 'r') as f:
		cells = json.load(f)

	with open('../resources/' + year + '_features.json', 'r') as f:
		features = json.load(f)

	# print('Building dataframe for %s...' % year)

	# df_cells = pd.read_json('../resources/' + year + '_features.json', orient='index')
	# df_cells.columns = ['base_val',			# 0
	#                     'count',			# 1
	#                     'curr_val',			# 2
	#                     'early_net_flow',	# 3
	#                     'flush_ratio',		# 4
	#                     'flushed',			# 5
	#                     'inflow',			# 6
	#                     'max_flow_hist',	# 7
	#                     'min_flow_hist',	# 8
	#         			'net_flow',			# 9
	#         			'num_strong_edges', # 10
	#         			'num_weak_edges',	# 11
	#         			'outflow',			# 12
	#         			'pct_incr',			# 13
	#         			'throughput',		# 14
	#         			'total_area']		# 15

	# # print(df_cells.head(5))
	# pct_incrs = df_cells[['pct_incr']].as_matrix()
	# t1 = np.percentile(pct_incrs, 80)
	# t2 = np.percentile(pct_incrs, 60)
	# t3 = np.percentile(pct_incrs, 40)
	# t4 = np.percentile(pct_incrs, 20)

	for i in range(len(cells)-1):
		cell_id = cells[i]['cell_id']
		if cell_id in features:
			pct_incr = features[cell_id]['pct_incr']
			cells[i]['pct_incr'] = pct_incr
			# if pct_incr >= t1:
			# 	cells[i]['performance'] = 't1'
			# elif pct_incr >= t2 and pct_incr < t1:
			# 	cells[i]['performance'] = 't2'
			# elif pct_incr >= t3 and pct_incr < t2:
			# 	cells[i]['performance'] = 't3'
			# elif pct_incr >= t4 and pct_incr < t3:
			# 	cells[i]['performance'] = 't4'
			# else:
			# 	cells[i]['performance'] = 't5'

	with open('../resources/' + year + '_cell_data_iter.json', 'w') as f:
		f.write(json.dumps(cells, indent=4, separators=(',', ': ')))

	# perf_targets = [0, 1, 2, 3, 4]

	# df_cells['performance'] = (df_cells['pct_incr'] >= t1).astype(int)
	
# 	# abv_thr = df_cells[['abv_thrshld']].as_matrix()
# 	# count = [1 for i in abv_thr if i == 1]
# 	# print(sum(count))
# 	# [0, 1, 3, 4, 5, 6, 7, 9]
# 	# [4, 6]
# 	# [0, 6]
# 	# [0, 4]
# 	X, y = df_cells.iloc[:, [0, 4]].values, df_cells.iloc[:, 10].values
# 	X_trn, X_tst, y_trn, y_tst = train_test_split(X, y, test_size=0.3, random_state=0)

# 	stdsc = StandardScaler()
# 	X_trn_std = stdsc.fit_transform(X_trn)
# 	X_tst_std = stdsc.transform(X_tst)

# 	if year == '1990':
# 		X_trn_all = X_trn_std
# 		X_tst_all = X_tst_std
# 		y_trn_all = y_trn
# 		y_tst_all = y_tst
# 	else:
# 		X_trn_all = np.vstack((X_trn_all, X_trn_std))
# 		X_tst_all = np.vstack((X_tst_all, X_tst_std))
# 		y_trn_all = np.hstack((y_trn_all, y_trn))
# 		y_tst_all = np.hstack((y_tst_all, y_tst))


# # clf = MLPClassifier(solver='lbfgs', alpha=1e-5, 
# # 	                hidden_layer_sizes=(5, 2), random_state=1)
# clf = svm.SVC(C=50.0, cache_size=200, class_weight=None, coef0=0.0,
#     decision_function_shape=None, degree=3, gamma='auto', kernel='rbf',
#     max_iter=-1, probability=False, random_state=None, shrinking=True,
#     tol=0.001, verbose=False)
# # clf = LogisticRegression(C=.1)
# # clf = RandomForestClassifier(criterion='entropy', n_estimators=250,
# 	                            # random_state=1, n_jobs=4) 	# n_jobs: use n cores

# clf.fit(X_trn_all, y_trn_all)  

# y_prd_all = clf.predict(X_tst_all)

# print('Overall accuracy: ', round(accuracy_score(y_tst_all, y_prd_all), 3))

# joblib.dump(clf, '../resources/classifier.pkl')

# labels = ['below', 'above']
# X_cmb_std, y_cmb, test_idx = pml_plot.combine(X_trn_all, X_tst_all, y_trn_all, y_tst_all)
# pml_plot.plot_decision_regions(X_cmb_std, y_cmb, clf, 
# 	                           test_idx=test_idx, labels=labels)
# plt.xlabel('Flush Ratio [standardized]')
# plt.ylabel('Net Flow [standardized]')
# plt.title('Cell Classification - LR')
# plt.legend(loc='upper left')
# plt.show()

# forest = joblib.load('../resources/classifier.pkl')

# # Try on 2000:
# for y in range(1990, 1991):
# 	year = str(y)

# 	with open('../resources/' + year + '_features.json', 'r') as f:
# 		features = json.load(f)

# 	print('Building dataframe for %s...' % year)

# 	df_cells = pd.read_json('../resources/' + year + '_features.json', orient='index')
# 	df_cells.columns = ['base_val',
# 	                    'count',
# 	                    'curr_val',
# 	                    'early_net_flow',
# 	                    'flush_ratio',
# 	                    'flushed',
# 	        			'net_flow',
# 	        			'num_edges',
# 	        			'pct_incr',
# 	        			'total_area']

# 	# print(df_cells.head(5))
# 	pct_incrs = df_cells[['pct_incr']].as_matrix()
# 	# print(type(pct_incrs))
# 	threshold = np.percentile(pct_incrs, 85)

# 	print('85th percentile threshold for parcels in %s is %f...' % (year, threshold))

# 	df_cells['abv_thrshld'] = (df_cells['pct_incr'] >= threshold).astype(int)

# 	X, y = df_cells.iloc[:, [0, 1, 3, 4, 5, 6, 7, 9]].values, df_cells.iloc[:, 10].values

# 	stdsc = StandardScaler()
# 	X_std = stdsc.fit_transform(X)

# 	y_prd = forest.predict(X)

# 	print(type(y_prd))
# 	print(y_prd.shape)

# 	count = [1 for i in y_prd if i == 1]
# 	print(sum(count))
# 	y_compare = np.not_equal(y, y_prd)
# 	count = [1 for tf in y_compare if tf]
# 	print(sum(count))
# 	# print(y_compare)

# 	print('%s accuracy: %f' % (year, accuracy_score(y_prd, y)))


# Feature Importance

# importances = forest.feature_importances_
# std = np.std([tree.feature_importances_ for tree in forest.estimators_],
#              axis=0)
# indices = np.argsort(importances)[::-1]

# # Print the feature ranking
# print("Feature ranking:")

# for f in range(X_trn_all.shape[1]):
#     print("%d. feature %d (%f)" % (f + 1, indices[f], importances[indices[f]]))

# # Plot the feature importances of the forest
# plt.figure()
# plt.title("Feature importances")
# plt.bar(range(X_trn_all.shape[1]), importances[indices],
#        color="r", yerr=std[indices], align="center")
# plt.xticks(range(X_trn_all.shape[1]), indices)
# plt.xlim([-1, X_trn_all.shape[1]])
# plt.show()