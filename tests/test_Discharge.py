# Standard library imports
import unittest

# Third party imports
import numpy as np
import pandas as pd

# Local imports
from app.attributes.Discharge import _calculate_qhat_qsd

class TestDischarge(unittest.TestCase):
    """Tests the methods in the Discharge class."""

    def test__calculate_qhat_qsd(self):
        # Create example discharge data for a key of 1
        data_dict = {}
        data_dict["1"] = pd.DataFrame(np.reshape(np.arange(0, 25, dtype=float), (5, 5)))
        data_dict["1"][0][0] = np.nan
        data_dict["1"][3][1] = np.nan
        data_dict["1"][4][1] = np.nan
        data_dict["1"][2][2] = np.nan
        hat_sd_dict = _calculate_qhat_qsd(data_dict)
        
        # Assert hat and sd values
        self.assertAlmostEqual(12.90476190, hat_sd_dict["qhat_reach"]["1"])
        self.assertAlmostEqual(7.282756947, hat_sd_dict["qsd_reach"]["1"])

if __name__ == '__main__':
    unittest.main()
