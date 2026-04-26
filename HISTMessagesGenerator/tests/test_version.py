# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

"""
Unit tests for version.py

Covers:
- get_version() returns a non-empty string
- Falls back to git describe when package metadata absent
- Falls back to 'dev' when both metadata and git are unavailable
- __version__ module attribute is set
"""

from __future__ import annotations

from unittest.mock import patch

import pytest


class TestGetVersion:
    def test_returns_string(self):
        from hist_messages_generator.version import get_version

        result = get_version()
        assert isinstance(result, str)

    def test_returns_non_empty(self):
        from hist_messages_generator.version import get_version

        assert get_version()

    def test_version_module_attribute_set(self):
        from hist_messages_generator import version

        assert hasattr(version, "__version__")
        assert isinstance(version.__version__, str)

    def test_fallback_to_git_when_package_not_found(self):
        from importlib.metadata import PackageNotFoundError

        with patch(
            "hist_messages_generator.version.version",
            side_effect=PackageNotFoundError("xml-extractor"),
        ):
            with patch(
                "hist_messages_generator.version.subprocess.check_output",
                return_value="v1.2.3-4-gabcdef",
            ):
                from hist_messages_generator.version import get_version

                result = get_version()
                assert result == "v1.2.3-4-gabcdef"

    def test_fallback_to_dev_when_git_unavailable(self):
        from importlib.metadata import PackageNotFoundError

        with patch(
            "hist_messages_generator.version.version",
            side_effect=PackageNotFoundError("xml-extractor"),
        ):
            with patch(
                "hist_messages_generator.version.subprocess.check_output",
                side_effect=Exception("git not found"),
            ):
                from hist_messages_generator.version import get_version

                result = get_version()
                assert result == "dev"

    def test_uses_package_metadata_when_available(self):
        with patch(
            "hist_messages_generator.version.version",
            return_value="3.0.0",
        ):
            from hist_messages_generator.version import get_version

            result = get_version()
            assert result == "3.0.0"
