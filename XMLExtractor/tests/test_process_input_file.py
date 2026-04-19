# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

"""Unit tests for process_input_file_to_ensure_is_clean().
These tests cover file cleaning, temporary backup handling, and replacement semantics."""

import unittest
from unittest.mock import MagicMock, mock_open, patch

import xml_extractor as xe  # type: ignore
from tests.fixtures import REPLACE_MAP


class TestProcessInputFile(unittest.TestCase):
    """Verify that input files are cleaned, backed up, and replaced correctly when necessary."""

    def setUp(self):
        import xml_extractor.xml_extractor as xe_mod # type: ignore
        xe_mod.logger = MagicMock()
        xe.replace_map = REPLACE_MAP

    def test_cleaning_happens(self):
        """Verify that Cleaning happens."""
        m_read = mock_open(read_data="dirty\n")
        m_write = mock_open()

        def open_side_effect(file, mode="r", *args, **kwargs):
            return m_read() if "r" in mode else m_write()

        with (
            patch("builtins.open", side_effect=open_side_effect),
            patch("xml_extractor.xml_extractor.clean_xml_content", return_value="clean\n"),
            patch("xml_extractor.xml_extractor.shutil.copy2"),
            patch("xml_extractor.xml_extractor.os.replace") as mock_replace,
        ):
            xe.process_input_file_to_ensure_is_clean("file.xml")

            m_write().writelines.assert_called_once_with(["clean\n"])
            mock_replace.assert_called_once()

    def test_no_cleaning_no_temp_file(self):
        """Verify that No cleaning no temporary file."""
        m = mock_open(read_data="clean\n")

        with (
            patch("builtins.open", m),
            patch("xml_extractor.xml_extractor.clean_xml_content", side_effect=lambda x, _, __: x),
            patch("xml_extractor.xml_extractor.shutil.copy2"),
            patch("xml_extractor.xml_extractor.os.path.exists", return_value=False),
            patch("xml_extractor.xml_extractor.os.remove") as mock_remove,
        ):
            xe.process_input_file_to_ensure_is_clean("file.xml")

            mock_remove.assert_not_called()

    def test_no_cleaning_temp_exists_removed(self):
        """Verify that No cleaning temporary exists removed."""
        m = mock_open(read_data="clean\n")

        with (
            patch("builtins.open", m),
            patch("xml_extractor.xml_extractor.clean_xml_content", side_effect=lambda x, _, __: x),
            patch("xml_extractor.xml_extractor.shutil.copy2"),
            patch("xml_extractor.xml_extractor.os.path.exists", return_value=True),
            patch("xml_extractor.xml_extractor.os.remove") as mock_remove,
        ):
            xe.process_input_file_to_ensure_is_clean("file.xml")

            mock_remove.assert_called_once()

    def test_multiple_lines_some_cleaned(self):
        """Verify that Multiple lines some cleaned."""
        m_read = mock_open(read_data="line1\nline2\n")
        m_write = mock_open()

        def fake_clean(line, _, __):
            return "cleaned\n" if "line1" in line else line

        def open_side_effect(file, mode="r", *args, **kwargs):
            return m_read() if "r" in mode else m_write()

        with (
            patch("builtins.open", side_effect=open_side_effect),
            patch("xml_extractor.xml_extractor.clean_xml_content", side_effect=fake_clean),
            patch("xml_extractor.xml_extractor.shutil.copy2"),
            patch("xml_extractor.xml_extractor.os.replace"),
        ):
            xe.process_input_file_to_ensure_is_clean("file.xml")

            m_write().writelines.assert_called_once_with(["cleaned\n", "line2\n"])

    def test_backup_created(self):
        """Verify that Backup created."""
        m = mock_open(read_data="data\n")

        with (
            patch("builtins.open", m),
            patch("xml_extractor.xml_extractor.clean_xml_content", return_value="cleaned\n"),
            patch("xml_extractor.xml_extractor.shutil.copy2") as mock_copy,
            patch("xml_extractor.xml_extractor.os.replace"),
            patch("xml_extractor.xml_extractor.os.path.exists", return_value=False),
        ):
            xe.process_input_file_to_ensure_is_clean("file.xml")

        mock_copy.assert_called_once_with("file.xml", "file.xml.bak")