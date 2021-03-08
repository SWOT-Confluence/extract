# Standard library imports
import unittest

# Third party imports
import numpy as np
import pandas as pd

# Local imports
from app.attributes.Topology import Topology
from app.attributes.Utilities import extract_node_data_shp, extract_node_data_txt, create_reach_dict, create_mean_series

class TestUtilities(unittest.TestCase):
    """Tests the methods in the Utilities file."""

    TOPOLOGY = Topology("tests/test_data/008_T.csv")
    DATA_DF = extract_node_data_txt("tests/test_data/008.discharge", 
            "Time;", TOPOLOGY)

    def test_extract_node_data_shp(self):
        # Run the method
        data_df = extract_node_data_shp("tests/test_data/008_S.shp", self.TOPOLOGY)

        # Assert the column names
        self.assertEqual("x", data_df.columns[0])
        self.assertEqual("y", data_df.columns[1])
        self.assertEqual("slope", data_df.columns[2])
        self.assertEqual("index", data_df.columns[3])

        # Assert index name and number of nodes
        self.assertEqual("nodeid", data_df.index.name)
        self.assertEqual(3520, len(data_df.index))
        
        # Assert shape
        self.assertEqual(3520, data_df.shape[0])    # rows
        self.assertEqual(4, data_df.shape[1])    # columns

    def test_extract_node_data_txt(self):
        # Assert shape
        self.assertEqual(3520, self.DATA_DF.shape[0])    # rows
        self.assertEqual(9863, self.DATA_DF.shape[1])    # columns

        # Assert index name and number of nodes
        self.assertEqual("nodeid", self.DATA_DF.index.name)
        self.assertEqual(3520, len(self.DATA_DF.index))

    def test_create_reach_dict(self):
        # Run the method
        df_dict = create_reach_dict(self.DATA_DF, self.TOPOLOGY, "008")

        # Assert the number of keys and values
        self.assertEqual(62, len(df_dict.keys()))
        self.assertEqual(62, len(df_dict.values()))

        # Assert the shape of key 2483
        self.assertEqual((43, 9862), df_dict["008_2483"].shape)

    def test_create_mean_series(self):
        # Create a dictionary with a dataframe value
        data_dict = {}
        data_dict["1"] = pd.DataFrame(np.reshape(np.arange(0, 50, dtype=float), (5, 10)))
        data_dict = create_mean_series(data_dict)
        
        # Assert result
        mean_series = pd.Series([20, 21, 22, 23, 24, 25, 26, 27, 28, 29], dtype=float)
        self.assertTrue(data_dict["1"].equals(mean_series))

if __name__ == '__main__':
    unittest.main()
