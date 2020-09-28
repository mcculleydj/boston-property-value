import math
import json

# cells are regular hexagons

S = .1 	# length of one side in miles

# source of lat/lng constants for Boston: 
# http://www.csgnetwork.com/degreelenllavcalc.html

miles_per_deg_lng_max = 51.29596230182694 # @ 42.23 N
miles_per_deg_lng_min = 51.16540876636814 # @ 42.39 N
miles_per_deg_lng = (miles_per_deg_lng_max + miles_per_deg_lng_min) / 2
miles_per_deg_lat = 69.02180802079067

# distance between centers in miles

x_step_miles = 1.5 * S
y_step_miles = S * math.sqrt(3)

# distance between centers in degrees of lat/lng

x_step_lng = x_step_miles / miles_per_deg_lng
y_step_lat = y_step_miles / miles_per_deg_lat

X = 14   # distance in miles to cover along x-axis
Y = 16   # distance in miles to cover along y-axis

n_x = int(X / x_step_miles)		# number of x_steps to cover X
n_y = int(Y / y_step_miles)		# number of y_steps to cover Y

# origin chosen to be further west and south than any point in Boston

y0 =  42.213600
x0 = -71.227413

centers = []

for i in range(n_x):
	lng = x0 + x_step_lng * i
	if i % 2 == 0:
		y0_ = y0
	else:
		y0_ = y0 + y_step_lat / 2 	# laterally adj cells are half a hex higher
	for j in range(n_y):
		lat = y0_ + y_step_lat * j
		centers.append((lat, lng))

### for testing only - cell centers should be equidistant ###
# def distance(p1, p2):
# 	x1 = miles_per_deg_lng * p1[1]
# 	x2 = miles_per_deg_lng * p2[1]
# 	y1 = miles_per_deg_lat * p1[0]
# 	y2 = miles_per_deg_lat * p2[0]
# 	return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
#############################################################

cells = []
cell_id = 0

for c in centers:
	x = miles_per_deg_lng * c[1]
	y = miles_per_deg_lat * c[0]

	p1_ = (y - y_step_miles / 2, x - S / 2)
	p2_ = (y - y_step_miles / 2, x + S / 2)
	p3_ = (y                   , x + S)
	p4_ = (y + y_step_miles / 2, x + S / 2)
	p5_ = (y + y_step_miles / 2, x - S / 2)
	p6_ = (y                   , x - S)

	p1 = (p1_[0] / miles_per_deg_lat, p1_[1] / miles_per_deg_lng)
	p2 = (p2_[0] / miles_per_deg_lat, p2_[1] / miles_per_deg_lng)
	p3 = (p3_[0] / miles_per_deg_lat, p3_[1] / miles_per_deg_lng)
	p4 = (p4_[0] / miles_per_deg_lat, p4_[1] / miles_per_deg_lng)
	p5 = (p5_[0] / miles_per_deg_lat, p5_[1] / miles_per_deg_lng)
	p6 = (p6_[0] / miles_per_deg_lat, p6_[1] / miles_per_deg_lng)

	cells.append({'cell_id': cell_id,
				  'lat1': p1[0],
				  'lng1': p1[1],
				  'lat2': p2[0],
				  'lng2': p2[1],
			 	  'lat3': p3[0],
				  'lng3': p3[1],
				  'lat4': p4[0],
				  'lng4': p4[1],
				  'lat5': p5[0],
				  'lng5': p5[1],
				  'lat6': p6[0],
				  'lng6': p6[1]})
	cell_id += 1

with open('../resources/cell_data.json', 'w') as f:
	f.write(json.dumps(cells, sort_keys=True, indent=4, separators=(',', ': ')))

# EOF
