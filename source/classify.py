import pandas as pd
import numpy as np
import json
import random
# import pml_plot
# import matplotlib.pyplot as plt

from get_adjacent import get_adj
from cells_within import cells_within

from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score

# from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC

# for saving classifier between runs
# from sklearn.externals import joblib

# 86-01 training data; 01-16 testing data
spans = [('1986', '2001'), ('2001', '2016')]

trn_path = '../resources/span_' + spans[0][0] + '_' + spans[0][1] + '_features.json'
tst_path = '../resources/span_' + spans[1][0] + '_' + spans[1][1] + '_features.json'

cols = ['abs_flow',
		'count',
		'early_flow',
		'flush_ratio',
		'flushed',
		'inflow',
		'init_flow',
		'late_flow',
		'max_flow',
		'mid_flow',
		'min_flow',
		'net_flow',
		'outflow',
		'rank',
		'str_edges',
		'target',
		'total_area',
		'value',
		'weak_edges']

print('Building training dataframe...')

df_trn = pd.read_json(trn_path, orient='index')
df_trn.columns = cols

print('Building testing dataframe...')

df_tst = pd.read_json(tst_path, orient='index')
df_tst.columns = cols

# Dataframe columns:
# 0: abs_flow
# 1: count
# 2: early_flow
# 3: flush_ratio
# 4: flushed
# 5: inflow
# 6: init_flow
# 7: late_flow
# 8: max_flow
# 9: mid_flow
# 10: min_flow
# 11: net_flow
# 12: outflow
# 13: rank
# 14: str_edges
# 15: target
# 16: total_area
# 17: value
# 18: weak_edges

# Feature selection:
dynamic_cols = [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
static_cols  = [1, 13, 14, 16, 17, 18]
all_cols     = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 16, 17, 18]

# these features result in a 193 rank jump on average
choice_cols  = [3, 4, 5, 6, 7, 8, 12, 13, 18]

# dataframe of only positive target cells in test set:
df_tgt = df_tst[df_tst['target'] == 1]

# X, y split for all three dataframes:
X_trn, y_trn = df_trn.iloc[:, choice_cols].values, df_trn.iloc[:, 15].values
X_tst, y_tst = df_tst.iloc[:, choice_cols].values, df_tst.iloc[:, 15].values
X_tgt, y_tgt = df_tgt.iloc[:, choice_cols].values, df_tgt.iloc[:, 15].values

# normalization
stdsc_trn = StandardScaler()
stdsc_trn.fit(X_trn)
stdsc_tst = StandardScaler()
stdsc_tst.fit(X_tst)

X_trn_std = stdsc_trn.transform(X_trn)
X_tst_std = stdsc_tst.transform(X_tst)
X_tgt_std = stdsc_tst.transform(X_tgt)

print('Training the SVM...')

### future work: use cross-validation techniques on a variety of
###              of datasets to tune hyperparameters

clf = SVC(C=10000, kernel='rbf', degree=4, gamma='auto', 
	      coef0=0.0, shrinking=True, probability=False, tol=0.001, 
	      cache_size=200, class_weight=None, verbose=False,
	      max_iter=-1, decision_function_shape=None, random_state=None)

clf.fit(X_trn_std, y_trn)

# make predictions

y_prd = clf.predict(X_tst_std)
pos_prd = y_prd[y_prd == 1]

print('\nNumber of positive predictions:', len(pos_prd))
print('Accuracy: ', round(accuracy_score(y_tst, y_prd), 3))

y_prd_tgt = clf.predict(X_tgt_std)
pos_prd_tgt = y_prd_tgt[y_prd_tgt == 1]

print('Number of positive predictions on target-only set:', len(pos_prd_tgt))
print('Target-only accuracy: ', round(accuracy_score(y_tgt, y_prd_tgt), 3))
print()

with open('../resources/vector_data.json', 'r') as f:
	vector_data = json.load(f)

tst_keys = list(df_tst.index)

# False positives

false_pos = []

for i in range(len(y_prd)):
	if y_prd[i] == 1 and y_tst[i] == 0:
		false_pos.append(str(tst_keys[i]))

print('Number of false positives: ', len(false_pos))

false_pos_delta_rank = {}
delta_ranks = []

for cell in false_pos:
	delta_ranks.append(vector_data[spans[1][1]][cell])
	false_pos_delta_rank[cell] = delta_ranks.append(vector_data[spans[1][1]][cell])

print('Average delta_rank in false positives: ', 
	  round((sum(delta_ranks) / len(delta_ranks)), 3))

# False negatives:

with open(tst_path, 'r') as f:
	features = json.load(f)

tgts = {cell for cell in features if features[cell]['target'] == 1}

pos = {str(tst_keys[i]) for i in range(len(y_prd)) if y_prd[i] == 1}

false_neg = [cell for cell in tgts if cell not in pos]

print('Number of false negatives: ', len(false_neg))

false_neg_delta_rank = {}
delta_ranks = []

for cell in false_neg:
	delta_ranks.append(vector_data[spans[1][1]][cell])
	false_neg_delta_rank[cell] = delta_ranks.append(vector_data[spans[1][1]][cell])

print('Average delta_rank in false_neg: ', 
	  round((sum(delta_ranks) / len(delta_ranks)), 3))

# edit iter JSON for showing top performing cells on a map

with open('../resources/2001_cell_data_iter.json', 'r') as f:
	cells2001 = json.load(f)

meta = cells2001[-1]
cells2001 = cells2001[:-1]

for cell in cells2001:
	if cell['cell_id'] in tgts:
		cell['target'] = True
	if cell['cell_id'] in pos:
		cell['chosen'] = True

cells2001 = cells2001 + [meta]

with open('../resources/2001_cell_data_iter.json', 'w') as f:
	f.write(json.dumps(cells2001, indent=4, separators=(',', ': ')))

# True positives:

true_pos = [cell for cell in tgts if cell in pos]

print('Number of true positives: ', len(true_pos))

true_pos_delta_rank = {}
delta_ranks = []

for cell in true_pos:
	delta_ranks.append(vector_data[spans[1][1]][cell])
	true_pos_delta_rank[cell] = delta_ranks.append(vector_data[spans[1][1]][cell])

print('Average delta_rank in true_pos: ', 
	  round((sum(delta_ranks) / len(delta_ranks)), 3))

print('Magnitude of the intersection between trn and tst sets:', len(vector_data['overlap']))

true_pos_in_overlap = [cell for cell in true_pos if cell in vector_data['overlap']]

print('Of the %d true positives %d were in the intersection.' % 
	 (len(true_pos), len(true_pos_in_overlap)))

delta_ranks = []

for cell in pos:
	delta_ranks.append(vector_data[spans[1][1]][cell])

print('Average delta_rank in all positives: ', 
	   round((sum(delta_ranks) / len(delta_ranks)), 3))
print()

print('Cells within one hop of selected cells...')

new_cells_to_check = set()

for cell in pos:
	adj = [str(c) for c in get_adj(int(cell))]
	new_cells_to_check.add(cell)
	for c in adj:
		if c in vector_data[spans[1][1]]:
			new_cells_to_check.add(c)

still_miss = []

for c in tgts:
	if c not in new_cells_to_check:
		still_miss.append(c)

print('New results: %d for %d...' % 
	  (len(tgts) - len(still_miss), len(new_cells_to_check)))

delta_ranks = []

for cell in new_cells_to_check:
	delta_ranks.append(vector_data[spans[1][1]][cell])

print('Average delta_rank in one hop expanded search: ', 
	  round((sum(delta_ranks) / len(delta_ranks)), 3))

print('Cells within two hops of selected cells...')

new_cells_to_check = set()

for cell in pos:
	adj = cells_within([cell], cell, set(), 2)
	new_cells_to_check.add(cell)
	for c in adj:
		if c in vector_data[spans[1][1]]:
			new_cells_to_check.add(c)

still_miss = []

for c in tgts:
	if c not in new_cells_to_check:
		still_miss.append(c)

print('New results: %d for %d...' %
	  (len(tgts) - len(still_miss), len(new_cells_to_check)))

delta_ranks = []

for cell in new_cells_to_check:
	delta_ranks.append(vector_data[spans[1][1]][cell])

print('Average delta_rank in 2 hop expanded search: ', 
	   round((sum(delta_ranks) / len(delta_ranks)), 3))
print()

print('\nComparison to some simple heuristics...\n')

print('255 cells at random...')

ks = [str(k) for k in tst_keys]

rs = random.sample(ks, 255)

delta_ranks = []

for cell in rs:
	delta_ranks.append(vector_data[spans[1][1]][cell])

print('Average delta_rank in random selection: ', 
	  round((sum(delta_ranks) / len(delta_ranks)), 3))
print()

print('Same 32 target cells from 86 to 01...')

trn_tgts = []
trn_keys = list(df_trn.index)

for i in range(len(y_trn)):
	if y_trn[i] == 1:
		trn_tgts.append(str(trn_keys[i]))

delta_ranks = []

for cell in trn_tgts:
	delta_ranks.append(vector_data[spans[1][1]][cell])

print('Average delta_rank in orig 32 selection: ', 
	  round((sum(delta_ranks) / len(delta_ranks)), 3))
print()

print('One hop expanded 32 original target cells...')

new_cells_to_check = set()

for cell in trn_tgts:
	adj = [str(c) for c in get_adj(int(cell))]
	new_cells_to_check.add(cell)
	for c in adj:
		if c in vector_data[spans[1][1]]:
			new_cells_to_check.add(c)

still_miss = []

for c in tgts:
	if c not in new_cells_to_check:
		still_miss.append(c)

print('New results: %d for %d...' %
	  (len(tgts) - len(still_miss), len(new_cells_to_check)))

delta_ranks = []

for cell in new_cells_to_check:
	delta_ranks.append(vector_data[spans[1][1]][cell])

print('Average delta_rank in one hop expanded search on original 32: ', 
	  round((sum(delta_ranks) / len(delta_ranks)), 3))
print()

print('Two hop expanded 32 original target cells...')

new_cells_to_check = set()

for cell in trn_tgts:
	adj = cells_within([cell], cell, set(), 2)
	new_cells_to_check.add(cell)
	for c in adj:
		if c in vector_data[spans[1][1]]:
			new_cells_to_check.add(c)

still_miss = []

for c in tgts:
	if c not in new_cells_to_check:
		still_miss.append(c)

print('New results: %d for %d...' %
	  (len(tgts) - len(still_miss), len(new_cells_to_check)))

delta_ranks = []

for cell in new_cells_to_check:
	delta_ranks.append(vector_data[spans[1][1]][cell])

print('Average delta_rank in two hop expanded search on orig 32: ', 
	  round((sum(delta_ranks) / len(delta_ranks)), 3))
print()

print('225 lowest ranked cells in 2001...')

cell_to_rank_map = []

for c in features:
	cell_to_rank_map.append((c, features[c]['rank']))

cell_to_rank_map.sort(key=lambda x: x[1], reverse=True)

lowest_255 = [c for (c, _) in cell_to_rank_map[0:255]]

delta_ranks = []

for cell in lowest_255:
	delta_ranks.append(vector_data[spans[1][1]][cell])

lowest_255_tgts = [cell for cell in lowest_255 if cell in tgts]

print('Number of true_pos in lowest_ranked:', len(lowest_255_tgts))

print('Average delta_rank in lowest-255 selection: ', 
	  round((sum(delta_ranks) / len(delta_ranks)), 3))
print ()

print('Cells ranked 50 through 275 in 2001...')

cell_to_rank_map = []

for c in features:
	cell_to_rank_map.append((c, features[c]['rank']))

cell_to_rank_map.sort(key=lambda x: x[1], reverse=True)

start = (len(cell_to_rank_map)-255) // 2

mid_255 = [c for (c, _) in cell_to_rank_map[50:305]]

delta_ranks = []

for cell in mid_255:
	delta_ranks.append(vector_data[spans[1][1]][cell])

consec_255_tgts = [cell for cell in mid_255 if cell in tgts]

print('Number of true_pos in 50-275:', len(consec_255_tgts))
print('Average delta_rank in 50-275 selection: ', 
	   round((sum(delta_ranks) / len(delta_ranks)), 3))
print()

print('Cells ranked 125 through 380 in 2001...')

cell_to_rank_map = []

for c in features:
	cell_to_rank_map.append((c, features[c]['rank']))

cell_to_rank_map.sort(key=lambda x: x[1], reverse=True)

best_255 = [c for (c, _) in cell_to_rank_map[125:380]]

delta_ranks = []

for cell in best_255:
	delta_ranks.append(vector_data[spans[1][1]][cell])

best_255_tgts = [cell for cell in best_255 if cell in tgts]

print('Number of true_pos between 125-380:', len(best_255_tgts))
print('Average delta_rank in highest-255 selection: ', 
	  round((sum(delta_ranks) / len(delta_ranks)), 3))

# Obsolete code testing alternative classifiers

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

# importances = clf.feature_importances_
# std = np.std([tree.feature_importances_ for tree in clf.estimators_],
#              axis=0)
# indices = np.argsort(importances)[::-1]

# # Print the feature ranking
# print("Feature ranking:")

# for f in range(X_trn.shape[1]):
#     print("%d. feature %d (%f)" % (f + 1, indices[f], importances[indices[f]]))

# # Plot the feature importances of the forest
# plt.figure()
# plt.title("Feature importances")
# plt.bar(range(X_trn.shape[1]), importances[indices],
#        color="r", yerr=std[indices], align="center")
# plt.xticks(range(X_trn.shape[1]), indices)
# plt.xlim([-1, X_trn.shape[1]])
# plt.show()