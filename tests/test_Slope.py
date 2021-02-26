# Standard library imports
import unittest
from unittest import mock
from unittest.mock import patch

# Third party imports
import numpy as np
import pandas as pd
from pandas._testing import assert_frame_equal

# Local imports
from app.attributes.Slope import Slope, _calculate_distance, \
    _create_node_distance_list, _apply_linear_regression, _calculate_reach
from app.attributes.Topology import Topology

class TestSlope(unittest.TestCase):
    """Tests the methods in the Dxarea class."""

    COORD_DATA = [[30369, 29.37, 56.446, "1", "2"], [30370, 29.36, 56.446, "1", "2"], 
            [30371, 29.35, 56.446, "1", "2"], [30372, 29.34, 56.446, "1", "2"],
            [30373, 29.33, 56.446, "1", "2"]]
    COORD_DATA = pd.DataFrame(COORD_DATA, columns=["index", "lon", "lat", "link", "dslink"])
    COORD_DATA.insert(0, "node", range(1, 6))
    COORD_DATA.set_index("node", inplace=True)

    WSE_DATA = [33.5, 30, 28.75, 25, 24.3, 23.8, 22, 20, 18.6, 17, 15.85, 13.12, 
        10, 8.6, 5.43, 4.40, 4.15, 3.33, 3.05, 2.75, 2.35, 1.95, 1.50, 1.25, 1.05]
    WSE_DATA = pd.DataFrame(np.array(WSE_DATA).reshape((5,5)), dtype=float)


    def test_calculate_distance(self):        
        # Retrieve row and start node data
        start_data = self.COORD_DATA.iloc[0]
        row_data = self.COORD_DATA.iloc[1]

        # Run function and assert result
        distance = _calculate_distance(row_data, start_data)
        self.assertAlmostEqual(616.7233638731635, distance)

    def test_create_node_distance_list(self):
        
        distance_df = _create_node_distance_list(self.COORD_DATA)

        # Assert distances
        self.assertAlmostEqual(0.0, distance_df.iloc[0])
        self.assertAlmostEqual(616.7233638731635, distance_df.iloc[1])
        self.assertAlmostEqual(1233.4467244843192, distance_df.iloc[2])
        self.assertAlmostEqual(1850.1700785721137, distance_df.iloc[3])
        self.assertAlmostEqual(2466.8934228745406, distance_df.iloc[4])

    def test_apply_linear_regression(self):

        distance_list = pd.Series([0.0, 616.72336, 1233.44672, 1850.170079, 2466.893423], index=[1, 2, 3, 4, 5])
        slope = _apply_linear_regression(self.WSE_DATA.iloc[:, 0], distance_list)
        
        # Assert slope result
        self.assertAlmostEqual(0.01325, slope, places=5)

    def test_calculate_reach(self):
        
        # Data needed to create slope object
        topo_data = self.COORD_DATA.rename(columns = {"index" : "topoid", "link" : "reachid"})
        convert_dict = { "reachid" : str, "topoid" : str }
        topo_data = topo_data.astype(convert_dict)
        topo_dict = {}
        topo_dict["008_1"] = topo_data

        # Create slope object and run method
        slope_list = _calculate_reach(("008_1", self.WSE_DATA), topo_dict)
        
        # Assert values of returned slope list
        key = slope_list[0]
        slope_series = slope_list[1]
        self.assertEqual("008_1", key)
        self.assertAlmostEqual(0.01325, slope_series.loc[0], places=5)
        self.assertAlmostEqual(0.01199, slope_series.loc[1], places=5)
        self.assertAlmostEqual(0.01154, slope_series.loc[2], places=5)
        self.assertAlmostEqual(0.01022, slope_series.loc[3], places=5)
        self.assertAlmostEqual(0.00985, slope_series.loc[4], places=5)
    
    @mock.patch.dict("app.config.extract_config", {"no_cores": 5, "input_dir": "", 
        "output_dir": "", "logging_dir": ""})
    @patch('app.attributes.Topology', autospec=True)
    @patch.object(Slope, '_create_node_dict')
    def test_create_reach_dict(self, mock_node, mock_topo):
        
        # Data needed to create slope object
        topo_data = self.COORD_DATA.rename(columns = {"index" : "topoid", "link" : "reachid"})
        convert_dict = { "reachid" : str, "topoid" : str }
        topo_data = topo_data.astype(convert_dict)
        mock_topo.topo_data = topo_data

        wse_node = {}
        wse_node["008_1"] = self.WSE_DATA

        # Create slope object; assert reach values
        slope = Slope(mock_topo, wse_node, "008")
        slope_series = slope.slope_reach["008_1"]
        self.assertAlmostEqual(0.01325, slope_series.loc[0], places=5)
        self.assertAlmostEqual(0.01199, slope_series.loc[1], places=5)
        self.assertAlmostEqual(0.01154, slope_series.loc[2], places=5)
        self.assertAlmostEqual(0.01022, slope_series.loc[3], places=5)
        self.assertAlmostEqual(0.00985, slope_series.loc[4], places=5)

    @mock.patch.dict("app.config.extract_config", {"no_cores": 5, "input_dir": "", 
        "output_dir": "", "logging_dir": ""})
    @patch('app.attributes.Topology', autospec=True)
    @patch.object(Slope, 'TIME_STEPS')
    def test_create_node_dict(self, mock_time, mock_topo):
        
        # Data needed to create slope object
        mock_time = 5

        topo_data = self.COORD_DATA.rename(columns = {"index" : "topoid", "link" : "reachid"})
        convert_dict = { "reachid" : str, "topoid" : str }
        topo_data = topo_data.astype(convert_dict)
        mock_topo.topo_data = topo_data

        wse_node = {}
        wse_node["008_1"] = self.WSE_DATA

        # Expected node dictionary
        expected_dict = {}
        expected_value = [
                        [0.01325, 0.01199, 0.01154, 0.01022, 0.00985],
                        [0.01325, 0.01199, 0.01154, 0.01022, 0.00985],
                        [0.01325, 0.01199, 0.01154, 0.01022, 0.00985],
                        [0.01325, 0.01199, 0.01154, 0.01022, 0.00985],
                        [0.01325, 0.01199, 0.01154, 0.01022, 0.00985],
                        ]
        expected_dict["008_1"] = pd.DataFrame(expected_value)
        expected_dict["008_1"].insert(0, "node", np.array(wse_node["008_1"].index))
        expected_dict["008_1"].set_index("node", inplace = True)

        # Create slope object; assert node values
        slope = Slope(mock_topo, wse_node, "008")
        assert_frame_equal(expected_dict["008_1"], slope.slope_node["008_1"], rtol=0.05)

if __name__ == '__main__':
    unittest.main()
