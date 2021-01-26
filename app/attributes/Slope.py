# Standard imports
from multiprocessing import Pool

# Third party imports
from geopy.distance import geodesic
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

# Local imports
from app.config import extract_config
from app.attributes.Utilities import create_reach_dict, extract_node_data_shp

class Slope:
    """Class that represents slope data.
    
    Attributes
    ----------
        coord_data: dictionary
            slope coordinate data organized by reach
        slope_node: dictionary
            slope node-level data organized by reach nx by 1 (dataframe) values
        slope_reach: dictionary
            slope reach-level data organized by reach with scalar values
        wse_node: dictionary
            wse node-level data organized by reach with nx by 1 (dataframe) values
        TIME_STEPS: integer
            Class attribute that stores the number of time steps
        topology: Topology
            Topology object that represents topology data
    """

    TIME_STEPS = 9862

    def __init__(self, file, topology, wse_node):
        self.file = file
        self.topology = topology
        self.wse_node = wse_node

        # Extract coordinate data from shapefile and create reach dataframes
        df = extract_node_data_shp(file, self.topology)
        self.coord_data = create_reach_dict(df, self.topology)

        # Use coordinate data and wse data to calculate slope (reach and node)
        self.slope_reach = self._create_reach_dict() 
        self.slope_node = self._create_node_dict()

    def _create_reach_dict(self):
        """Uses linear regression to calculate the reach-level slope."""

        # Determine the slope in parallel for each reach
        temp_list = []
        with Pool(extract_config["no_cores"]) as pool:
            temp_list = pool.map(self._calculate_reach, self.wse_node.items())

        # Convert results of parallel processing into a dictionary with key of reachid
        reach_dict = { element[0] : element[1] for element in temp_list }

        return reach_dict

    def _calculate_reach(self, dict_item):
        """Run a linear regression on distance and height data to determine slope."""
        
        # Independent variable (x) - node distances
        node_dist_array = np.array(self._create_node_distance_list(dict_item[0])).reshape((-1, 1))
        
        # Dependent variable (y) - run linear regression on each time step
        slope_series = dict_item[1].apply(_apply_linear_regression, node_dist = node_dist_array)
        
        # Return a list of reachid and slope values
        return [dict_item[0], slope_series]

    def _create_node_distance_list(self, key):
        """Calculate the distance of each node from the start node."""
        
        # Locate geographic data in slope file
        df = self.coord_data[key]

        # Define start node and set distance to 0 for start node
        start_node = df.iloc[0]
        distance_list = []
        distance_list.append(0)

        # Return distance list for reaches that only have one node
        if df.shape[0] == 1:
            return distance_list
        else:
            # Calculate distance between each node and sort in descending order
            df2 = df.iloc[1:]
            df_list = df2.apply(_calculate_distance, axis = 1, start_node = start_node) \
                .sort_values(ascending = False) \
                .tolist()
            return df_list + distance_list
    
    def _create_node_dict(self):
        """Appends reach-level slope values to the node to produce an nx by nt matrix."""

        node_dict = {}
        for key, value in self.slope_reach.items():
            # Repeat reach slope values to fit a nx by nt matrix
            value_tile = np.tile(value.to_numpy(), (self.wse_node[key].shape[0], 1))
            # Create a dataframe with repeated values
            node_df = pd.DataFrame(value_tile, columns = np.arange(0, self.TIME_STEPS))
            # Insert node values as an index to the dataframe
            node_df.insert(0, "node", np.array(self.wse_node[key].index))
            node_df.set_index("node", inplace = True)
            node_dict[key] = node_df

        return node_dict


def _calculate_distance(row, start_node):
        """Calculates the distance between the start_node and the node found at 
        the row parameter."""

        # Start node latitude and longitude
        start = (start_node["y"], start_node["x"])
        # Current node latitude and longitude
        current = (row["y"], row["x"])
        # Return the distance
        return geodesic(start, current).meters

def _apply_linear_regression(column, node_dist):
        """Apply linear regression on column (time step) and node distance."""

        # Get height data as a numpy array sorted in descending order
        height = np.sort(column.to_numpy())[::-1]
        # Create and fit Linear Regression model
        model = LinearRegression().fit(node_dist, height)
        # Return slope
        return model.coef_[0]