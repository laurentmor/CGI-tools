import logging
import unittest
from unittest.mock import patch
import xml_extractor as xe
from tests.fixtures import make_extractor


class TestDeleteOutputDir(unittest.TestCase):

    def setUp(self):
        xe.logger = logging.getLogger("test")

    def test_removes_files_and_dir(self):
        ext = make_extractor(output_dir="out")
        walk_result = [
            ("out", ["sub"], ["f1.xml", "f2.xml"]),
            ("out/sub", [], ["f3.xml"]),
        ]
        with patch("os.walk", return_value=iter(walk_result)), \
             patch("os.remove") as mock_remove, \
             patch("os.rmdir") as mock_rmdir:
            ext.delete_output_dir()

        self.assertEqual(mock_remove.call_count, 3)
        self.assertGreaterEqual(mock_rmdir.call_count, 1)
