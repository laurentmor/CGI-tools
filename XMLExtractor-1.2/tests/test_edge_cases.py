# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

"""Regression tests for edge-case behavior across XML cleaning, ZIP password validation, and XMLExtractor settings.
They ensure the extractor handles unusual input without crashing."""

import logging
import unittest
from unittest.mock import MagicMock, patch

import xml_extractor as xe
from tests.fixtures import make_extractor, patch_iterparse


class TestEdgeCases(unittest.TestCase):
    """Validate edge-case behavior for XML cleaning, zip password validation, and extractor configuration values."""

    def setUp(self):
        xe.logger = logging.getLogger("test")

    def test_get_message_id_with_whitespace(self):
        """Verify that Get message id with whitespace."""
        ext = make_extractor()
        content = "<Root>  <MessageID>  MSG  </MessageID>  </Root>"
        self.assertIn("MSG", ext.get_message_id(content))

    def test_clean_xml_unicode_passthrough(self):
        """Verify that Clean xml unicode passthrough."""
        result = xe.clean_xml_content("Héllo Wörld", {})
        self.assertEqual(result, "Héllo Wörld")

    def test_validate_zip_password_unicode(self):
        """Verify that Validate zip password unicode."""
        self.assertTrue(xe.validate_zip_password("pässwörd123"))

    def test_extractor_column_name_stored(self):
        """Verify that Extractor column name stored."""
        self.assertEqual(make_extractor(column_name="MY_COL").column_name, "MY_COL")

    def test_row_with_no_message_id_skipped(self):
        """Verify that Row with no message id skipped."""
        xml = """\
<RESULTS>
  <ROW>
    <COLUMN NAME="RICH_TEXT_NCLOB"><![CDATA[<Root><NO_ID/></Root>]]></COLUMN>
  </ROW>
</RESULTS>"""
        ext = make_extractor()
        written = {}

        def fake_open(path, mode="r", **kw):
            handle = MagicMock()
            handle.__enter__ = lambda s: s
            handle.__exit__ = MagicMock(return_value=False)
            handle.write = lambda data: written.update({path: data})
            return handle

        with (
            patch_iterparse(xml),
            patch("builtins.open", side_effect=fake_open),
            patch.object(ext, "check_output_dir"),
            patch.object(ext, "create_zip_archive"),
        ):
            ext.extract_and_save_elements()

        self.assertEqual(len(written), 0)
