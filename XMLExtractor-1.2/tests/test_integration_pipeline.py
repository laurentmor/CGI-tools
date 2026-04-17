# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

"""Unit tests covering the full extraction pipeline end-to-end.
These tests simulate export.xml parsing, file creation, and optional ZIP generation entirely in memory."""
import logging
import os
import unittest
from unittest.mock import MagicMock, patch
import xml_extractor as xe
from tests.fixtures import make_extractor, patch_iterparse


class TestIntegrationPipeline(unittest.TestCase):
    """
    Simulates the real export.xml sample through the full extraction pipeline.
    All I/O is intercepted; no disk is touched.
    """

    EXPORT_XML = """\
<?xml version='1.0' encoding='UTF8'?>
<RESULTS>
  <ROW>
    <COLUMN NAME="RICH_TEXT_NCLOB"><![CDATA[<Proponix><Header><MessageID>103594361C</MessageID></Header></Proponix>]]></COLUMN>
  </ROW>
  <ROW>
    <COLUMN NAME="RICH_TEXT_NCLOB"><![CDATA[<Proponix><Header><MessageID>1035943663</MessageID></Header></Proponix>]]></COLUMN>
  </ROW>
  <ROW>
    <COLUMN NAME="RICH_TEXT_NCLOB"><![CDATA[<Proponix><Header><MessageID>103594362F</MessageID></Header></Proponix>]]></COLUMN>
  </ROW>
</RESULTS>"""

    def setUp(self):
        xe.logger = logging.getLogger("test")

    def test_all_three_messages_extracted(self):
        """Verify that All three messages extracted."""
        ext = make_extractor(input_file="export.xml", output_dir="xmls",
                             output_file_name="archive", create_zip=False)
        handle = MagicMock()
        handle.__enter__ = lambda s: s
        handle.__exit__ = MagicMock(return_value=False)
        handle.write = lambda data: None
        opened_files = []

        def tracked_open(path, mode="r", **kw):
            if "w" in mode:
                opened_files.append(path)
            return handle

        with patch_iterparse(self.EXPORT_XML), \
             patch.object(ext, "check_output_dir"), \
             patch.object(ext, "create_zip_archive"), \
             patch("builtins.open", side_effect=tracked_open):
            ext.extract_and_save_elements()

        names = {os.path.basename(p) for p in opened_files}
        self.assertIn("103594361C.xml", names)
        self.assertIn("1035943663.xml", names)
        self.assertIn("103594362F.xml", names)

    def test_zip_archive_triggered_when_requested(self):
        """Verify that Zip archive triggered when requested."""
        ext = make_extractor(create_zip=True, output_file_name="export_out")
        handle = MagicMock()
        handle.__enter__ = lambda s: s
        handle.__exit__ = MagicMock(return_value=False)
        handle.write = MagicMock()

        with patch_iterparse(self.EXPORT_XML), \
             patch("builtins.open", return_value=handle), \
             patch.object(ext, "check_output_dir"), \
             patch.object(ext, "create_zip_archive") as mock_zip:
            ext.extract_and_save_elements()

        mock_zip.assert_called_once()
