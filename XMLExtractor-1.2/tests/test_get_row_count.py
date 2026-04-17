# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

"""Unit tests for get_row_count().
They verify that row counting works correctly for empty XML, a single row, and multiple rows."""
import logging
import unittest
import xml_extractor as xe
from tests.fixtures import make_extractor, patch_iterparse
from tests.fixtures import MULTI_ROW_XML, SINGLE_ROW_XML, EMPTY_RESULTS_XML


class TestGetRowCount(unittest.TestCase):

    """Test get_row_count() using empty, single-row, and multi-row XML inputs to verify row counting behavior."""
    def setUp(self):
        xe.logger = logging.getLogger("test")
        self.extractor = None

    def test_counts_rows(self):
        """Verify that Counts rows."""
        self.extractor = make_extractor(input_file=MULTI_ROW_XML)
        self.assertEqual(self.extractor.get_row_count(), 3)

    def test_empty_xml_zero_rows(self):
        """Verify that Empty xml zero rows."""
        self.extractor = make_extractor(input_file=EMPTY_RESULTS_XML)
        self.assertEqual(self.extractor.get_row_count(), 0)

    def test_single_row(self):
        """Verify that Single row."""
        self.extractor = make_extractor(input_file=SINGLE_ROW_XML)
        self.assertEqual(self.extractor.get_row_count(), 1) 