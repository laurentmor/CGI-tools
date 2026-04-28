# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

import pytest
from fixtures import ALL_TYPES_ROWS, DUPLICATE_ROW, MULTI_ROW, SINGLE_ROW, make_xml

from hist_messages_generator.hist_messages_generator import (
    HISTMessagesGenerator,
    InstrumentIndex,
    main,
)
from hist_messages_generator.product_class_resolver import InstrumentClass

pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")


# =========================================================
# 🧩 Helpers
# =========================================================

def run_and_read_sql(generator, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    generator.run()
    return (tmp_path / "sql_statements.sql").read_text()


@pytest.fixture
def bare_generator():
    return HISTMessagesGenerator.__new__(HISTMessagesGenerator)


# =========================================================
# InstrumentIndex
# =========================================================

@pytest.mark.parametrize(
    "member,expected",
    [
        (InstrumentIndex.CLASS, 0),
        (InstrumentIndex.PARTY_TYPE, 1),
    ],
)
def test_instrument_index_values(member, expected):
    assert member == expected


def test_instrument_index_ordering():
    assert InstrumentIndex.CLASS < InstrumentIndex.PARTY_TYPE


def test_instrument_index_type():
    assert isinstance(InstrumentIndex.CLASS, int)


# =========================================================
# __init__
# =========================================================

def test_init_fields(generator):
    assert "export" in generator.input_file
    assert generator.customer == "CUST01"
    assert generator.bank == "BANKX"


def test_file_logging_disabled(tmp_path, single_row_xml):
    log_path = tmp_path / "x.log"
    HISTMessagesGenerator(
        log_file=str(log_path),
        input_file=str(single_row_xml),
        customer="C",
        bank="B",
        enable_file_logging=False,
    )
    assert not log_path.exists()


def test_file_logging_enabled(tmp_path, single_row_xml):
    log_path = tmp_path / "enabled.log"
    HISTMessagesGenerator(
        log_file=str(log_path),
        input_file=str(single_row_xml),
        customer="C",
        bank="B",
        enable_file_logging=True,
    )

    handlers = [
        Path(h.baseFilename)
        for h in HISTMessagesGenerator.logger.handlers
        if isinstance(h, logging.FileHandler)
    ]
    assert log_path in handlers


# =========================================================
# XML validation
# =========================================================

def test_validate_xml_valid(generator, single_row_xml):
    assert generator.validate_xml_structure(str(single_row_xml))


@pytest.mark.parametrize(
    "path,expected",
    [
        ("bad_xml", (ET.ParseError, AttributeError)),
        ("/no/file.xml", (FileNotFoundError, AttributeError)),
    ],
)
def test_validate_xml_errors(generator, request, path, expected):
    p = request.getfixturevalue(path) if path != "/no/file.xml" else path
    with pytest.raises(expected):
        generator.validate_xml_structure(str(p))


# =========================================================
# Columns validation
# =========================================================

def test_columns_valid(generator, single_row_xml):
    generator.validate_columns_exist(
        str(single_row_xml), ["INSTRUMENT_ID", "TYPE_", "CUSTOMER_PARTY_TYPE"]
    )


def test_columns_missing(generator, missing_col_xml):
    with pytest.raises(ValueError):
        generator.validate_columns_exist(
            str(missing_col_xml), ["INSTRUMENT_ID", "TYPE_", "CUSTOMER_PARTY_TYPE"]
        )


@pytest.mark.parametrize(
    "cols",
    [
        ["INSTRUMENT_ID"],
        [],
    ],
)
def test_columns_partial_ok(generator, single_row_xml, cols):
    generator.validate_columns_exist(str(single_row_xml), cols)


# =========================================================
# Row count
# =========================================================

@pytest.mark.parametrize(
    "fixture_name,expected",
    [
        ("single_row_xml", 1),
        ("multi_row_xml", 3),
    ],
)
def test_row_count(generator_factory, request, fixture_name, expected):
    xml = request.getfixturevalue(fixture_name)
    g = generator_factory(xml)
    assert g.get_row_count() == expected


def test_row_count_empty(generator_factory, tmp_xml):
    g = generator_factory(tmp_xml("<ROWS></ROWS>"))
    assert g.get_row_count() == 0


def test_row_count_missing(generator):
    generator.input_file = "/no/file.xml"
    with pytest.raises((FileNotFoundError, AttributeError)):
        generator.get_row_count()


# =========================================================
# build_instruments_dictionary
# =========================================================

@pytest.mark.parametrize(
    "xml_str,expected_len",
    [
        (SINGLE_ROW, 1),
        (MULTI_ROW, 3),
        (DUPLICATE_ROW, 1),
        ("<ROWS></ROWS>", 0),
    ],
)
def test_build_dict_lengths(bare_generator, xml_str, expected_len):
    root = ET.fromstring(xml_str)
    result = bare_generator.build_instruments_dictionary(root)
    assert len(result) == expected_len


def test_build_dict_values(bare_generator):
    root = ET.fromstring(SINGLE_ROW)
    result = bare_generator.build_instruments_dictionary(root)

    assert result["INS001"][InstrumentIndex.CLASS] == InstrumentClass.DOCUMENTARY_LC
    assert result["INS001"][InstrumentIndex.PARTY_TYPE] == "BUYER"


def test_build_dict_missing_id(bare_generator):
    xml = make_xml([{"TYPE_": "DLC", "CUSTOMER_PARTY_TYPE": "BUYER"}])
    result = bare_generator.build_instruments_dictionary(ET.fromstring(xml))
    assert result == {}


def test_build_dict_whitespace(bare_generator):
    xml = make_xml([
        {"INSTRUMENT_ID": "  INS999  ", "TYPE_": "  DLC  ", "CUSTOMER_PARTY_TYPE": "  BUYER  "}
    ])
    result = bare_generator.build_instruments_dictionary(ET.fromstring(xml))
    assert "INS999" in result
    assert result["INS999"][InstrumentIndex.PARTY_TYPE] == "BUYER"


def test_build_dict_all_types(bare_generator):
    root = ET.fromstring(ALL_TYPES_ROWS)
    result = bare_generator.build_instruments_dictionary(root)
    assert len(result) == 23


# =========================================================
# run()
# =========================================================

def test_run_creates_file(generator_factory, single_row_xml, tmp_path, monkeypatch):
    g = generator_factory(single_row_xml)
    run_and_read_sql(g, tmp_path, monkeypatch)
    assert (tmp_path / "sql_statements.sql").exists()


@pytest.mark.parametrize(
    "kwargs,expected",
    [
        ({}, "INSERT INTO"),
        ({"customer": "MY_CUST"}, "MY_CUST"),
        ({"bank": "MY_BANK"}, "MY_BANK"),
    ],
)
def test_run_basic(generator_factory, single_row_xml, tmp_path, monkeypatch, kwargs, expected):
    g = generator_factory(single_row_xml, **kwargs)
    sql = run_and_read_sql(g, tmp_path, monkeypatch)
    assert expected in sql


@pytest.mark.parametrize(
    "fixture_name,count",
    [
        ("multi_row_xml", 3),
        ("duplicate_row_xml", 1),
    ],
)
def test_run_insert_counts(generator_factory, request, tmp_path, monkeypatch, fixture_name, count):
    xml = request.getfixturevalue(fixture_name)
    g = generator_factory(xml)
    sql = run_and_read_sql(g, tmp_path, monkeypatch)
    assert sql.count("INSERT INTO") == count


def test_run_contains_expected_data(generator_factory, single_row_xml, tmp_path, monkeypatch):
    g = generator_factory(single_row_xml)
    sql = run_and_read_sql(g, tmp_path, monkeypatch)

    assert "commit;" in sql
    assert "INS001" in sql
    assert "BUYER" in sql
    assert "documentary_lc" in sql
    assert "select * from outgoing_intrfc_e" in sql


@pytest.mark.parametrize(
    "fixture_name,expected_exception",
    [
        ("bad_xml", (ET.ParseError, AttributeError)),
        ("missing_col_xml", ValueError),
    ],
)
def test_run_errors(generator_factory, request, fixture_name, expected_exception):
    xml = request.getfixturevalue(fixture_name)
    g = generator_factory(xml)
    with pytest.raises(expected_exception):
        g.run()


def test_run_bil_regression(generator_factory, tmp_xml, tmp_path, monkeypatch):
    xml_path = tmp_xml(
        make_xml([{"INSTRUMENT_ID": "BIL001", "TYPE_": "BIL", "CUSTOMER_PARTY_TYPE": "BUYER"}])
    )
    g = generator_factory(xml_path)
    sql = run_and_read_sql(g, tmp_path, monkeypatch)
    assert "billing_instrument" in sql


# =========================================================
# CLI
# =========================================================

def test_main_calls_run(single_row_xml):
    with patch("sys.argv", ["prog", str(single_row_xml), "C", "B"]),\
         patch.object(HISTMessagesGenerator, "run") as mock:
            main()
            mock.assert_called_once()


def test_main_passes_args(single_row_xml):
    captured = {}

    def fake_init(self, **kwargs):
        captured.update(kwargs)

    with patch("sys.argv", ["prog", str(single_row_xml), "CUST", "BANK"]),\
         patch.object(HISTMessagesGenerator, "__init__", fake_init),\
         patch.object(HISTMessagesGenerator, "run"):
                main()

    assert captured["customer"] == "CUST"
    assert captured["bank"] == "BANK"


def test_main_version():
    with patch("sys.argv", ["prog", "--version"]):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0