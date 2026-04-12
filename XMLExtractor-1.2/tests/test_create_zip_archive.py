import logging
import unittest
from unittest.mock import patch
import xml_extractor as xe
from tests.fixtures import make_extractor


class TestCreateZipArchive(unittest.TestCase):

    def setUp(self):
        xe.logger = logging.getLogger("test")

    def test_dry_run_skips_zip(self):
        ext = make_extractor(dry_run=True)
        with patch.object(ext, "create_unprotected_zip") as mock_u, \
             patch.object(ext, "create_protected_zip") as mock_p:
            ext.create_zip_archive()
        mock_u.assert_not_called()
        mock_p.assert_not_called()

    def test_no_password_calls_unprotected(self):
        ext = make_extractor(output_file_name="archive", zip_password=None)
        with patch.object(ext, "create_unprotected_zip") as mock_u:
            ext.create_zip_archive()
        mock_u.assert_called_once()

    def test_with_password_calls_protected(self):
        ext = make_extractor(output_file_name="archive", zip_password="pass1")
        with patch.object(ext, "create_protected_zip") as mock_p:
            ext.create_zip_archive()
        mock_p.assert_called_once()

    def test_protected_zip_filename_suffix(self):
        ext = make_extractor(output_file_name="myarchive", zip_password="pass1")
        with patch.object(ext, "create_protected_zip"):
            ext.create_zip_archive()
        self.assertIn("protected", ext.zip_filename)
