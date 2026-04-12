import logging
import unittest
import xml_extractor as xe
from tests.fixtures import make_extractor, patch_iterparse
from tests.fixtures import MULTI_ROW_XML, SINGLE_ROW_XML, EMPTY_RESULTS_XML


class TestGetRowCount(unittest.TestCase):

    def setUp(self):
        xe.logger = logging.getLogger("test")
        self.extractor = make_extractor()

    def test_counts_rows(self):
        with patch_iterparse(MULTI_ROW_XML):
            self.assertEqual(self.extractor.get_row_count(), 3)

    def test_empty_xml_zero_rows(self):
        with patch_iterparse(EMPTY_RESULTS_XML):
            self.assertEqual(self.extractor.get_row_count(), 0)

    def test_single_row(self):
        with patch_iterparse(SINGLE_ROW_XML):
            self.assertEqual(self.extractor.get_row_count(), 1)
