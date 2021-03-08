# Third party imports
import pandas as pd

class Topology:
    """Class that represesnts a topology CSV file.

    Attributes
    ----------
        file: Path
            Path to topology CSV file
        num_nodes: int
            Number of nodes present in topology file
        topo_data: dictionary
            Topology data organized by reach as a dataframe value
    """

    def __init__(self, file):
        """Initializes a Topology object using the basin number parameter."""
        
        self.file = file
        topo_df = pd.read_csv(self.file)
        self.num_nodes = len(topo_df.index)
        self.topo_data = self._extract_topo_data(topo_df)

    def _extract_topo_data(self, topo_df):
        """Retrieve data from CSV file found at Path attribute."""

        # Add an explicit node index to match other data
        topo_df = topo_df.rename(columns = {"index" : "nodeid", "link" : "reachid"})
        
        # Convert reachid and topoid to str values
        convert_dict = { "reachid" : str, "nodeid" : str }
        topo_df = topo_df.astype(convert_dict)
        
        # Set node as index
        topo_df.set_index("nodeid", inplace = True)
        
        return topo_df