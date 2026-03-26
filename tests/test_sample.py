import unittest
import os
import sys

# Ensure the root directory is on the path so utils can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.logger import get_logger

class TestEnvironmentSetup(unittest.TestCase):
    def setUp(self):
        self.logger = get_logger("TestLogger")

    def test_logger_initialization(self):
        """Test if the logger initializes properly."""
        self.assertIsNotNone(self.logger)
        self.assertEqual(self.logger.name, "TestLogger")
        self.logger.info("Test logger initialized successfully.")

    def test_sample_assertion(self):
        """A simple sanity check test."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
