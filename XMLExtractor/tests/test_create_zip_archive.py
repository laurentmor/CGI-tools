# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

"""Unit tests for create_zip_archive().
These tests verify that archive creation selects protected or unprotected ZIP workflows correctly."""

import logging
import unittest
from unittest.mock import patch

import xml_extractor as xe
from tests.fixtures import make_extractor


class TestCreateZipArchive(unittest.TestCase):
    """Verify archive creation selects the correct protected or unprotected path, including dry-run bypass."""

    def setUp(self):
        xe.logger = logging.getLogger("test")

    def test_dry_run_skips_zip(self):
        """Verify that dry-run mode skips zip."""
        ext = make_extractor(dry_run=True)
        with (
            patch.object(ext, "create_unprotected_zip") as mock_u,
            patch.object(ext, "create_protected_zip") as mock_p,
        ):
            ext.create_zip_archive()
        mock_u.assert_not_called()
        mock_p.assert_not_called()

    def test_no_password_calls_unprotected(self):
        """Verify that No password calls unprotected."""
        ext = make_extractor(output_file_name="archive", zip_password=None)
        with patch.object(ext, "create_unprotected_zip") as mock_u:
            ext.create_zip_archive()
        mock_u.assert_called_once()

    def test_with_password_calls_protected(self):
        """Verify that With password calls protected."""
        ext = make_extractor(output_file_name="archive", zip_password="pass1")
        with patch.object(ext, "create_protected_zip") as mock_p:
            ext.create_zip_archive()
        mock_p.assert_called_once()

    def test_protected_zip_filename_suffix(self):
        """Verify that Protected zip filename suffix."""
        ext = make_extractor(output_file_name="myarchive", zip_password="pass1")
        with patch.object(ext, "create_protected_zip"):
            ext.create_zip_archive()
        self.assertIn("protected", ext.zip_filename)
