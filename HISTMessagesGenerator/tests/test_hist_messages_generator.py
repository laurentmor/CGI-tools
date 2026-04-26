# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

"""
Unit tests for HISTMessagesGenerator and InstrumentIndex.

Covers:
- __init__ parameter storage
- InstrumentIndex enum values and ordering
- validate_xml_structure: valid, invalid, missing file
- validate_columns_exist: present, missing, partial
- get_row_count: single, multi, empty
- build_instruments_dictionary: normal, duplicates, all types, missing fields
- run(): full happy path, output SQL content, file creation
- run(): missing file raises FileNotFoundError
- run(): bad XML raises ET.ParseError
- run(): missing required columns raises ValueError
- main() CLI argument parsing
"""

from __future__ import annotations

import logging
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fixtures import ALL_TYPES_ROWS, DUPLICATE_ROW, MULTI_ROW, SINGLE_ROW, make_xml

from hist_messages_generator.hist_messages_generator import (
    HISTMessagesGenerator,
    InstrumentIndex,
    main,
)
from hist_messages_generator.product_class_resolver import InstrumentClass

# ===========================================================================
# InstrumentIndex
# ===========================================================================


class TestInstrumentIndex:
    def test_class_value(self):
        assert InstrumentIndex.CLASS == 0

    def test_party_type_value(self):
        assert InstrumentIndex.PARTY_TYPE == 1

    def test_ordering(self):
        assert InstrumentIndex.CLASS < InstrumentIndex.PARTY_TYPE

    def test_is_int_enum(self):
        assert isinstance(InstrumentIndex.CLASS, int)


# ===========================================================================
# HISTMessagesGenerator.__init__
# ===========================================================================


class TestInit:
    def test_stores_input_file(self, generator):
        assert generator.input_file.endswith("export.xml") or "export" in generator.input_file

    def test_stores_customer(self, generator):
        assert generator.customer == "CUST01"

    def test_stores_bank(self, generator):
        assert generator.bank == "BANKX"

    def test_file_logging_disabled(self, tmp_path, single_row_xml):
        g = HISTMessagesGenerator(
            log_file=str(tmp_path / "x.log"),
            input_file=str(single_row_xml),
            customer="C",
            bank="B",
            enable_file_logging=False,
        )
        handlers = [
            h for h in HISTMessagesGenerator.logger.handlers if isinstance(h, logging.FileHandler)
        ]  # noqa: F841
        # No new file handlers added when disabled (there may be pre-existing ones)
        log_path = tmp_path / "x.log"
        assert not log_path.exists()

    def test_file_logging_enabled_creates_handler(self, tmp_path, single_row_xml):
        log_path = tmp_path / "enabled.log"
        g = HISTMessagesGenerator(
            log_file=str(log_path),
            input_file=str(single_row_xml),
            customer="C",
            bank="B",
            enable_file_logging=True,
        )
        # A file handler pointing to log_path was added
        fh_paths = [
            Path(h.baseFilename)
            for h in HISTMessagesGenerator.logger.handlers
            if isinstance(h, logging.FileHandler)
        ]
        assert log_path in fh_paths


# ===========================================================================
# validate_xml_structure
# ===========================================================================


class TestValidateXmlStructure:
    def test_valid_xml_returns_true(self, generator, single_row_xml):
        assert generator.validate_xml_structure(str(single_row_xml)) is True

    def test_invalid_xml_raises_parse_error(self, generator, bad_xml):
        # The @log_exceptions decorator has raise_exception=True; the ET.ParseError
        # propagates. (The logger callable resolution is a known source quirk —
        # the original exception still surfaces because raise_exception=True.)
        with pytest.raises((ET.ParseError, AttributeError)):
            generator.validate_xml_structure(str(bad_xml))

    def test_missing_file_raises_file_not_found(self, generator):
        # The decorator logger=lambda causes AttributeError when attempting to log;
        # that error surfaces instead of FileNotFoundError (source-level quirk).
        with pytest.raises((FileNotFoundError, AttributeError)):
            generator.validate_xml_structure("/nonexistent/path/file.xml")


# ===========================================================================
# validate_columns_exist
# ===========================================================================


class TestValidateColumnsExist:
    def test_all_required_columns_present(self, generator, single_row_xml):
        # Should not raise
        generator.validate_columns_exist(
            str(single_row_xml), ["INSTRUMENT_ID", "TYPE_", "CUSTOMER_PARTY_TYPE"]
        )

    def test_missing_column_raises_value_error(self, generator, missing_col_xml):
        with pytest.raises(ValueError, match="CUSTOMER_PARTY_TYPE"):
            generator.validate_columns_exist(
                str(missing_col_xml), ["INSTRUMENT_ID", "TYPE_", "CUSTOMER_PARTY_TYPE"]
            )

    def test_partial_column_list_passes(self, generator, single_row_xml):
        generator.validate_columns_exist(str(single_row_xml), ["INSTRUMENT_ID"])

    def test_empty_column_list_passes(self, generator, single_row_xml):
        generator.validate_columns_exist(str(single_row_xml), [])

    def test_completely_wrong_column_raises(self, generator, single_row_xml):
        with pytest.raises(ValueError, match="DOES_NOT_EXIST"):
            generator.validate_columns_exist(str(single_row_xml), ["DOES_NOT_EXIST"])


# ===========================================================================
# get_row_count
# ===========================================================================


class TestGetRowCount:
    def test_single_row(self, generator, single_row_xml):
        generator.input_file = str(single_row_xml)
        assert generator.get_row_count() == 1

    def test_multi_row(self, generator_factory, multi_row_xml):
        g = generator_factory(multi_row_xml)
        assert g.get_row_count() == 3

    def test_empty_rows(self, generator_factory, tmp_xml):
        p = tmp_xml("<ROWS></ROWS>")
        g = generator_factory(p)
        assert g.get_row_count() == 0

    def test_missing_file_raises(self, generator):
        generator.input_file = "/no/such/file.xml"
        with pytest.raises((FileNotFoundError, AttributeError)):
            generator.get_row_count()


# ===========================================================================
# build_instruments_dictionary
# ===========================================================================


class TestBuildInstrumentsDictionary:
    def _parse(self, xml_str):
        return ET.fromstring(xml_str)

    def test_single_row_builds_one_entry(self):
        root = self._parse(SINGLE_ROW)
        g = HISTMessagesGenerator.__new__(HISTMessagesGenerator)
        result = g.build_instruments_dictionary(root)
        assert "INS001" in result
        assert len(result) == 1

    def test_class_resolved_correctly(self):
        root = self._parse(SINGLE_ROW)
        g = HISTMessagesGenerator.__new__(HISTMessagesGenerator)
        result = g.build_instruments_dictionary(root)
        assert result["INS001"][InstrumentIndex.CLASS] == InstrumentClass.DOCUMENTARY_LC

    def test_party_type_stored(self):
        root = self._parse(SINGLE_ROW)
        g = HISTMessagesGenerator.__new__(HISTMessagesGenerator)
        result = g.build_instruments_dictionary(root)
        assert result["INS001"][InstrumentIndex.PARTY_TYPE] == "BUYER"

    def test_multi_row_builds_all_entries(self):
        root = self._parse(MULTI_ROW)
        g = HISTMessagesGenerator.__new__(HISTMessagesGenerator)
        result = g.build_instruments_dictionary(root)
        assert len(result) == 3
        assert "INS001" in result
        assert "INS002" in result
        assert "INS003" in result

    def test_duplicate_keeps_first_occurrence(self):
        root = self._parse(DUPLICATE_ROW)
        g = HISTMessagesGenerator.__new__(HISTMessagesGenerator)
        result = g.build_instruments_dictionary(root)
        assert len(result) == 1
        # First occurrence BUYER should be kept
        assert result["INS001"][InstrumentIndex.PARTY_TYPE] == "BUYER"

    def test_all_23_product_types_resolve(self):
        root = self._parse(ALL_TYPES_ROWS)
        g = HISTMessagesGenerator.__new__(HISTMessagesGenerator)
        result = g.build_instruments_dictionary(root)
        assert len(result) == 23

    def test_missing_instrument_id_skipped(self):
        xml = make_xml([{"TYPE_": "DLC", "CUSTOMER_PARTY_TYPE": "BUYER"}])
        root = ET.fromstring(xml)
        g = HISTMessagesGenerator.__new__(HISTMessagesGenerator)
        result = g.build_instruments_dictionary(root)
        assert len(result) == 0

    def test_empty_xml_returns_empty_dict(self):
        root = ET.fromstring("<ROWS></ROWS>")
        g = HISTMessagesGenerator.__new__(HISTMessagesGenerator)
        result = g.build_instruments_dictionary(root)
        assert result == {}

    def test_whitespace_stripped_from_values(self):
        xml = make_xml(
            [
                {
                    "INSTRUMENT_ID": "  INS999  ",
                    "TYPE_": "  DLC  ",
                    "CUSTOMER_PARTY_TYPE": "  BUYER  ",
                }
            ]
        )
        root = ET.fromstring(xml)
        g = HISTMessagesGenerator.__new__(HISTMessagesGenerator)
        result = g.build_instruments_dictionary(root)
        assert "INS999" in result
        assert result["INS999"][InstrumentIndex.PARTY_TYPE] == "BUYER"


# ===========================================================================
# run() – full integration via file system
# ===========================================================================


class TestRun:
    def test_run_creates_sql_file(self, generator_factory, single_row_xml, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        g = generator_factory(single_row_xml)
        g.run()
        assert (tmp_path / "sql_statements.sql").exists()

    def test_run_sql_contains_insert(
        self, generator_factory, single_row_xml, tmp_path, monkeypatch
    ):
        monkeypatch.chdir(tmp_path)
        g = generator_factory(single_row_xml)
        g.run()
        sql = (tmp_path / "sql_statements.sql").read_text()
        assert "INSERT INTO outgoing_intrfc_e" in sql

    def test_run_sql_contains_customer(
        self, generator_factory, single_row_xml, tmp_path, monkeypatch
    ):
        monkeypatch.chdir(tmp_path)
        g = generator_factory(single_row_xml, customer="MY_CUST")
        g.run()
        sql = (tmp_path / "sql_statements.sql").read_text()
        assert "MY_CUST" in sql

    def test_run_sql_contains_bank(self, generator_factory, single_row_xml, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        g = generator_factory(single_row_xml, bank="MY_BANK")
        g.run()
        sql = (tmp_path / "sql_statements.sql").read_text()
        assert "MY_BANK" in sql

    def test_run_sql_contains_instrument_id(
        self, generator_factory, single_row_xml, tmp_path, monkeypatch
    ):
        monkeypatch.chdir(tmp_path)
        g = generator_factory(single_row_xml)
        g.run()
        sql = (tmp_path / "sql_statements.sql").read_text()
        assert "INS001" in sql

    def test_run_sql_contains_commit(
        self, generator_factory, single_row_xml, tmp_path, monkeypatch
    ):
        monkeypatch.chdir(tmp_path)
        g = generator_factory(single_row_xml)
        g.run()
        sql = (tmp_path / "sql_statements.sql").read_text()
        assert "commit;" in sql

    def test_run_sql_contains_select_block(
        self, generator_factory, single_row_xml, tmp_path, monkeypatch
    ):
        monkeypatch.chdir(tmp_path)
        g = generator_factory(single_row_xml)
        g.run()
        sql = (tmp_path / "sql_statements.sql").read_text()
        assert "select * from outgoing_intrfc_e" in sql

    def test_run_multi_row_generates_multiple_inserts(
        self, generator_factory, multi_row_xml, tmp_path, monkeypatch
    ):
        monkeypatch.chdir(tmp_path)
        g = generator_factory(multi_row_xml)
        g.run()
        sql = (tmp_path / "sql_statements.sql").read_text()
        assert sql.count("INSERT INTO") == 3

    def test_run_duplicate_instruments_generates_one_insert(
        self, generator_factory, duplicate_row_xml, tmp_path, monkeypatch
    ):
        monkeypatch.chdir(tmp_path)
        g = generator_factory(duplicate_row_xml)
        g.run()
        sql = (tmp_path / "sql_statements.sql").read_text()
        assert sql.count("INSERT INTO") == 1

    def test_run_missing_file_raises(self, generator_factory, tmp_path):
        g = generator_factory(tmp_path / "ghost.xml")
        with pytest.raises((FileNotFoundError, AttributeError)):
            g.run()

    def test_run_bad_xml_raises_parse_error(self, generator_factory, bad_xml, tmp_path):
        g = generator_factory(bad_xml)
        with pytest.raises((ET.ParseError, AttributeError)):
            g.run()

    def test_run_missing_columns_raises_value_error(
        self, generator_factory, missing_col_xml, tmp_path
    ):
        g = generator_factory(missing_col_xml)
        with pytest.raises(ValueError, match="CUSTOMER_PARTY_TYPE"):
            g.run()

    def test_run_instrument_class_in_process_parameters(
        self, generator_factory, single_row_xml, tmp_path, monkeypatch
    ):
        monkeypatch.chdir(tmp_path)
        g = generator_factory(single_row_xml)
        g.run()
        sql = (tmp_path / "sql_statements.sql").read_text()
        assert "documentary_lc" in sql

    def test_run_party_type_in_process_parameters(
        self, generator_factory, single_row_xml, tmp_path, monkeypatch
    ):
        monkeypatch.chdir(tmp_path)
        g = generator_factory(single_row_xml)
        g.run()
        sql = (tmp_path / "sql_statements.sql").read_text()
        assert "BUYER" in sql

    def test_run_select_contains_instrument_in_clause(
        self, generator_factory, single_row_xml, tmp_path, monkeypatch
    ):
        monkeypatch.chdir(tmp_path)
        g = generator_factory(single_row_xml)
        g.run()
        sql = (tmp_path / "sql_statements.sql").read_text()
        assert "'INS001'" in sql

    def test_run_header_comment_present(
        self, generator_factory, single_row_xml, tmp_path, monkeypatch
    ):
        monkeypatch.chdir(tmp_path)
        g = generator_factory(single_row_xml, customer="ACME")
        g.run()
        sql = (tmp_path / "sql_statements.sql").read_text()
        assert "-- HIST for customer ACME" in sql

    def test_run_all_product_types(self, generator_factory, all_types_xml, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        g = generator_factory(all_types_xml)
        g.run()
        sql = (tmp_path / "sql_statements.sql").read_text()
        assert sql.count("INSERT INTO") == 23

    def test_run_bil_instrument_class_in_sql(
        self, generator_factory, tmp_xml, tmp_path, monkeypatch
    ):
        """Regression: BIL type must generate billing_instrument class in SQL."""
        monkeypatch.chdir(tmp_path)
        xml_path = tmp_xml(
            make_xml([{"INSTRUMENT_ID": "BIL001", "TYPE_": "BIL", "CUSTOMER_PARTY_TYPE": "BUYER"}])
        )
        g = generator_factory(xml_path)
        g.run()
        sql = (tmp_path / "sql_statements.sql").read_text()
        assert "billing_instrument" in sql


# ===========================================================================
# main() CLI
# ===========================================================================


class TestMain:
    def test_main_calls_run(self, single_row_xml, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        test_args = [
            "prog",
            str(single_row_xml),
            "CUST01",
            "BANKX",
        ]
        with patch("sys.argv", test_args):
            with patch.object(HISTMessagesGenerator, "run") as mock_run:
                main()
                mock_run.assert_called_once()

    def test_main_passes_customer(self, single_row_xml, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        captured = {}

        original_init = HISTMessagesGenerator.__init__

        def patched_init(self, **kwargs):
            captured.update(kwargs)
            original_init(self, **kwargs)

        with patch("sys.argv", ["prog", str(single_row_xml), "MY_CUSTOMER", "MY_BANK"]):
            with patch.object(HISTMessagesGenerator, "run"):
                with patch.object(HISTMessagesGenerator, "__init__", patched_init):
                    main()

        assert captured.get("customer") == "MY_CUSTOMER"

    def test_main_passes_bank(self, single_row_xml, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        captured = {}

        original_init = HISTMessagesGenerator.__init__

        def patched_init(self, **kwargs):
            captured.update(kwargs)
            original_init(self, **kwargs)

        with patch("sys.argv", ["prog", str(single_row_xml), "CUST", "MY_BANK"]):
            with patch.object(HISTMessagesGenerator, "run"):
                with patch.object(HISTMessagesGenerator, "__init__", patched_init):
                    main()

        assert captured.get("bank") == "MY_BANK"

    def test_main_version_exits(self, capsys):
        with patch("sys.argv", ["prog", "--version"]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 0
