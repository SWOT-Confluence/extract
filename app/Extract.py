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
        input_dir_list: list
            list of Path objects to directories that contain basin files
        logger: Logger
            Logger object to log messages to a file
        output_directory: Path
            Path to directory that will contain output files
    """

    def __init__(self, input_dir_list, output_directory, logger):
        self.input_dir_list = input_dir_list
        self.output_directory = output_directory
        self.logger = logger

    def extract_data(self):
        """Extracts data from input and outputs two NetCDF files per river reach.
        
        Reaches are determined from the Topology CSV files and one NetCDF file
        is outputed for SWOT attributes and the other is for SWORD of Science
        data.
        """

        for entry in self.input_dir_list:

                self.logger.info(f"Processing basin: {entry.name}")

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
        self.logger.info('Calculating topology...')
        topology = Topology(input.topology_file)

        # Discharge reach and node data (Qhat and Qsd)
        self.logger.info('Calculating discharge...')
        discharge = Discharge(input.discharge_file, topology, input.basin_num, input.invalid_nodes)

        # width reach and node data
        self.logger.info('Calculating width...')
        width = Width(input.width_file, topology, input.basin_num, input.invalid_nodes)

        # wse reach and node data
        self.logger.info('Calculating wse...')
        wse = Wse(input.wse_file, topology, input.basin_num, input.invalid_nodes)

        # slope2 reach and node data
        self.logger.info('Calculating slope2...')
        slope = Slope(topology, wse.wse_node, input.basin_num, input.invalid_nodes)

        # d_x_area reach and node data
        self.logger.info('Calculating d_x_area...')
        dxarea = Dxarea(width, wse, topology)

        return {
            "discharge" : discharge,
            "dxarea" : dxarea,
            "slope" : slope,
            "width" : width,
            "wse" : wse
        }
