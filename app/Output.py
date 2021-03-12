# Third party imports
from netCDF4 import Dataset
import numpy as np

class Output:
    """Class that represents output data to be written to NetCDF.

    Output consists of two NETCDFs per river reach; one for SWOT data and
    one for SoS of Science data.

    Attributes
    ----------
        data: dictionary
            dictionary of UK data organized by reach as dataframe values
        output_directory: Path
            Path to the directory where NetCDFs will be written
        swot_dataset: Dataset
            netCDF4.Dataset object that represents SWOT NetCDF to be written
        swot_reach: Group
            netCDF4.Group object for reach level data
        swot_node: Group
            netCDF4.Group object for node level data
        sos_dataset: Dataset
            netCDF4.Dataset object that represents SoS NetCDF to be written
        sos_reach: Group
            netCDF4.Group object for reach level data
        sos_node: Group
            netCDF4.Group object for node level data
    """

    TIME_STEPS = 9862
    FILL_VALUE = -9999

    def __init__(self, data, output_directory, logger):
        self.logger = logger
        self.data = data
        self.output_directory = output_directory
        
        self.swot_dataset = None
        self.swot_reach = None
        self.swot_node = None
        
        self.sos_dataset = None
        self.sos_reach = None
        self.sos_node = None

    def write_output(self):
        """Writes output to two NetCDF files for SWOT and SoS of Science data
        on the reach and node level."""

        for key, value in self.data["topology"].items():
            self.logger.info(f"WRITING REACH: {key}")
            number_nodes = value.shape[0]
            self._define_datasets(str(key))
            self._create_dim_coords(number_nodes)
            self._create_groups()
            self._create_swot_reach_vars(key)
            self._create_swot_node_vars(key)
            self._create_sos_reach_vars(key)
            self.swot_dataset.close()
            self.sos_dataset.close()

            # Clear dataset and groups
            self.swot_dataset = None
            self.swot_reach = None
            self.swot_node = None
            self.sos_dataset = None
            self.sos_reach = None
            self.sos_node = None

    def _define_datasets(self, reach_id):
        """Defines datasets for writing SWOT and SoS data."""

        # SWOT
        swot_file = self.output_directory / (reach_id + "_SWOT.nc")
        self.swot_dataset = Dataset(swot_file, "w", format="NETCDF4")
        self.swot_dataset.title = f"SWOT data for reach ID: {reach_id}"

        # SoS
        sos_file = self.output_directory / (reach_id + "_SOS.nc")
        self.sos_dataset = Dataset(sos_file, "w", format="NETCDF4")
        self.sos_dataset.title = f"SoS of Science data for reach ID: {reach_id}"

    def _create_dim_coords(self, number_nodes):
        """Create dimensions and coordinate variables for each dimension."""

        # SWOT
        self.swot_dataset.createDimension("nt", self.TIME_STEPS)
        self.swot_dataset.createDimension("nx", number_nodes)
        create_coord_var(self.swot_dataset, number_nodes)

    def _create_groups(self):
        """Create SWOT reach and node groups and SoS reach and node groups."""

        # SWOT
        self.swot_reach = self.swot_dataset.createGroup("reach")
        self.swot_node = self.swot_dataset.createGroup("node")

        # SoS
        self.sos_reach = self.sos_dataset.createGroup("reach")
        self.sos_node = self.sos_dataset.createGroup("node")

    def _create_swot_reach_vars(self, key):
        """Create SWOT reach-level variables."""

        # d_x_area
        dxa_v = self.swot_reach.createVariable("d_x_area", "f8", ("nt"), fill_value = self.FILL_VALUE)
        dxa_v.long_name = "change in cross-sectional area"
        dxa_v.units = "m^2"
        dxa_v.valid_min = -10000000
        dxa_v.valid_max = 10000000
        self.data["dxarea"].dxarea_reach[key].fillna(value = self.FILL_VALUE, inplace = True)
        dxa_v[:] = self.data["dxarea"].dxarea_reach[key].to_numpy()
        
        # slope2
        slope2_v = self.swot_reach.createVariable("slope2", "f8", ("nt"), fill_value = self.FILL_VALUE)
        slope2_v.long_name = "enhanced water surface slope with respect to geoid"
        slope2_v.units = "m/m"
        slope2_v.valid_min = -0.001
        slope2_v.valid_max = 0.1
        self.data["slope"].slope_reach[key].fillna(value = self.FILL_VALUE, inplace = True)
        slope2_v[:] = self.data["slope"].slope_reach[key].to_numpy()

        # width
        width_v = self.swot_reach.createVariable("width", "f8", ("nt"), fill_value = self.FILL_VALUE)
        width_v.long_name = "reach width"
        width_v.units = "m"
        width_v.valid_min = 0.0
        width_v.valid_max = 100000
        self.data["width"].width_reach[key].fillna(value = self.FILL_VALUE, inplace = True)
        width_v[:] = self.data["width"].width_reach[key].to_numpy()

        # wse
        wse_v = self.swot_reach.createVariable("wse", "f8", ("nt"), fill_value = self.FILL_VALUE)
        wse_v.long_name = "water surface elevation with respect to the geoid"
        wse_v.units = "m"
        wse_v.valid_min = -1000
        wse_v.valid_max = 100000
        self.data["wse"].wse_reach[key].fillna(value = self.FILL_VALUE, inplace = True)
        wse_v[:] = self.data["wse"].wse_reach[key].to_numpy()

    def _create_sos_reach_vars(self, key):
        """Create SoS reach-level variables."""

        # Qhat
        qhat_v = self.sos_reach.createVariable("Qhat", "f8", fill_value = self.FILL_VALUE)
        qhat_v.long_name = "Mean_Q"
        qhat_v.units = "m^3/s"
        qhat = self.FILL_VALUE if np.isnan(self.data["discharge"].qhat_reach[key]) else self.data["discharge"].qhat_reach[key]
        qhat_v.assignValue(qhat)

        # Qsd
        qsd_v = self.sos_reach.createVariable("Qsd", "f8", fill_value = self.FILL_VALUE)
        qsd_v.long_name = "sd_Q"
        qsd_v.units = "m^3/s"
        qsd = self.FILL_VALUE if np.isnan(self.data["discharge"].qsd_reach[key]) else self.data["discharge"].qsd_reach[key]
        qsd_v.assignValue(qsd)

    def _create_swot_node_vars(self, key):
        """Create SWOT node-level variables."""

        # d_x_area
        dxa_v = self.swot_node.createVariable("d_x_area", "f8", ("nx", "nt"), fill_value = self.FILL_VALUE)
        dxa_v.long_name = "change in cross-sectional area"
        dxa_v.units = "m^2"
        dxa_v.valid_min = -10000000
        dxa_v.valid_max = 10000000
        self.data["dxarea"].dxarea_node[key].fillna(value = self.FILL_VALUE, inplace = True)
        dxa_v[:] = self.data["dxarea"].dxarea_node[key].to_numpy()
        
        # slope2
        slope2_v = self.swot_node.createVariable("slope2", "f8", 
            ("nx", "nt"), fill_value = self.FILL_VALUE)
        slope2_v.long_name = "enhanced water surface slope with respect to geoid"
        slope2_v.units = "m/m"
        slope2_v.valid_min = -0.001
        slope2_v.valid_max = 0.1
        self.data["slope"].slope_node[key].fillna(value = self.FILL_VALUE, inplace = True)
        slope2_v[:] = self.data["slope"].slope_node[key].to_numpy()

        # width
        width_v = self.swot_node.createVariable("width", "f8", ("nx", "nt",), fill_value = self.FILL_VALUE)
        width_v.long_name = "node width"
        width_v.units = "m"
        width_v.valid_min = 0.0
        width_v.valid_max = 100000
        self.data["width"].width_node[key].fillna(value = self.FILL_VALUE, inplace = True)
        width_v[:] = self.data["width"].width_node[key].to_numpy()

        # wse
        wse_v = self.swot_node.createVariable("wse", "f8", ("nx", "nt",), fill_value = self.FILL_VALUE)
        wse_v.long_name = "water surface elevation with respect to the geoid"
        wse_v.units = "m"
        wse_v.valid_min = -1000
        wse_v.valid_max = 100000
        self.data["wse"].wse_node[key].fillna(value = self.FILL_VALUE, inplace = True)
        wse_v[:] = self.data["wse"].wse_node[key].to_numpy()

def create_coord_var(dataset, number_nodes):
    """Create coordinate variables for each dimension in the parameter dataset."""

    # time step coordinate variable
    nt = dataset.createVariable("nt", "i4", ("nt",))
    nt.units = "day"
    nt.long_name = "nt"
    nt[:] = range(0, Output.TIME_STEPS)

    # node coordinate variable
    nx = dataset.createVariable("nx", "i4", ("nx",))
    nx.units = "node"
    nx.long_name = "nx"
    nx[:] = range(1, number_nodes + 1)