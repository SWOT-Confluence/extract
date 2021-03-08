# Standard library imports
import unittest
from unittest.mock import patch

# Third party imports
import numpy as np
import pandas as pd
from pandas._testing import assert_frame_equal

# Local imports
from app.attributes.Topology import Topology
from app.attributes.Wse import _extract_base_data

class TestWse(unittest.TestCase):
    """Tests the methods in the Wse class."""

    def test_extract_base_data(self):
        # Create sample of expected data
        wse = [
                ["30369", 29.3708, 56.4458, 171.7888],
                ["30370", 29.3625, 56.4458, 171.7888],
                ["30371", 29.3542, 56.4458, 167.9494],
                ["30372", 29.3458, 56.4458, 167.9494],
                ["30373", 29.3375, 56.4458, 167.9494]
            ]
        wse_df = pd.DataFrame(wse, columns=["nodeid", "x", "y", "elev"])
        wse_df.set_index("nodeid", inplace=True)
        
        # Execute function
        topology = Topology("tests/test_data/008_T.csv")
        base_data = _extract_base_data("tests/test_data/008.stage", topology)
        assert_frame_equal(wse_df, base_data.iloc[:5])

if __name__ == '__main__':
    unittest.main()
