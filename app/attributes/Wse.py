# Third party imports
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
            wse reach-level data organized by reach with nx by 1 (series) values
        topology: Topology
            Topology object that represents data found in file
    """

    def __init__(self, file, topology):
        self.file = file
        self.topology = topology
        
        # Create node level wse data by adding stage data together
        base_data = self._extract_base_data()
        node_data = extract_node_data_txt(self.file, "Time;", self.topology)
        df = node_data.add(base_data["elev"], axis = "index")
        
        # Create node-level and reach-level dataframes for each reach
        self.wse_node = create_reach_dict(df, self.topology)
        self.wse_reach = create_mean_series(self.wse_node)

    def _extract_base_data(self):
        """Extracts base elevation matrix from file attribute."""
        
        header_end = get_line_num(self.file, "Stage information") + 1
        base_data = pd.read_csv(self.file, 
            skiprows = range(0, header_end), 
            nrows = self.topology.num_nodes,
            header = None, 
            delim_whitespace = True)
        base_data.columns = ["node", "x", "y", "elev"]
        base_data.set_index("node", inplace = True)
        return base_data