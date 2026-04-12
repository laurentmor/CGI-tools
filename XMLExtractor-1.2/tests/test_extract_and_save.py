import unittest
from unittest.mock import MagicMock, mock_open, patch
import xml_extractor as xe
from tests.fixtures import make_extractor


class TestExtractAndSave(unittest.TestCase):

    def setUp(self):
        xe.logger = MagicMock()

    def _make_elem(self, tag, text=None):
        elem = MagicMock()
        elem.tag = tag
        elem.text = text
        elem.find = MagicMock()
        elem.clear = MagicMock()
        return elem

    # --------------------------------------------------
    # 1. Invalid root tag
    # --------------------------------------------------
    def test_invalid_root(self):
        ext = make_extractor()
        context = iter([("start", MagicMock(tag="WRONG"))])
        with patch("xml_extractor.ET.iterparse", return_value=context), \
             patch.object(ext, "get_row_count", return_value=1), \
             patch.object(ext, "check_output_dir"):
            with self.assertRaises(ValueError):
                ext.extract_and_save_elements()

    # --------------------------------------------------
    # 2. No ROW elements
    # --------------------------------------------------
    def test_no_rows(self):
        ext = make_extractor()
        context = iter([("start", MagicMock(tag="RESULTS"))])
        with patch("xml_extractor.ET.iterparse", return_value=context), \
             patch.object(ext, "get_row_count", return_value=0), \
             patch.object(ext, "check_output_dir"):
            ext.extract_and_save_elements()  # must not raise

    # --------------------------------------------------
    # 3. ROW with no matching column
    # --------------------------------------------------
    def test_row_without_column(self):
        ext = make_extractor()
        root = MagicMock(tag="RESULTS")
        row = self._make_elem("ROW")
        row.find.return_value = None
        context = iter([("start", root), ("end", row)])
        with patch("xml_extractor.ET.iterparse", return_value=context), \
             patch.object(ext, "get_row_count", return_value=1), \
             patch.object(ext, "check_output_dir"):
            ext.extract_and_save_elements()  # must not raise

    # --------------------------------------------------
    # 4. Column present but text is None
    # --------------------------------------------------
    def test_column_without_text(self):
        ext = make_extractor()
        root = MagicMock(tag="RESULTS")
        row = self._make_elem("ROW")
        row.find.return_value = MagicMock(text=None)
        context = iter([("start", root), ("end", row)])
        with patch("xml_extractor.ET.iterparse", return_value=context), \
             patch.object(ext, "get_row_count", return_value=1), \
             patch.object(ext, "check_output_dir"):
            ext.extract_and_save_elements()  # must not raise

    # --------------------------------------------------
    # 5. Column present but xml_id is empty
    # --------------------------------------------------
    def test_empty_xml_id(self):
        ext = make_extractor()
        root = MagicMock(tag="RESULTS")
        row = self._make_elem("ROW")
        row.find.return_value = MagicMock(text="data")
        context = iter([("start", root), ("end", row)])
        with patch("xml_extractor.ET.iterparse", return_value=context), \
             patch.object(ext, "get_row_count", return_value=1), \
             patch.object(ext, "get_message_id", return_value=""), \
             patch.object(ext, "check_output_dir"):
            ext.extract_and_save_elements()  # must not raise

    # --------------------------------------------------
    # 6. Nominal case — file created with correct content
    # --------------------------------------------------
    def test_valid_row_creates_file(self):
        ext = make_extractor(dry_run=False)
        root = MagicMock(tag="RESULTS")
        row = self._make_elem("ROW")
        row.find.return_value = MagicMock(text=" <xml>data</xml> ")
        context = iter([("start", root), ("end", row)])
        m = mock_open()
        with patch("xml_extractor.ET.iterparse", return_value=context), \
             patch.object(ext, "get_row_count", return_value=1), \
             patch.object(ext, "get_message_id", return_value="123"), \
             patch.object(ext, "check_output_dir"), \
             patch("builtins.open", m):
            ext.extract_and_save_elements()
        m().write.assert_called_once_with("<xml>data</xml>")

    # --------------------------------------------------
    # 7. Dry run — no file written
    # --------------------------------------------------
    def test_dry_run(self):
        ext = make_extractor(dry_run=True)
        root = MagicMock(tag="RESULTS")
        row = self._make_elem("ROW")
        row.find.return_value = MagicMock(text="data")
        context = iter([("start", root), ("end", row)])
        with patch("xml_extractor.ET.iterparse", return_value=context), \
             patch.object(ext, "get_row_count", return_value=1), \
             patch.object(ext, "get_message_id", return_value="123"), \
             patch.object(ext, "check_output_dir"), \
             patch("builtins.open") as mock_open_file:
            ext.extract_and_save_elements()
        mock_open_file.assert_not_called()

    # --------------------------------------------------
    # 8. ZIP triggered when create_zip=True
    # --------------------------------------------------
    def test_create_zip_called(self):
        ext = make_extractor(create_zip=True)
        context = iter([("start", MagicMock(tag="RESULTS"))])
        with patch("xml_extractor.ET.iterparse", return_value=context), \
             patch.object(ext, "get_row_count", return_value=0), \
             patch.object(ext, "check_output_dir"), \
             patch.object(ext, "create_zip_archive") as mock_zip:
            ext.extract_and_save_elements()
        mock_zip.assert_called_once()
