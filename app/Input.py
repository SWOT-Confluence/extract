# Standard imports
from pathlib import Path

class Input:
    """A class that represents input data files to be processed.
    
    Attributes
    ----------
        input_directory: Path
            Path to directory that contains input data
        discharge_file: Path
            Path to discharge file
        slope_file: Path
            Path to slope file
        topology_file: Path
            Path to topology file
        width_file: Path
            Path to width file
        wse_file: Path
            Path to stage file
    """

    def __init__(self, input_directory):
            self.input_directory = Path(input_directory.path)
            basin_num = input_directory.name
            self.discharge_file = self.input_directory / (basin_num + ".discharge")
            self.slope_file = self.input_directory / (basin_num + "_S.shp")
            self.topology_file = self.input_directory / (basin_num + "_T.csv")
            self.width_file = self.input_directory / (basin_num + "_W.shp")
            self.wse_file = self.input_directory / (basin_num + ".stage")