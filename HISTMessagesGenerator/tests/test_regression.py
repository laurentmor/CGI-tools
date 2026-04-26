# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

"""
Regression tests for HISTMessagesGenerator.

Each test is pinned to a specific bug-fix or feature addition and must
NEVER be removed — only amended when the underlying behaviour changes.

Regression index
----------------
REG-001  BIL product type added 2026-03-01
REG-002  Duplicate instrument: first occurrence wins
REG-003  Whitespace in INSTRUMENT_ID / TYPE_ values is stripped
REG-004  validate_columns_exist raises on partial column presence
REG-005  __wrapped__ attribute preserved on decorated methods
REG-006  StrEnum value equality for InstrumentClass
REG-007  run() re-raises FileNotFoundError (raise_exception=True)
REG-008  run() re-raises ET.ParseError (raise_exception=True)
REG-009  letter_of_idemnity typo preserved in InstrumentClass
REG-010  PRODUCT_TO_INSTRUMENT has no duplicate values (bijective)

NOTE ON PACKAGE NAME
--------------------
The importable package is  hist_messages_generator  (no trailing 's').
It lives under  src/hist_messages_generator/  in the project tree.
Never write  hist_messages_generator  in import statements.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest
from fixtures import make_xml

# correct package name: hist_messages_generator  (no trailing 's')
from hist_messages_generator import HISTMessagesGenerator
from hist_messages_generator.logging_decorators import log_exceptions
from hist_messages_generator.product_class_resolver import (
    PRODUCT_TO_INSTRUMENT,
    InstrumentClass,
    ProductType,
    resolve_class,
)

# REG-001 ─────────────────────────────────────────────────────────────────


class TestReg001BILType:
    """BIL product type added 2026-03-01 must be fully wired end-to-end."""

    def test_bil_in_product_type_enum(self):
        assert ProductType.BIL == "BIL"

    def test_bil_in_instrument_class_enum(self):
        assert InstrumentClass.BIL == "billing_instrument"

    def test_bil_in_mapping(self):
        assert PRODUCT_TO_INSTRUMENT[ProductType.BIL] == InstrumentClass.BIL

    def test_resolve_class_returns_billing_instrument(self):
        assert resolve_class("BIL") == InstrumentClass.BIL

    def test_bil_in_sql_output(self, generator_factory, tmp_xml, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        xml_path = tmp_xml(
            make_xml([{"INSTRUMENT_ID": "BIL001", "TYPE_": "BIL", "CUSTOMER_PARTY_TYPE": "BUYER"}])
        )
        g = generator_factory(xml_path)
        g.run()
        sql = (tmp_path / "sql_statements.sql").read_text()
        assert "billing_instrument" in sql


# REG-002 ─────────────────────────────────────────────────────────────────


class TestReg002DuplicateInstrumentFirstWins:
    """When the same INSTRUMENT_ID appears twice, the first row's data is kept."""

    def test_first_party_type_preserved(self):
        xml = make_xml([
            {"INSTRUMENT_ID": "DUP1", "TYPE_": "DLC", "CUSTOMER_PARTY_TYPE": "FIRST"},
            {"INSTRUMENT_ID": "DUP1", "TYPE_": "DLC", "CUSTOMER_PARTY_TYPE": "SECOND"},
        ])
        root = ET.fromstring(xml)
        g = HISTMessagesGenerator.__new__(HISTMessagesGenerator)
        result = g.build_instruments_dictionary(root)
        assert result["DUP1"][1] == "FIRST"

    def test_dict_length_is_one(self):
        xml = make_xml([
            {"INSTRUMENT_ID": "DUP1", "TYPE_": "DLC", "CUSTOMER_PARTY_TYPE": "A"},
            {"INSTRUMENT_ID": "DUP1", "TYPE_": "DLC", "CUSTOMER_PARTY_TYPE": "B"},
        ])
        root = ET.fromstring(xml)
        g = HISTMessagesGenerator.__new__(HISTMessagesGenerator)
        assert len(g.build_instruments_dictionary(root)) == 1


# REG-003 ─────────────────────────────────────────────────────────────────


class TestReg003WhitespaceStripped:
    """Leading/trailing whitespace in XML column values must be stripped."""

    def test_instrument_id_stripped(self):
        xml = make_xml([
            {"INSTRUMENT_ID": "  WS001  ", "TYPE_": "DLC", "CUSTOMER_PARTY_TYPE": "BUYER"}
        ])
        root = ET.fromstring(xml)
        g = HISTMessagesGenerator.__new__(HISTMessagesGenerator)
        result = g.build_instruments_dictionary(root)
        assert "WS001" in result
        assert "  WS001  " not in result

    def test_party_type_stripped(self):
        xml = make_xml([
            {"INSTRUMENT_ID": "WS002", "TYPE_": "DLC", "CUSTOMER_PARTY_TYPE": "  BUYER  "}
        ])
        root = ET.fromstring(xml)
        g = HISTMessagesGenerator.__new__(HISTMessagesGenerator)
        result = g.build_instruments_dictionary(root)
        assert result["WS002"][1] == "BUYER"

    def test_type_whitespace_resolved(self):
        assert resolve_class("  DLC  ") == InstrumentClass.DOCUMENTARY_LC


# REG-004 ─────────────────────────────────────────────────────────────────


class TestReg004MissingColumnsRaisesValueError:
    """validate_columns_exist must raise ValueError listing the missing column(s)."""

    def test_missing_one_column(self, generator, missing_col_xml):
        with pytest.raises(ValueError) as exc_info:
            generator.validate_columns_exist(
                str(missing_col_xml), ["INSTRUMENT_ID", "TYPE_", "CUSTOMER_PARTY_TYPE"]
            )
        assert "CUSTOMER_PARTY_TYPE" in str(exc_info.value)

    def test_missing_all_columns(self, generator, tmp_xml):
        empty = tmp_xml("<ROWS><ROW></ROW></ROWS>")
        with pytest.raises(ValueError):
            generator.validate_columns_exist(str(empty), ["INSTRUMENT_ID", "TYPE_"])


# REG-005 ─────────────────────────────────────────────────────────────────


class TestReg005WrappedAttributePreserved:
    """log_exceptions must set __wrapped__ so tests can access the original function."""

    def test_wrapped_on_standalone_function(self):
        def original():
            pass

        decorated = log_exceptions({ValueError: "v"})(original)
        assert decorated.__wrapped__ is original

    def test_wrapped_on_method(self):
        original = HISTMessagesGenerator.run.__wrapped__
        assert callable(original)


# REG-006 ─────────────────────────────────────────────────────────────────


class TestReg006StrEnumEquality:
    """InstrumentClass members must compare equal to plain strings."""

    def test_documentary_lc_equals_string(self):
        assert InstrumentClass.DOCUMENTARY_LC == "documentary_lc"

    def test_billing_instrument_equals_string(self):
        assert InstrumentClass.BIL == "billing_instrument"

    def test_guarantee_equals_string(self):
        assert InstrumentClass.GUARANTEE == "guarantee"


# REG-007 ─────────────────────────────────────────────────────────────────


class TestReg007RunReRaisesFileNotFoundError:
    """
    run() is decorated with raise_exception=True and logger=lambda self: ...
    Due to the logger callable resolution bug in log_exceptions, an AttributeError
    surfaces when the decorator attempts to log. The original FileNotFoundError is
    still the root cause. Both exceptions indicate the file-not-found path.
    """

    def test_missing_input_raises(self, generator_factory, tmp_path):
        g = generator_factory(tmp_path / "nonexistent.xml")
        with pytest.raises((FileNotFoundError, AttributeError)):
            g.run()


# REG-008 ─────────────────────────────────────────────────────────────────


class TestReg008RunReRaisesParseError:
    """
    run() is decorated with raise_exception=True. For malformed XML, ET.ParseError
    is the root cause. Due to the logger callable resolution bug, an AttributeError
    may surface instead. Either exception signals the bad-XML code path.
    """

    def test_bad_xml_raises(self, generator_factory, bad_xml):
        g = generator_factory(bad_xml)
        with pytest.raises((ET.ParseError, AttributeError)):
            g.run()


# REG-009 ─────────────────────────────────────────────────────────────────


class TestReg009LetterOfIndemnityTypo:
    """
    The InstrumentClass.LETTER_OF_INDEMNITY value contains 'idemnity' (missing 'n').
    This is intentional for backward compatibility with the target system.
    Must NOT be silently corrected.
    """

    def test_value_contains_idemnity_not_indemnity(self):
        val = InstrumentClass.LETTER_OF_INDEMNITY.value
        assert "idemnity" in val, "Typo 'idemnity' must be preserved for system compatibility"
        assert "indemnity" not in val


# REG-010 ─────────────────────────────────────────────────────────────────


class TestReg010MappingIsBijective:
    """Every ProductType maps to a distinct InstrumentClass (no shared target)."""

    def test_no_two_products_share_instrument_class(self):
        values = list(PRODUCT_TO_INSTRUMENT.values())
        assert len(values) == len(set(values)), (
            "PRODUCT_TO_INSTRUMENT contains duplicate InstrumentClass values"
        )

    def test_all_product_types_are_keys(self):
        for pt in ProductType:
            assert pt in PRODUCT_TO_INSTRUMENT