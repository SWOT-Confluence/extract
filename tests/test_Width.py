# Standard library imports
import unittest
from unittest.mock import patch

# Third party imports
import numpy as np
import pandas as pd
from pandas._testing import assert_frame_equal

# Local imports
from app.attributes.Width import _create_node_dict

class TestWidth(unittest.TestCase):
    """Tests the methods in the Width class."""

    def test_create_node_dict(self):
        
        # Mock and create width data
        width = [
            [29.370833, 56.445833, 30.0, 30369],
            [29.362500, 56.445833, 30.0, 30370],
            [29.354167, 56.445833, 30.0, 30371],
            [29.345833, 56.445833, 30.0, 30372],
            [29.337500, 56.445833, 30.0, 30373]
        ]
        width_df = pd.DataFrame(width, columns=["x", "y", "width", "index"])
        width_df.insert(0, "node", range(5))
        width_df.set_index("node", inplace = True)
        
        width_dict = {}
        width_dict["008_1"] = width_df

        # Create expected data
        node = pd.DataFrame(np.full((5, 9362), 30.0), dtype=float)
        node.columns = np.arange(500, 9862)
        node.insert(0, "node", range(5))
        node.set_index("node", inplace = True)
        expected_dict = {}
        expected_dict["008_1"] = node

        # Execute function
        node_dict = _create_node_dict(width_dict)
        assert_frame_equal(expected_dict["008_1"], node_dict["008_1"])

if __name__ == '__main__':
    unittest.main()
