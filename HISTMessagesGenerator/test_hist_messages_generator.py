import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
import tempfile
import os
import logging

from HISTMessagesGenerator import HISTMessagesGenerator


class TestHISTMessagesGenerator(unittest.TestCase):
    # ==========================================================
    # Setup test instance and logger
    # ==========================================================
    def setUp(self):
        # Patch FileHandler to prevent actual filesystem writes
        patcher = patch("logging.FileHandler")
        self.addCleanup(patcher.stop)
        patcher.start()

        # Create HISTMessagesGenerator instance for testing
        self.generator = HISTMessagesGenerator(
            log_file="test.log",
            input_file="dummy.xml",
            customer="TESTCUST",
            bank="TESTBANK",
            enable_file_logging=False
        )

        # Configure logger for tests
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
        self.logger = logging.getLogger("TEST_LOGGER")

    # ==========================================================
    # Helper method: build XML in memory
    # ==========================================================
    def build_xml(self, rows):
        """
        Create an in-memory XML tree from a list of dictionaries.

        Args:
            rows (list of dict): Each dict represents a row, e.g.
            [{"INSTRUMENT_ID": "1", "TYPE_": "ABC", "CUSTOMER_PARTY_TYPE": "P1"}, ...]

        Returns:
            xml.etree.ElementTree.Element: Root XML element
        """
        root = ET.Element("ROWS")
        for row_data in rows:
            row = ET.SubElement(root, "ROW")
            for key, value in row_data.items():
                col = ET.SubElement(row, "COLUMN", NAME=key)
                col.text = value
        return root

    # ==========================================================
    # Tests for build_instruments_dictionary
    # ==========================================================
    @patch("HISTMessagesGenerator.resolve_class")
    def test_build_dictionary_unique(self, mock_resolve):
        """Should build dictionary with unique instruments only."""
        self.logger.info("TEST: test_build_dictionary_unique - Should build dictionary with unique instruments only")
        mock_resolve.side_effect = lambda x: x  # identity function

        xml = self.build_xml([
            {"INSTRUMENT_ID": f"I{i}", "TYPE_": "A", "CUSTOMER_PARTY_TYPE": f"P{i}"}
                for i in range(1, 4500001)

        ])

        result = self.generator.build_instruments_dictionary(xml)

        self.assertEqual(len(result), 4500000)
        self.assertIn("I1", result)
        self.assertIn("I2", result)

    @patch("HISTMessagesGenerator.resolve_class")
    def test_duplicate_instrument_keeps_first(self, mock_resolve):
        """Duplicate instrument IDs should keep the first occurrence only."""
        self.logger.info("TEST: test_duplicate_instrument_keeps_first - Duplicate instrument IDs keep first occurrence")
        mock_resolve.side_effect = lambda x: x

        xml = self.build_xml([
            {"INSTRUMENT_ID": "1", "TYPE_": "A", "CUSTOMER_PARTY_TYPE": "P1"},
            {"INSTRUMENT_ID": "1", "TYPE_": "A", "CUSTOMER_PARTY_TYPE": "P2"},
        ])

        result = self.generator.build_instruments_dictionary(xml)

        self.assertEqual(len(result), 1)
        self.assertEqual(result["1"][1], "P1")  # first party_type kept

    @patch("HISTMessagesGenerator.resolve_class")
    def test_ignore_null_instrument(self, mock_resolve):
        """Rows without INSTRUMENT_ID should be ignored."""
        self.logger.info("TEST: test_ignore_null_instrument - Rows without INSTRUMENT_ID ignored")
        mock_resolve.side_effect = lambda x: x

        xml = self.build_xml([
            {"TYPE_": "A", "CUSTOMER_PARTY_TYPE": "P1"}
        ])

        result = self.generator.build_instruments_dictionary(xml)

        self.assertEqual(len(result), 0)

    # ==========================================================
    # Tests for validate_columns_exist
    # ==========================================================
    def test_validate_columns_success(self):
        """Should not raise an error if all required columns exist."""
        self.logger.info("TEST: test_validate_columns_success - All required columns exist")

        xml_content = """<?xml version="1.0"?>
<ROWS>
    <ROW>
        <COLUMN NAME="INSTRUMENT_ID">1</COLUMN>
        <COLUMN NAME="TYPE_">A</COLUMN>
        <COLUMN NAME="CUSTOMER_PARTY_TYPE">P1</COLUMN>
    </ROW>
</ROWS>"""

        # Create a temporary XML file
        tmp_file = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".xml", encoding="utf-8")
        tmp_file.write(xml_content)
        tmp_file.close()

        try:
            # Open file explicitly in read mode to avoid Windows lock issue
            with open(tmp_file.name, 'r', encoding='utf-8') as f:
                self.generator.validate_columns_exist(f.name, ["INSTRUMENT_ID", "TYPE_", "CUSTOMER_PARTY_TYPE"])
        finally:
            os.remove(tmp_file.name)

    def test_validate_columns_missing(self):
        """Should raise ValueError if any required column is missing."""
        self.logger.info("TEST: test_validate_columns_missing - Missing required columns should raise ValueError")

        xml_content = """<?xml version="1.0"?>
<ROWS>
    <ROW>
        <COLUMN NAME="INSTRUMENT_ID">1</COLUMN>
    </ROW>
</ROWS>"""

        tmp_file = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".xml", encoding="utf-8")
        tmp_file.write(xml_content)
        tmp_file.close()

        try:
            # Open file explicitly in read mode to avoid Windows lock
            with open(tmp_file.name, 'r', encoding='utf-8') as f:
                with self.assertRaises(ValueError):
                    self.generator.validate_columns_exist(f.name, ["INSTRUMENT_ID", "TYPE_", "CUSTOMER_PARTY_TYPE"])
        finally:
            os.remove(tmp_file.name)


if __name__ == "__main__":
    unittest.main()
