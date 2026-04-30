# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

"""Unit tests for create_protected_zip().
These tests cover password handling, nested directory traversal, and error propagation during protected ZIP creation."""

import logging
import unittest
from unittest.mock import MagicMock, patch

import xml_extractor as xe  # type: ignore
from tests.fixtures import make_extractor


class TestCreateProtectedZip(unittest.TestCase):
    """Verify protected ZIP creation includes password setup, nested directories, and robust error handling."""

    def setUp(self):
        xe.logger = logging.getLogger("test")

    def _make_fake_zip(self):
        fake_zip = MagicMock()
        fake_zip.__enter__ = lambda s: s
        fake_zip.__exit__ = MagicMock(return_value=False)
        return fake_zip

    # --------------------------------------------------
    # 1. Nominal case (covers file loop)
    # --------------------------------------------------
    def test_zip_with_files(self):
        """Verify that Zip with files."""
        ext = make_extractor(zip_password="secret123", output_dir="out")
        fake_zip = self._make_fake_zip()
        walk_data = [("out", [], ["a.xml", "b.xml"])]

        with (
            patch("xml_extractor.xml_extractor.pyzipper.AESZipFile", return_value=fake_zip),
            patch("xml_extractor.xml_extractor.os.walk", return_value=iter(walk_data)),
        ):
            ext.create_protected_zip("archive.zip")

        fake_zip.setpassword.assert_called_once_with(b"secret123")
        self.assertEqual(fake_zip.write.call_count, 2)

    # --------------------------------------------------
    # 2. No files (empty branch)
    # --------------------------------------------------
    def test_zip_no_files(self):
        """Verify that Zip no files."""
        ext = make_extractor(zip_password="secret123", output_dir="out")
        fake_zip = self._make_fake_zip()

        with (
            patch("xml_extractor.xml_extractor.pyzipper.AESZipFile", return_value=fake_zip),
            patch("xml_extractor.xml_extractor.os.walk", return_value=iter([("out", [], [])])),
        ):
            ext.create_protected_zip("archive.zip")

        fake_zip.write.assert_not_called()

    # --------------------------------------------------
    # 3. Nested subdirectories
    # --------------------------------------------------
    def test_nested_directories(self):
        """Verify that Nested directories."""
        ext = make_extractor(zip_password="secret123", output_dir="out")
        fake_zip = self._make_fake_zip()
        walk_data = [("out", ["sub"], ["a.xml"]), ("out/sub", [], ["b.xml"])]

        with (
            patch("xml_extractor.xml_extractor.pyzipper.AESZipFile", return_value=fake_zip),
            patch("xml_extractor.xml_extractor.os.walk", return_value=iter(walk_data)),
        ):
            ext.create_protected_zip("archive.zip")

        self.assertEqual(fake_zip.write.call_count, 2)

    # --------------------------------------------------
    # 4. UTF-8 password encoding
    # --------------------------------------------------
    def test_password_encoding(self):
        """Verify that Password encoding."""
        ext = make_extractor(zip_password="pässwörd", output_dir="out")
        fake_zip = self._make_fake_zip()

        with (
            patch("xml_extractor.xml_extractor.pyzipper.AESZipFile", return_value=fake_zip),
            patch("xml_extractor.xml_extractor.os.walk", return_value=iter([("out", [], [])])),
        ):
            ext.create_protected_zip("archive.zip")

        fake_zip.setpassword.assert_called_once_with("pässwörd".encode())

    # --------------------------------------------------
    # 5. Exception on open re-raised
    # --------------------------------------------------
    def test_exception_in_zipfile_reraised(self):
        """Verify that Exception in zipfile reraised."""
        ext = make_extractor(zip_password="secret123", output_dir="out")
        with (
            patch(
                "xml_extractor.xml_extractor.pyzipper.AESZipFile", side_effect=OSError("zip error")
            ),
            self.assertRaises(IOError),
        ):
            ext.create_protected_zip("archive.zip")

    # --------------------------------------------------
    # 6. Exception on write re-raised
    # --------------------------------------------------
    def test_exception_in_write_reraised(self):
        """Verify that Exception in write reraised."""
        ext = make_extractor(zip_password="secret123", output_dir="out")
        fake_zip = self._make_fake_zip()
        fake_zip.write.side_effect = OSError("write error")

        with (
            patch("xml_extractor.xml_extractor.pyzipper.AESZipFile", return_value=fake_zip),
            patch(
                "xml_extractor.xml_extractor.os.walk", return_value=iter([("out", [], ["a.xml"])])
            ),
            self.assertRaises(IOError),
        ):
            ext.create_protected_zip("archive.zip")

    # --------------------------------------------------
    # 7. Logger called on success
    # --------------------------------------------------
    def test_logger_called(self):
        """Verify that Logger called."""
        ext = make_extractor(zip_password="secret123", output_dir="out")
        fake_zip = self._make_fake_zip()

        with (
            patch("xml_extractor.xml_extractor.pyzipper.AESZipFile", return_value=fake_zip),
            patch("xml_extractor.xml_extractor.os.walk", return_value=iter([("out", [], [])])),
            patch("xml_extractor.xml_extractor.logger.info") as mock_log,
        ):
            ext.create_protected_zip("archive.zip")

        mock_log.assert_called()
