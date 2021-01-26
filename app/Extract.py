# Standard imports
from os import scandir

# Local imports
from app.Input import Input
from app.Output import Output
from app.attributes.Discharge import Discharge
from app.attributes.Dxarea import Dxarea
from app.attributes.Slope import Slope
from app.attributes.Topology import Topology
from app.attributes.Width import Width
from app.attributes.Wse import Wse

class Extract:
    """A class that extracts SWOT and SWORD of Science data from files located 
    at data_directory attribute.

    Attributes
    ----------
        data_directory: Path
            Path to directory that contains basin files
        output_directory: Path
            Path to directory that will contain output files
    """

    def __init__(self, data_directory, output_directory):
        self.data_directory = data_directory
        self.output_directory = output_directory

    def extract_data(self):
        """Extracts data from input and outputs two NetCDF files per river reach.
        
        Reaches are determined from the Topology CSV files and one NetCDF file
        is outputed for SWOT attributes and the other is for SWORD of Science
        data.
        """

        with scandir(self.data_directory) as entries:
            for entry in entries:

                print("\nBASIN:", entry.name)

                # Obtain input files
                input = Input(entry)

                # Retrieve data from UK files
                data_dict = self._create_data_dict(input)

                # Write output
                output = Output(data_dict, self.output_directory)
                output.write_output()
    
    def _create_data_dict(self, input):
        """Create a dictionary of node and reach level data from input files."""

        # Topology
        print('Calculating topology...')
        topology = Topology(input.topology_file)

        # Discharge reach and node data (Qhat and Qsd)
        print('Calculating discharge...')
        discharge = Discharge(input.discharge_file, topology)

        # width reach and node data
        print('Calculating width...')
        width = Width(input.width_file, topology)

        # wse reach and node data
        print('Calculating wse...')
        wse = Wse(input.wse_file, topology)

        # slope2 reach and node data
        print('Calculating slope2...')
        slope = Slope(input.slope_file, topology, wse.wse_node)

        # d_x_area reach and node data
        print('Calculating d_x_area...')
        dxarea = Dxarea(width, wse, topology)

        return {
            "discharge" : discharge,
            "dxarea" : dxarea,
            "slope" : slope,
            "width" : width,
            "wse" : wse
        }
