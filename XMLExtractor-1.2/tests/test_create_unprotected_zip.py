import logging
import unittest
import zipfile
from unittest.mock import MagicMock, patch
import xml_extractor as xe
from tests.fixtures import make_extractor


class TestCreateUnprotectedZip(unittest.TestCase):

    def setUp(self):
        xe.logger = logging.getLogger("test")

    def test_zip_contains_output_files(self):
        ext = make_extractor(output_dir="out", output_file_name="archive")
        ext.zip_filename = "archive.zip"
        walk_result = [("out", [], ["a.xml", "b.xml"])]
        fake_zip = MagicMock()
        fake_zip.__enter__ = lambda s: s
        fake_zip.__exit__ = MagicMock(return_value=False)
        with patch("os.walk", return_value=iter(walk_result)), \
             patch("zipfile.ZipFile", return_value=fake_zip):
            ext.create_unprotected_zip()
        self.assertTrue(fake_zip.write.called)

    def test_zip_created_with_deflate(self):
        ext = make_extractor()
        ext.zip_filename = "out.zip"
        fake_zip = MagicMock()
        fake_zip.__enter__ = lambda s: s
        fake_zip.__exit__ = MagicMock(return_value=False)
        with patch("os.walk", return_value=iter([])), \
             patch("zipfile.ZipFile", return_value=fake_zip) as mock_zf:
            ext.create_unprotected_zip()
        mock_zf.assert_called_once_with(
            "out.zip", "w", compression=zipfile.ZIP_DEFLATED
        )
