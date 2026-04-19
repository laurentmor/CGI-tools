# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

"""Unit tests for delete_output_dir().
These tests confirm that files and directories are removed safely from the output tree."""

import logging
import unittest
from unittest.mock import patch

import xml_extractor as xe
from tests.fixtures import make_extractor


class TestDeleteOutputDir(unittest.TestCase):
    """Verify delete_output_dir() removes output files and directories safely and completely."""

    def setUp(self):
        xe.logger = logging.getLogger("test")

    def test_removes_files_and_dir(self):
        """Verify that Removes files and directory."""
        ext = make_extractor(output_dir="out")
        with patch("xml_extractor.shutil.rmtree") as mock_rmtree:
            ext.delete_output_dir()

        mock_rmtree.assert_called_once_with("out")
