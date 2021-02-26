# Standard library imports
import unittest
from unittest.mock import patch

# Third party imports
import numpy as np
import pandas as pd
from pandas._testing import assert_frame_equal, assert_series_equal

# Local imports
from app.attributes.Dxarea import _calculate_dxa, Dxarea
from app.attributes.Topology import Topology
from app.attributes.Width import Width
from app.attributes.Wse import Wse

class TestDxarea(unittest.TestCase):
    """Tests the methods in the Dxarea class."""

    TOPOLOGY = Topology("tests/test_data/008_T.csv")

    def test_calculate_dxa_node(self):
        # Create width data
        width = pd.DataFrame(np.full((3, 5), 30.0), dtype=float)
        
        # Create wse data
        wse_list = [33.5, 30, 28.75, 25, 24.3, 23.8, 22, 20, 18.6, 17, 15.85, 13.12, 10, 8.6, 5.43]
        wse = pd.DataFrame(np.array(wse_list).reshape((3,5)), dtype=float)

        # Expected dxa
        expected_dxa = np.array([291, 240, 262.5, 192, 219, 0, 0, 0, 0, 0, -238.5, -266.4, -300, -300, -347.1]).reshape((3,5))
        expected_dxa = pd.DataFrame(expected_dxa)
        
        # Assert result of function
        actual_dxa = _calculate_dxa(wse, width)
        assert_frame_equal(expected_dxa, actual_dxa)

    def test_calculate_dxa_reach(self):
        # Create width data
        width = pd.Series(np.full((5), 30.0), dtype=float)
        
        # Create wse data
        wse = pd.Series(np.array([24.38333, 21.70666, 19.58333, 17.4, 15.57666]), dtype=float)

        # Expected dxa
        expected_dxa = pd.Series(np.array([144, 63.6999, 0, -65.4999, -120.2001]), dtype=float)

        # Assert result of function
        actual_dxa = _calculate_dxa(wse, width)
        assert_series_equal(expected_dxa, actual_dxa)

    @patch('app.attributes.Width', autospec=True)
    @patch('app.attributes.Wse', autospec=True)
    def test_create_dxa_node_dict(self, mock_wse, mock_width):
        # Create width data
        width_node_dict = {}
        width_node_dict["1"] = pd.DataFrame(np.full((3, 5), 30.0), dtype=float)
        mock_width.width_node = width_node_dict
        mock_width.width_reach = {}

        # Create wse data
        wse_list = [33.5, 30, 28.75, 25, 24.3, 23.8, 22, 20, 18.6, 17, 15.85, 13.12, 10, 8.6, 5.43]
        wse_dict = {}
        wse_dict["1"] = pd.DataFrame(np.array(wse_list).reshape((3,5)), dtype=float)
        mock_wse.wse_node = wse_dict
        mock_wse.wse_reach = {}

        # Assert results of node dictionary creation
        dxa = Dxarea(mock_width, mock_wse, self.TOPOLOGY)
        expected_node = np.array([291, 240, 262.5, 192, 219, 0, 0, 0, 0, 0, -238.5, -266.4, -300, -300, -347.1]).reshape((3,5))
        expected_dict = {}
        expected_dict["1"] = pd.DataFrame(expected_node)
        assert_frame_equal(expected_dict["1"], dxa.dxarea_node["1"])
    
    @patch('app.attributes.Width', autospec=True)
    @patch('app.attributes.Wse', autospec=True)
    def test_create_dxa_reach_dict(self, mock_wse, mock_width):
        # Create width data
        width_reach_dict = {}
        width_reach_dict["1"] = pd.Series(np.full((5), 30.0), dtype=float)
        mock_width.width_reach = width_reach_dict
        mock_width.width_node = {}

        # Create wse data
        wse_reach_dict = {}
        wse_reach_dict["1"] = pd.Series(np.array([24.38333, 21.70666, 19.58333, 17.4, 15.57666]), dtype=float)
        mock_wse.wse_reach = wse_reach_dict
        mock_wse.wse_node = {}

        # Assert results of reach dictionary creation
        dxa = Dxarea(mock_width, mock_wse, self.TOPOLOGY)
        expected_dict = {}
        expected_dict["1"] = pd.Series(np.array([144, 63.6999, 0, -65.4999, -120.2001]), dtype=float)
        assert_series_equal(expected_dict["1"], dxa.dxarea_reach["1"])

if __name__ == '__main__':
    unittest.main()
