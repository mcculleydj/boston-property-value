Assumptions:

- By filtering on pCodes as of 2016 I am discounting parcels that were residential in the past. I have no idea what the impact of this decision might be, but I believe there were far more industrial or commercial properties that became residential than the other way around.
- I do not have access to historical living area data. Therefore, I am making an assumption that living area for a given parcel has not changed over time.
- My choice of 0.1 miles for the side length of the hexagonal cells is arbitrary.
- My choice of a minimum of 30,000 square feet and 10 parcels for cell liveness is arbitrary. However, allowing cells covering a relatively large area with a low number of residential parcels to live places too much stock in a very small sample.
- My choice of eight cells as the radius defining a neighborhood (for generating weak edges) is dependent on cell size and seemed appropriate for Boston. This may not be a good choice for other cities.

Source Files (in order of execution):

1. initialize_collections.py	Drops and creates all necessary collections in a MongoDB instance. Assumes that a database named “repo” has already been created. The following collections are dropped and created: `asmts_2016, parcels, missing_parcels, failed_parcels, parcels_w_loc, parcels_wo_loc, parcels_misloc, residential, outliers`

1. get_parcels.py	Fetches parcel data from the dataset “2016 Property Assessment” available via Socrata API call from https://data.cityofboston.gov/. Populates asmts_2016 with documents containing pid, latitude, and longitude. Roughly 40% of the location data is not available in this dataset. Eliminates all duplicate parcels.

1. scrape_assessments.py	Uses pid from asmt_2016 to scrape http://www.cityofboston.gov/assessing/search/ using BeautifulSoup. Populates parcels with all of the data available for each parcel. Server side errors are handled as exceptions. Failed attempts are stored in failed¬_parcels for future attempts, if desired. Parcels whose pid does not produce a match in the assessment database are stored in missing_parcels. Whitespace and unit/apt numbers are filtered by the method refine_address to support accurate geocoding. 

1. geocode.py	Uses Google’s Geocode API to geocode all parcels with missing location data. Appends the field loc in accordance with MongoDB geospatial convention. Inserts each geocoded parcel into parcels_w_loc. Parcels that cannot be located or whose address does not begin with a street number are inserted into parcels_wo_loc and parcels that are located outside of Boston are inserted into parcels¬-_misloc. Finally, each parcel with existing location data is added to parcels_w_loc with the latitude and longitude fields replaced by the loc field.
filter_residential.py	Filters parcels¬_w_loc for parcels with at least 300 square feet of living area and a p_code identifying the parcel as a condo, single-family home, two-family home, three-family home, or four to six-unit apartment building during the latest assessment. The parcels that remain are stored in residential. 

1. add_vpsf.py	For all documents in residential and for all years in a given document’s history adds vpsf (value per square foot) to history.yyyy if the parcel was of a residential type during that year and assessed value was greater than $20,000.
delete_outliers.py	For all years between 1985 and 2016, examines all documents in residential and collects only those for which history.yyyy.vpsf exists. Uses John Tukey’s method to detect outliers for each year. Eliminates outliers by removing history.yyyy.vpsf for that year. Adds a document in outliers containing year, upper_bound, lower_bound, pid, and vpsf for each vpsf removed from a document in residential.

1. generate_cells.py	Creates a JSON file named cell_data with a complete list of cell objects containing the fields cell_id, lat1, lng1, lat2, lng2, … , lat6, lng6 such that the six points defined by each (lat, lng) demarcate a small hexagonal cell laid out in a rectangle which covers the entire city of Boston.

1. assign_cell_id.py	Leverages MongoDB’s geoWithin feature to map each parcel in residential to its host cell and records it in a new field called cell_id. Features a remap dictionary that can correct obvious geocoding mistakes by reassigning all parcels in one cell to another. For this dataset only the parcels assigned to cell 3354 were obviously out of place. Using remap they were reassigned to 3355.

1. aggregate_cell_data.py	For all cells, for all years between 1985 and 2016, and for all parcels assigned to this cell: if vpsf exists in a given year then this parcel’s vpsf is considered (along with all of the others) to calculate the avg_vpsf for the cell. The living area for every parcel with a vpsf is added to total_area for each year. This script appends total_area, avg_vpsf and count, the number of parcels contributing to avg_vpsf, for each year in each cell if there were any parcels to pull data from. Prior to assigning the avg_vpsf, a JSON file titled inflation is used to adjust the avg_vpsf for inflation so that all values are in 2016 dollars. The aggregate data is stored under a key for each year in the cell_data JSON file.

1. split_cell_data.py	Produces a separate JSON file, YYYY_cell_data, which preserves only the data for that year. The data is stored as a dictionary keyed by cell_id. Every cell and the aggregated data, if any, present in the JSON file cell_data appears in each YYYY_cell_data file. A live field is added to each cell and initialized to false. Cells meeting the liveness threshold based on a total_area of at least 30,000 ft2 and a count of at least 10 parcels have live set to true. All cells have the fields border, bridge, and bridge_neighbor appended with an initialized value of false.

1. get_adjacent.py (not run, but called in other scripts)	Defines a method get_adj(cell), which returns the six cells adjacent to the parameter cell. This is a common method in the scripts that follow.

1. build_graph.py (not run, but called in other scripts)	Defines a method build_graph(year), which passes over each cell in the corresponding YYYY_cell_data_iter.json file and converts live and border cells to nodes in a graph where edges exist between neighboring cells on the map. This is a common method in the scripts that follow.

1. cells_within.py (not run, but called in other scripts)	Defines a recursive method cells_within(cells, center_cell, cell_set, n) that returns the set of cells within n hops of the center_cell.

1. connect_graph.py	Defines a method called add_layer(year), which updates the corresponding YYYY_cell_data JSON file by setting the border flag to true for all non-live cells bordering live cells or existing border cells (after the first iteration). Iteratively uses add_layer and build_graph to expand the graph with border cells until it is fully connected. Graphs are constructed using the NetworkX library.

1. detect_bridge_cells.py	A bridge cell is any border cell that lies on a shortest path (note that only one possible shortest path is considered) between each pair of live cells within a radius of eight cells. The NetworkX library provides the framework to produce and search each path for possible bridge cells. The bridge flag is set to true for any border cell meeting these criteria.

1. create_edge_maps.py	Defines a method named build_edge_map(year) which creates a JSON file YYYY_edge_map for a given year storing a dictionary where the key is the cell_id for every live and bridge node identified in the JSON file YYYY_cell_data and the value is a list of adjacent live or bridge nodes.

1. add_weak_edges.py	Defines a method named label_bridge_nodes(year) that sets the bridge_neighbor flag to true for any live node sharing an edge with any bridge node. Defines a method named detect_weak_edges(year) that discovers all the weak edges in the graph. A weak edge exists between two bridge_neighbors within eight cells of each other if the shortest path between them features only bridge nodes and there is no path through a graph of only live nodes of eight or less hops. Builds a new JSON file called YYYY_edge_map_final mapping each live node to a list of its strong (directly adjacent live nodes) and weak edges.

1. run_model.py	Uses YYYY_cell_data and YYYY_edge_map_final to create a graphical model. Each node has a value and total area defined in the cell data and edges are defined by the edge map. The model is stochastic and continues to loop while more than 10% of the original value remains in the graph. During each epoch, value is allowed to flow along edges from higher value nodes to lower value ones proportional to the difference in their values multiplied by a resistance constant (which is different for strong and weak edges). Additionally, during each epoch value is flushed at each node in proportion to the node’s total area subject to a flush constant. The result of running the flow/flush algorithm is stored in a new JSON file named YYYY_cell_state.

1. make_iterable.py	Transforms the dictionary stored in YYYY_cell_data into a list of cells and saves it in a new JSON file YYYY_cell_data_iter for use with D3 and JavaScript to create visuals. Adds some model data from YYYY_cell_state for inclusion in displays. Creates one final entry in each file storing metadata for use with D3 and JavaScript to create visuals.

1. create_vector.py	Utilizes cell_state and cell_data to write JSON files storing machine learning features for use by classify.py. This script is also where the line is drawn separating a positive observation (referred to as target cells in the code) from a negative one. The span between 86-01 is used as training data for supervised learning. The span between 01-16 is used to test the accuracy of the model. This is easily changed to any time span. Originally, I attempted to make predictions on a five-year basis, but short term market behavior has too great an impact on the results. Changes in cell value over 10 – 15 years is independent of the overall market and indicative of the actual changes taking place within those neighborhoods.

1. classify.py	Selects features to optimize performance of the cells selected by the model. Experimentation was done with several classifiers and ultimately an SVM with an RBF kernel was chosen for its consistently high performing results. The next highest performing classifier was an MLP neural network, but was not consistent when applied to various time spans.

Border municipalities (counterclockwise)

Winthrop – East Boston
Revere – East Boston
Chelsea – East Boston and Charlestown
Everett – Charlestown 
Somerville – Charlestown 
Cambridge – Allston, Back Bay, West End (spans the Charles River)
Watertown – Allston, Brighton
Newton – Brighton, West Roxbury
Brookline – Allston, Brighton, JP, West Roxbury, Fenway, Mission Hill, etc
Deadham – West Roxbury, Readville, Hyde Park
Milton – Mattapan, Ashmont, Hyde Park, Readville
Quincy – Ashmont, Neponset/Port Norfolk
