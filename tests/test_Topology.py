# Standard library imports
import unittest

# Local imports
from app.attributes.Topology import Topology

class TestTopology(unittest.TestCase):
    """Tests the methods in the Topology class."""

    def test_extract_topo_data(self):
        # Create topology object
        topo = Topology("tests/test_data/008_T.csv")

        # Assert value of object's attributes
        self.assertEqual(3520, topo.num_nodes)
        self.assertEqual(["topoid", "lon", "lat", "reachid", "dslink"], list(topo.topo_data.columns))
        self.assertEqual("node", topo.topo_data.index.name)

if __name__ == '__main__':
    unittest.main()
