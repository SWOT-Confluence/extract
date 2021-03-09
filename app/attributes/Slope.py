# Standard imports
from itertools import repeat
from multiprocessing import Pool

# Third party imports
from geopy.distance import geodesic
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

# Local imports
from app.data.config import extract_config

class Slope:
    """Class that represents slope data.
    
    Attributes
    ----------
        coord_dict: dictionary
            slope coordinate data organized by reach
        slope_node: dictionary
            slope node-level data organized by reach with nx by nt (dataframe) values
        slope_reach: dictionary
            slope reach-level data organized by by reach with 1 by nt (series) values
        wse_node: dictionary
            wse node-level data organized by reach with nx by nt (dataframe) values
        TIME_STEPS: integer
            Class attribute that stores the number of time steps
        topology: Topology
            Topology object that represents topology data
    """

    TIME_STEPS = 9862

    def __init__(self, topology, wse_node, basin_num, invalid_nodes):

        self.topology = topology
        self.wse_node = wse_node

        # Remove invalid nodes from topology and organize by reachid
        coord_df = list(topology.topo_data.groupby("reachid"))
        self.coord_dict = { basin_num + '_' + element[0] : element[1] for element in coord_df }

        # Use coordinate data and wse data to calculate slope (reach and node)
        self.slope_reach = self._create_reach_dict() 
        self.slope_node = self._create_node_dict()

    def _create_reach_dict(self):
        """Uses linear regression to calculate the reach-level slope."""

        # Determine the slope in parallel for each reach
        temp_list = []
        coord_iter = repeat(self.coord_dict, times = len(self.wse_node.items()))
        wse_coord_iter = zip(self.wse_node.items(), coord_iter)
        with Pool(extract_config["no_cores"]) as pool:
            temp_list = pool.starmap(_calculate_reach, wse_coord_iter)

        # Convert results of parallel processing into a dictionary with key of reachid
        reach_dict = { element[0] : element[1] for element in temp_list }

        return reach_dict
    
    def _create_node_dict(self):
        """Appends reach-level slope values to the node to produce an nx by nt matrix."""

        node_dict = {}
        for key, value in self.slope_reach.items():
            # Repeat reach slope values to fit a nx by nt matrix
            value_tile = np.tile(value.to_numpy(), (self.wse_node[key].shape[0], 1))

            # Create a dataframe with repeated values
            node_df = pd.DataFrame(value_tile)
            
            # Insert node identifiers as an index to the dataframe
            node_df.insert(0, "nodeid", self.coord_dict[key].index.to_numpy())
            node_df.set_index("nodeid", inplace = True)
            
            # Apply a mask of wse NaN values to slope node df
            node_df.mask(self.wse_node[key].isna(), np.nan, inplace=True)

            # Save node level data
            node_dict[key] = node_df

        return node_dict

def _calculate_reach(wse_node_dict, coord_dict):
        """Run a linear regression on distance and height data to determine slope."""
        
        # Get distances from each node to the start node (first in reach)
        node_distances = _create_node_distance_list(coord_dict[wse_node_dict[0]])
        
       # Run linear regression on each time step
        slope_series = wse_node_dict[1].apply(_apply_linear_regression, node_dist = node_distances)
        
        # Return a list of reachid and slope values
        return [wse_node_dict[0], slope_series]

def _create_node_distance_list(coord_df):
    """Calculate the distance of each node from the start node."""
    
    # Define start node and set distance to 0 for start node
    start_node = coord_df.iloc[0]

    # Run a function to calculate distance on each row in the value DF
    distance_df = coord_df.apply(_calculate_distance, 
                            axis = 1, start_node = start_node)
    return distance_df

def _calculate_distance(row, start_node):
        """Calculates the distance between the start_node and the node found at 
        the row parameter."""

        # Start node latitude and longitude
        start = (start_node["lat"], start_node["lon"])
        
        # Current node latitude and longitude
        current = (row["lat"], row["lon"])
        
        # Return the distance
        return geodesic(start, current).meters

def _apply_linear_regression(column, node_dist):
    """Apply linear regression on column (time step) and node distance."""

    # Dependent variable (y) - heights
    height = column.to_numpy()
    
    # Mask out NaNs and return NaN if no height data is present
    mask = ~np.isnan(height)
    height = height[mask]
    if len(height) < 5:
        return np.nan

    # Independent variable (x) - node distances
    node_dist = node_dist.to_numpy()[mask]
    distance = node_dist.reshape((-1, 1))
    
    # Create and fit Linear Regression model
    model = LinearRegression().fit(distance, height)
    
    # Return slope
    return -model.coef_[0]