# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

"""Unit tests for play_sound().
These tests verify that sounds play only when a file exists and mute mode is disabled."""

import unittest
from unittest.mock import patch

import xml_extractor as xe  # type: ignore


class TestPlaySound(unittest.TestCase):
    """Verify sound playback is invoked only when a sound file exists and mute is disabled."""

    # --------------------------------------------------
    # 1. Sound played — nominal case
    # --------------------------------------------------
    def test_play_sound_called(self):
        """Verify that play_sound calls winsound.PlaySound when not muted and file exists."""
        with (
            patch("xml_extractor.xml_extractor.WINSOUND_AVAILABLE", True),
            patch("xml_extractor.xml_extractor.winsound") as mock_winsound,
            patch("pathlib.Path.exists", return_value=True),
        ):
            xe.play_sound("test.wav", mute=False)
        mock_winsound.PlaySound.assert_called_once()

    # --------------------------------------------------
    # 2. File absent → nothing played
    # --------------------------------------------------
    def test_file_not_exists(self):
        """Verify that File not exists."""
        with patch("os.path.exists", return_value=False), patch("winsound.PlaySound") as mock_play:
            xe.play_sound("test.wav", mute=False)
        mock_play.assert_not_called()

    # --------------------------------------------------
    # 3. Mute enabled → nothing played
    # --------------------------------------------------
    def test_mute_true(self):
        """Verify that Mute true."""
        with patch("os.path.exists", return_value=True), patch("winsound.PlaySound") as mock_play:
            xe.play_sound("test.wav", mute=True)
        mock_play.assert_not_called()

    # --------------------------------------------------
    # 4. Mute + file absent → nothing played
    # --------------------------------------------------
    def test_mute_and_file_not_exists(self):
        """Verify that Mute and file not exists."""
        with patch("os.path.exists", return_value=False), patch("winsound.PlaySound") as mock_play:
            xe.play_sound("test.wav", mute=True)
        mock_play.assert_not_called()