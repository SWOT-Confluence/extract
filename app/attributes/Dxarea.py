# Standard imports
import warnings

class Dxarea:
    """Class that represents d_x_area data.

    Attributes
    ----------
        dxarea_node: dictionary
           d_x_area node-level data organized by reach with nx by nt (dataframe) values
        dxarea_reach: dictionary
           d_x_area reach-level data organized by reach with 1 by nt (series) values
        topology: Topology
            Topology object that represents topology data
        width: Width
            Width object that contains a dataframe of width data
        wse: Wse
            Wse object that contains a dataframe of wse data
    """

    def __init__(self, width, wse, topology):
        self.topology = topology
        self.width = width
        self.wse = wse
        self.dxarea_node = self._create_dxa_node_dict()
        self.dxarea_reach = self._create_dxa_reach_dict()

    def _create_dxa_node_dict(self):
        """Create a dictionary of d_x_area node values organized by reach."""

        # Extract wse and width values to calculate d_x_area and store in a dictionary
        dxa_dict = {}
        for key, value in self.width.width_node.items():
            wse = self.wse.wse_node[key]
            dxa_dict[key] = _calculate_dxa(wse, value)
        
        return dxa_dict

    def _create_dxa_reach_dict(self):
        """Create a dictionary of d_x_area reach values organized by reach."""

        reach_dict = {}
        for key, value in self.width.width_reach.items():
            wse = self.wse.wse_reach[key]
            reach_dict[key] = _calculate_dxa(wse, value)

        return reach_dict

def _calculate_dxa(wse, width):
        """Calculate dA data using width and wse attributes."""

        # Subtract median wse across time level from all wse values
        # Ignore RuntimeWarning: Mean of empty slice
        dH = None
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            dH = wse.subtract(wse.median(axis = 0, skipna = True))
        
        # Multiple width by change in wse
        return width.multiply(dH)