# Standard library imports
import unittest
from unittest.mock import patch

# Third party imports
import numpy as np
import pandas as pd
from pandas._testing import assert_frame_equal

# Local imports
from app.attributes.Wse import _extract_base_data

class TestWse(unittest.TestCase):
    """Tests the methods in the Wse class."""

    def test_extract_base_data(self):
        # Create sample of expected data
        wse = [
                [1, 29.3708, 56.4458, 171.7888],
                [2, 29.3625, 56.4458, 171.7888],
                [3, 29.3542, 56.4458, 167.9494],
                [4, 29.3458, 56.4458, 167.9494],
                [5, 29.3375, 56.4458, 167.9494]
            ]
        wse_df = pd.DataFrame(wse, columns=["node", "x", "y", "elev"])
        wse_df.set_index("node", inplace=True)
        
        # Execute function
        base_data = _extract_base_data("tests/test_data/008.stage", 3520)
        assert_frame_equal(wse_df, base_data.iloc[:5])

if __name__ == '__main__':
    unittest.main()
