"""
Implementation of plotting methods
for use with the examples in Python Machine Learning
"""

import numpy as np
import matplotlib.pyplot as plt

from matplotlib.colors import ListedColormap

# note that this method is restricted to five classes

def plot_decision_regions(X, y, classifier, resolution=0.02, labels=None, test_idx=None):

	# setup marker generator and color map
	markers = ('s', 'x', 'o', '^', 'v') 							# markers tuple
	colors = ('red', 'blue', 'lightgreen', 'gray', 'cyan') 			# colors tuple
	cmap = ListedColormap(colors[:len(np.unique(y))]) 				# create a colormap with a color
																	# for each outcome
	# plot the decision surface
	x1_min, x1_max = X[:, 0].min() - 1, X[:, 0].max() + 1 			# determine x bounds
	x2_min, x2_max = X[:, 1].min() - 1, X[:, 1].max() + 1 			# determine y bounds

	# numpy.arange(start, stop, step) returns an evenly spaced ndarray
	# numpy.meshgrid(arr1, arr2) -> list of ndarrays
	# |a1| = m and |a2| = n
	# meshgrid(a1, a2)[0] = [[-a1-],                      	m by n that stacks m a1 row vectors
	#                        [-a1-],
	#                         ...,
	#                        [-a1-]]
	# meshgrid(a1, a2)[1] = [[ |  ]  [ |  ]       [ |  ]]   n by m that stacks n a2 col vectors
	#                       [[ a2 ], [ a2 ], ..., [ a2 ]]
	#                       [[ |  ]  [ |  ]       [ |  ]]

	xx1, xx2 = np.meshgrid(np.arange(x1_min, x1_max, resolution),
		                   np.arange(x2_min, x2_max, resolution))

	# ndarray.ravel() flattens the array into a 1-D sequence:
	# e.g. [[1, 3], [2, 4]].ravel() = [1, 3, 2, 4]
	# ndarray.T returns the tranpose
	# so [[1, 3], [2, 4]].T.ravel() = [1, 2, 3, 4]

	# np.array([xx1.ravel(), xx2.ravel()]).T produces a list of all points on the mesh

	Z = classifier.predict(np.array([xx1.ravel(), xx2.ravel()]).T)	# use perceptron to predict each point
	Z = Z.reshape(xx1.shape) 										# reshape Z according to xx1

	plt.contourf(xx1, xx2, Z, alpha=0.4, cmap=cmap)
	plt.xlim(xx1.min(), xx1.max())
	plt.ylim(xx2.min(), xx2.max())

	# plot class samples
	for idx, cl in enumerate(np.unique(y)):
		plt.scatter(x=X[y == cl, 0], y=X[y == cl, 1], 
			        alpha=0.8, c=cmap(idx), 
			        label=labels[idx] if labels is not None else cl,
			        marker=markers[idx])

	# highlight test samples
	if test_idx:
		# X_test, y_test = X[test_idx, :], y[test_idx]
		X_test, y_test = X[range(test_idx, X.shape[0]), :], y[range(test_idx, y.shape[0])]
		plt.scatter(X_test[:, 0], X_test[:, 1], c='',
			        alpha=1.0, linewidths=1, marker='o',
			        s=55, label='Test Set')

def combine(X_trn, X_tst, y_trn, y_tst):
	X_cmb = np.vstack((X_trn, X_tst))
	y_cmb = np.hstack((y_trn, y_tst))
	return X_cmb, y_cmb, X_trn.shape[0]

# EOF
