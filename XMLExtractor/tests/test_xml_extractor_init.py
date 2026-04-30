# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

"""Unit tests for XMLExtractor initialization.
These tests verify that constructor arguments are stored correctly and defaults are applied."""

import unittest
from unittest.mock import patch

from tests.fixtures import make_extractor


class TestXMLExtractorInit(unittest.TestCase):
    """Verify XMLExtractor initialization and default attribute handling."""

    def test_all_attributes_set(self):
        """Verify that All attributes set."""
        extractor = make_extractor(
            input_file="in.xml", output_dir="out", zip_password="pass1", create_zip=True
        )
        self.assertEqual(extractor.input_file, "in.xml")
        self.assertEqual(extractor.output_dir, "out")
        self.assertEqual(extractor.zip_password, "pass1")
        self.assertTrue(extractor.create_zip)

    def test_dry_run_default_false(self):
        """Verify that dry-run mode default false."""
        self.assertFalse(make_extractor().dry_run)

    def test_mute_stored(self):
        """Verify that Mute stored."""
        self.assertTrue(make_extractor(mute=True).mute)


class TestCheckOutputDir(unittest.TestCase):
    """Verify check_output_dir handles directory creation and user prompts correctly."""

    def test_directory_created_when_not_exists(self):
        """Verify that Directory created when not exists."""
        ext = make_extractor(output_dir="new_dir")
        with (
            patch("xml_extractor.xml_extractor.os.path.exists", return_value=False),
            patch("xml_extractor.xml_extractor.os.makedirs") as mock_makedirs,
        ):
            ext.check_output_dir()
        mock_makedirs.assert_called_once_with("new_dir", exist_ok=True)

    def test_file_deleted_and_directory_created(self):
        """Verify that File deleted and directory created."""
        ext = make_extractor(output_dir="file_path")
        with (
            patch("xml_extractor.xml_extractor.os.path.exists", return_value=True),
            patch("xml_extractor.xml_extractor.os.path.isfile", return_value=True),
            patch("builtins.input", return_value="Y"),
            patch("xml_extractor.xml_extractor.os.remove") as mock_remove,
            patch("xml_extractor.xml_extractor.os.makedirs") as mock_makedirs,
            patch("xml_extractor.xml_extractor.logger") as mock_logger,
        ):
            ext.check_output_dir()
        mock_remove.assert_called_once_with("file_path")
        mock_makedirs.assert_called_once_with("file_path", exist_ok=True)
        mock_logger.info.assert_called_with(
            "Removed file and created output directory 'file_path'."
        )

    def test_file_not_deleted_when_user_says_no(self):
        """Verify that File not deleted when user says no."""
        ext = make_extractor(output_dir="file_path")
        with (
            patch("xml_extractor.xml_extractor.os.path.exists", return_value=True),
            patch("xml_extractor.xml_extractor.os.path.isfile", return_value=True),
            patch("builtins.input", return_value="N"),
            patch("xml_extractor.xml_extractor.logger") as mock_logger,
            self.assertRaises(ValueError),
        ):
            ext.check_output_dir()
        mock_logger.error.assert_called_with("Output path 'file_path' is a file. Cannot proceed.")

    def test_directory_not_deleted_when_user_says_no(self):
        """Verify that Directory not deleted when user says no."""
        ext = make_extractor(output_dir="dir_path")
        with (
            patch("xml_extractor.xml_extractor.os.path.exists", return_value=True),
            patch("xml_extractor.xml_extractor.os.path.isfile", return_value=False),
            patch("builtins.input", return_value="N"),
            patch("xml_extractor.xml_extractor.logger") as mock_logger,
        ):
            ext.check_output_dir()
        mock_logger.info.assert_called_with(
            "Output directory 'dir_path' already exists. Content will be appended."
        )
