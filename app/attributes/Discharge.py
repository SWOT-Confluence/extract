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
        qhat_node: dictionary
            Prior mean discharge for each node nx by 1 (dataframe) values
        qsd_node: dictionary
            Standard deviation of discharge for each node nx by 1 (dataframe) values
        qhat_reach: dictionary
            Prior mean discharge for each reach (scalar)
        qsd_reach: dictionary
            Standard deviation of discharge for each reach (scalar)
        topology: Topology
            Topology object that represents topology data
    """

    def __init__(self, file, topology):
        self.file = file
        # Obtain discharge data in a dataframe
        self.topology = topology
        df = extract_node_data_txt(self.file, "Time;", self.topology)
        discharge_data = create_reach_dict(df, self.topology)
        
        # Calculate SWORD of Science data: Qhat and Qsds
        sword_data = self._calculate_qhat_qsd(discharge_data)
        
        # Reach
        self.qhat_reach = sword_data["qhat_reach"]
        self.qsd_reach = sword_data["qsd_reach"]

        # Node
        self.qhat_node = sword_data["qhat_node"]
        self.qsd_node = sword_data["qsd_node"]

    def _calculate_qhat_qsd(self, discharge_data):
        """Calculate qhat and qsd attributes using discharge_data parameter and 
        returns a dictionary organized by reach."""

        qhat_reach_dict = {}
        qsd_reach_dict = {}
        qhat_node_dict = {}
        qsd_node_dict = {}
        for key, value in discharge_data.items():

            # Calculate the mean
            mean = np.mean(value.values)
            qhat_reach_dict[key] = mean
            
            # Calculate the standard deviation
            sd = np.std(value.values)
            qsd_reach_dict[key] = sd

            # Append qhat and qsd to the node level
            qhat_node_dict[key], qsd_node_dict[key] = \
                _calculate_qhat_qsd_node(value, mean, sd)
        
        return { "qhat_reach" : qhat_reach_dict, 
                  "qsd_reach" :  qsd_reach_dict,
                  "qhat_node" : qhat_node_dict,
                  "qsd_node" : qsd_node_dict}

def _calculate_qhat_qsd_node(discharge, qhat, qsd):
    """Appends qhat and qsd reach values to the node level for each reach."""

    num_nodes = len(discharge.index)
    nodes = np.array(discharge.index)
    
    # qhat
    qhat_data = { "node" : nodes, "qhat" : np.repeat(qhat, num_nodes) }
    qhat_df = pd.DataFrame(data = qhat_data)
    qhat_df.set_index("node", inplace = True)

    # qsd
    qsd_data = { "node" : nodes, "qsd" : np.repeat(qsd, num_nodes) }
    qsd_df = pd.DataFrame(data = qsd_data)
    qsd_df.set_index("node", inplace = True)

    return qhat_df, qsd_df