# Standard imports
import warnings

# Third party imports
import numpy as np
import pandas as pd

# Local imports
from app.attributes.Utilities import create_reach_dict, extract_node_data_txt

class Discharge:
    """Class that represents discharge data.

    Attributes
    ----------
        file: Path
            Path to .discharge file
        q_node: dictionary
            discharge node-level data organized by reach with nx by nt (dataframe) values
        qhat_reach: dictionary
            Prior mean discharge for each reach (scalar)
        qsd_reach: dictionary
            Standard deviation of discharge for each reach (scalar)
        topology: Topology
            Topology object that represents topology data
    """

    def __init__(self, file, topology, basin_num):
        self.file = file

        # Obtain discharge data in a dataframe
        self.topology = topology
        df = extract_node_data_txt(self.file, "Time;", self.topology)
        df.replace(0.0, np.NaN, inplace = True)
        self.q_node = create_reach_dict(df, self.topology, basin_num)
        
        # Calculate SWORD of Science data: Qhat and Qsds
        sword_data = _calculate_qhat_qsd(self.q_node)
        self.qhat_reach = sword_data["qhat_reach"]
        self.qsd_reach = sword_data["qsd_reach"]

def _calculate_qhat_qsd(discharge_data):
    """Calculate qhat and qsd attributes using discharge_data parameter and 
    returns a dictionary organized by reach."""

    qhat_reach_dict = {}
    qsd_reach_dict = {}
    for key, value in discharge_data.items():

        # Handle RuntimeWarnings for cases where value contains all NaNs
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)

            # Calculate the mean
            mean = np.nanmean(value.values)
            qhat_reach_dict[key] = mean
            
            # Calculate the standard deviation
            sd = np.nanstd(value.values)
            qsd_reach_dict[key] = sd
    
    return { "qhat_reach" : qhat_reach_dict, 
                "qsd_reach" :  qsd_reach_dict }