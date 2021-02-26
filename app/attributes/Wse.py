# Third party imports
import numpy as np
import pandas as pd

# Local imports
from app.attributes.Utilities import create_mean_series, create_reach_dict, extract_node_data_txt, get_line_num

class Wse:
    """Class that represents wse data.
    
    Attributes
    ----------
        file : Path
            Path to .stage file
        wse_node: dictionary
            wse node-level data organized by reach with nx by nt (dataframe) values
        wse_reach: dictionary
            wse reach-level data organized by reach with 1 by nt (series) values
        topology: Topology
            Topology object that represents data found in file
    """

    def __init__(self, file, topology, basin_num):
        self.file = file
        self.topology = topology
        
        # Add base elevation to node evelation - replacing all zero values with NaN
        base_data = _extract_base_data(self.file, self.topology.num_nodes)
        node_data = extract_node_data_txt(self.file, "Time;", self.topology)
        node_data.replace(0, np.nan, inplace = True)
        df = node_data.add(base_data["elev"], axis = "index")

        # Create node-level and reach-level dataframes for each reach
        self.wse_node = create_reach_dict(df, self.topology, basin_num)
        self.wse_reach = create_mean_series(self.wse_node)

def _extract_base_data(file, num_nodes):
    """Extracts base elevation matrix from file attribute."""
    
    header_end = get_line_num(file, "Stage information") + 1
    base_data = pd.read_csv(file, 
        skiprows = range(0, header_end), 
        nrows = num_nodes,
        header = None, 
        delim_whitespace = True)
    base_data.columns = ["node", "x", "y", "elev"]
    base_data.set_index("node", inplace = True)
    return base_data