# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

"""Unit tests for normalize_xml_encoding_declaration().
These tests ensure malformed 'UTF8'-style encoding declarations are
rewritten to the canonical 'UTF-8' spelling that expat recognizes."""

import unittest

import xml_extractor as xe


class TestNormalizeXmlEncodingDeclaration(unittest.TestCase):
    """Verify the XML encoding declaration is normalized correctly."""

    def test_empty_string_passthrough(self):
        """Verify that empty string passthrough."""
        self.assertEqual(xe.normalize_xml_encoding_declaration(""), "")

    def test_none_passthrough(self):
        """Verify that None passthrough."""
        self.assertIsNone(xe.normalize_xml_encoding_declaration(None))

    def test_line_without_encoding_unchanged(self):
        """Verify that a line without an encoding declaration is unchanged."""
        line = "<RESULTS>\n"
        self.assertEqual(xe.normalize_xml_encoding_declaration(line), line)

    def test_utf8_single_quotes_fixed(self):
        """Verify that UTF8 with single quotes is rewritten to UTF-8."""
        line = "<?xml version='1.0'  encoding='UTF8' ?>\r\n"
        expected = "<?xml version='1.0'  encoding='UTF-8' ?>\r\n"
        self.assertEqual(xe.normalize_xml_encoding_declaration(line), expected)

    def test_utf8_double_quotes_fixed(self):
        """Verify that UTF8 with double quotes is rewritten to UTF-8."""
        line = '<?xml version="1.0" encoding="UTF8"?>\n'
        expected = '<?xml version="1.0" encoding="UTF-8"?>\n'
        self.assertEqual(xe.normalize_xml_encoding_declaration(line), expected)

    def test_lowercase_utf8_fixed(self):
        """Verify that a lowercase 'utf8' is rewritten to UTF-8."""
        line = '<?xml version="1.0" encoding="utf8"?>\n'
        expected = '<?xml version="1.0" encoding="UTF-8"?>\n'
        self.assertEqual(xe.normalize_xml_encoding_declaration(line), expected)

    def test_already_correct_unchanged(self):
        """Verify that an already-correct 'UTF-8' declaration is left untouched."""
        line = "<?xml version='1.0' encoding='UTF-8' ?>\r\n"
        self.assertEqual(xe.normalize_xml_encoding_declaration(line), line)

    def test_non_utf8_encoding_unchanged(self):
        """Verify that unrelated encodings (e.g. ISO-8859-1) are left untouched."""
        line = "<?xml version='1.0' encoding='ISO-8859-1' ?>\r\n"
        self.assertEqual(xe.normalize_xml_encoding_declaration(line), line)


if __name__ == "__main__":
    unittest.main()
