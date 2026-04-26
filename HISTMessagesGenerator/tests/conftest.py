# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

"""
tests/conftest.py — pytest fixtures only.

sys.path is set by the root conftest.py before this file loads.
Package name on disk: hist_messages_generator  (no trailing 's')
"""

from __future__ import annotations

import logging
from pathlib import Path

import pytest
from fixtures import (
    ALL_TYPES_ROWS,
    DUPLICATE_ROW,
    LARGE_XML,
    MISSING_COLUMNS_ROW,
    MULTI_ROW,
    SINGLE_ROW,
    make_xml,
)

__all__ = [
    "make_xml",
    "SINGLE_ROW",
    "MULTI_ROW",
    "DUPLICATE_ROW",
    "ALL_TYPES_ROWS",
    "MISSING_COLUMNS_ROW",
    "LARGE_XML",
]


@pytest.fixture()
def tmp_xml(tmp_path):
    def _write(content: str, filename: str = "export.xml") -> Path:
        p = tmp_path / filename
        p.write_text(content, encoding="utf-8")
        return p

    return _write


@pytest.fixture()
def single_row_xml(tmp_xml):
    return tmp_xml(SINGLE_ROW)


@pytest.fixture()
def multi_row_xml(tmp_xml):
    return tmp_xml(MULTI_ROW)


@pytest.fixture()
def duplicate_row_xml(tmp_xml):
    return tmp_xml(DUPLICATE_ROW)


@pytest.fixture()
def all_types_xml(tmp_xml):
    return tmp_xml(ALL_TYPES_ROWS)


@pytest.fixture()
def large_xml(tmp_xml):
    return tmp_xml(LARGE_XML)


@pytest.fixture()
def missing_col_xml(tmp_xml):
    return tmp_xml(MISSING_COLUMNS_ROW)


@pytest.fixture()
def bad_xml(tmp_xml):
    return tmp_xml("<ROWS><ROW><UNCLOSED>")


@pytest.fixture()
def generator(tmp_path, single_row_xml):
    from hist_messages_generator.hist_messages_generator import HISTMessagesGenerator

    return HISTMessagesGenerator(
        log_file=str(tmp_path / "test.log"),
        input_file=str(single_row_xml),
        customer="CUST01",
        bank="BANKX",
        enable_file_logging=False,
    )


@pytest.fixture()
def generator_factory(tmp_path):
    from hist_messages_generator.hist_messages_generator import HISTMessagesGenerator

    def _make(xml_path, customer="CUST01", bank="BANKX"):
        return HISTMessagesGenerator(
            log_file=str(tmp_path / "test.log"),
            input_file=str(xml_path),
            customer=customer,
            bank=bank,
            enable_file_logging=False,
        )

    return _make


@pytest.fixture(autouse=True)
def _silence_logger():
    # __name__ inside the source module is hist_messages_generator.hist_messages_generator
    lgr = logging.getLogger(
        "HISTMessagesGenerator - hist_messages_generator.hist_messages_generator"
    )
    original = lgr.level
    lgr.setLevel(logging.CRITICAL)
    yield
    lgr.setLevel(original)
