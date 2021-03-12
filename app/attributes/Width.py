# Third party imports
import numpy as np
import pandas as pd

# Local imports
from app.attributes.Utilities import create_mean_series, create_reach_dict, extract_node_data_shp

class Width:
    """Class that represents a .slope file.
    
    Attributes
    ----------
        file: Path
            Path to shapefile for slope data
        topology: Topology
            Topology object that represents topology data
        TIME_STEPS: integer
            Class attribute that stores the number of time steps
        width_node: dictionary
            width node-level data organized by reach with nx by nt (dataframe) values
        width_reach: dictionary
            width reach-level data organized by reach with 1 by nt values
    """

    TIME_STEPS = 9862
    TIME_STEPS_500 = 9362

    def __init__(self, file, topology, basin_num, invalid_nodes):
        self.file = file
        self.topology = topology
        
        # Replace invalid nodes with NaN and organize dataframe by reach
        df = extract_node_data_shp(file, self.topology)
        df.loc[invalid_nodes[basin_num], :] = np.nan
        df_dict = create_reach_dict(df, self.topology, basin_num)

        # Create node-level and reach-level dataframes for each reach
        self.width_node = _create_node_dict(df_dict)
        self.width_reach = create_mean_series(self.width_node)

def _create_node_dict(df_dict):
    """Append node-level width data to each dataframe in the df_dict parameter."""

    node_dict = {}
    for key, value in df_dict.items():
        # Drop coordinate columns
        value.drop(labels = ["x", "y", "index"], axis = 1, inplace = True)
        
        # Repeat width value along columns (time steps)
        value_tile = np.tile(value.astype("float64").to_numpy(), (1, Width.TIME_STEPS_500))
        
        # Create a dataframe with repeated width data
        width_df = pd.DataFrame(value_tile, columns = np.arange(500, Width.TIME_STEPS))
        
        # Insert node values as an index to the dataframe
        width_df.insert(0, "node", np.array(value.index))
        width_df.set_index("node", inplace = True)
        node_dict[key] = width_df

    return node_dict