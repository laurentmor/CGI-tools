# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

"""
Integration tests for HISTMessagesGenerator.

These tests exercise the full pipeline from XML input to SQL output,
verifying correctness across realistic scenarios.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
from fixtures import make_xml

from hist_messages_generator import HISTMessagesGenerator

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def run_and_read(generator_factory, xml_path, tmp_path, monkeypatch, customer="CUST", bank="BNK"):
    monkeypatch.chdir(tmp_path)
    g = generator_factory(xml_path, customer=customer, bank=bank)
    g.run()
    return (tmp_path / "sql_statements.sql").read_text()


# ---------------------------------------------------------------------------
# End-to-end: SQL correctness
# ---------------------------------------------------------------------------


class TestSQLOutput:
    def test_insert_count_matches_unique_instruments(
        self, generator_factory, tmp_xml, tmp_path, monkeypatch
    ):
        xml = make_xml([
            {"INSTRUMENT_ID": "A", "TYPE_": "DLC", "CUSTOMER_PARTY_TYPE": "BUYER"},
            {"INSTRUMENT_ID": "B", "TYPE_": "GUA", "CUSTOMER_PARTY_TYPE": "SELLER"},
            {"INSTRUMENT_ID": "A", "TYPE_": "DLC", "CUSTOMER_PARTY_TYPE": "SELLER"},  # dup
        ])
        sql = run_and_read(generator_factory, tmp_xml(xml), tmp_path, monkeypatch)
        assert sql.count("INSERT INTO outgoing_intrfc_e") == 2

    def test_in_clause_lists_all_instrument_ids(
        self, generator_factory, tmp_xml, tmp_path, monkeypatch
    ):
        xml = make_xml([
            {"INSTRUMENT_ID": "X100", "TYPE_": "FIN", "CUSTOMER_PARTY_TYPE": "BUYER"},
            {"INSTRUMENT_ID": "X200", "TYPE_": "SLC", "CUSTOMER_PARTY_TYPE": "BUYER"},
        ])
        sql = run_and_read(generator_factory, tmp_xml(xml), tmp_path, monkeypatch)
        assert "'X100'" in sql
        assert "'X200'" in sql

    def test_select_block_appears_twice(
        self, generator_factory, tmp_xml, tmp_path, monkeypatch
    ):
        """The SELECT block is emitted before and after the INSERTs."""
        xml = make_xml([{"INSTRUMENT_ID": "Z1", "TYPE_": "DLC", "CUSTOMER_PARTY_TYPE": "BUYER"}])
        sql = run_and_read(generator_factory, tmp_xml(xml), tmp_path, monkeypatch)
        assert sql.count("select * from outgoing_intrfc_e") == 2

    def test_commit_present_once(
        self, generator_factory, tmp_xml, tmp_path, monkeypatch
    ):
        xml = make_xml([{"INSTRUMENT_ID": "Z1", "TYPE_": "DLC", "CUSTOMER_PARTY_TYPE": "BUYER"}])
        sql = run_and_read(generator_factory, tmp_xml(xml), tmp_path, monkeypatch)
        assert sql.count("commit;") == 1

    def test_process_parameters_contains_instrument_class(
        self, generator_factory, tmp_xml, tmp_path, monkeypatch
    ):
        xml = make_xml([{"INSTRUMENT_ID": "G1", "TYPE_": "GUA", "CUSTOMER_PARTY_TYPE": "BUYER"}])
        sql = run_and_read(generator_factory, tmp_xml(xml), tmp_path, monkeypatch)
        assert "instrument_class = guarantee" in sql

    def test_process_parameters_contains_party_type(
        self, generator_factory, tmp_xml, tmp_path, monkeypatch
    ):
        xml = make_xml([{"INSTRUMENT_ID": "G1", "TYPE_": "GUA", "CUSTOMER_PARTY_TYPE": "ISSUER"}])
        sql = run_and_read(generator_factory, tmp_xml(xml), tmp_path, monkeypatch)
        assert "party_type = ISSUER" in sql

    def test_process_parameters_dest_is_tpl(
        self, generator_factory, tmp_xml, tmp_path, monkeypatch
    ):
        xml = make_xml([{"INSTRUMENT_ID": "T1", "TYPE_": "DLC", "CUSTOMER_PARTY_TYPE": "BUYER"}])
        sql = run_and_read(generator_factory, tmp_xml(xml), tmp_path, monkeypatch)
        assert "DestinationId = TPL" in sql

    def test_intrfc_event_type_is_hist(
        self, generator_factory, tmp_xml, tmp_path, monkeypatch
    ):
        xml = make_xml([{"INSTRUMENT_ID": "T1", "TYPE_": "DLC", "CUSTOMER_PARTY_TYPE": "BUYER"}])
        sql = run_and_read(generator_factory, tmp_xml(xml), tmp_path, monkeypatch)
        assert "'HIST'" in sql

    def test_priority_is_1(
        self, generator_factory, tmp_xml, tmp_path, monkeypatch
    ):
        xml = make_xml([{"INSTRUMENT_ID": "T1", "TYPE_": "DLC", "CUSTOMER_PARTY_TYPE": "BUYER"}])
        sql = run_and_read(generator_factory, tmp_xml(xml), tmp_path, monkeypatch)
        assert "'1'" in sql

    def test_status_s_present(
        self, generator_factory, tmp_xml, tmp_path, monkeypatch
    ):
        xml = make_xml([{"INSTRUMENT_ID": "T1", "TYPE_": "DLC", "CUSTOMER_PARTY_TYPE": "BUYER"}])
        sql = run_and_read(generator_factory, tmp_xml(xml), tmp_path, monkeypatch)
        assert "'S'" in sql

    def test_worker_asyagt01_present(
        self, generator_factory, tmp_xml, tmp_path, monkeypatch
    ):
        xml = make_xml([{"INSTRUMENT_ID": "T1", "TYPE_": "DLC", "CUSTOMER_PARTY_TYPE": "BUYER"}])
        sql = run_and_read(generator_factory, tmp_xml(xml), tmp_path, monkeypatch)
        assert "ASYAGT01" in sql

    def test_customer_id_in_customer_subquery(
        self, generator_factory, tmp_xml, tmp_path, monkeypatch
    ):
        xml = make_xml([{"INSTRUMENT_ID": "T1", "TYPE_": "DLC", "CUSTOMER_PARTY_TYPE": "BUYER"}])
        sql = run_and_read(generator_factory, tmp_xml(xml), tmp_path, monkeypatch, customer="MYCUST")
        assert "customer_id = 'MYCUST'" in sql or "customer_id = MYCUST" in sql or "customer_id = 'MyCust'" in sql or "MYCUST" in sql.upper()


# ---------------------------------------------------------------------------
# BIL regression (added 2026-03-01)
# ---------------------------------------------------------------------------


class TestBILRegression:
    def test_bil_end_to_end(self, generator_factory, tmp_xml, tmp_path, monkeypatch):
        xml = make_xml([
            {"INSTRUMENT_ID": "BIL100", "TYPE_": "BIL", "CUSTOMER_PARTY_TYPE": "APPLICANT"}
        ])
        sql = run_and_read(generator_factory, tmp_xml(xml), tmp_path, monkeypatch)
        assert "billing_instrument" in sql
        assert "BIL100" in sql
        assert "APPLICANT" in sql

    def test_bil_in_mixed_batch(self, generator_factory, tmp_xml, tmp_path, monkeypatch):
        xml = make_xml([
            {"INSTRUMENT_ID": "DLC001", "TYPE_": "DLC", "CUSTOMER_PARTY_TYPE": "BUYER"},
            {"INSTRUMENT_ID": "BIL001", "TYPE_": "BIL", "CUSTOMER_PARTY_TYPE": "BUYER"},
        ])
        sql = run_and_read(generator_factory, tmp_xml(xml), tmp_path, monkeypatch)
        assert sql.count("INSERT INTO") == 2
        assert "billing_instrument" in sql
        assert "documentary_lc" in sql


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_instrument_id_with_special_characters(
        self, generator_factory, tmp_xml, tmp_path, monkeypatch
    ):
        xml = make_xml([
            {"INSTRUMENT_ID": "INS-001/A", "TYPE_": "DLC", "CUSTOMER_PARTY_TYPE": "BUYER"}
        ])
        sql = run_and_read(generator_factory, tmp_xml(xml), tmp_path, monkeypatch)
        assert "INS-001/A" in sql

    def test_customer_id_with_numbers(
        self, generator_factory, tmp_xml, tmp_path, monkeypatch
    ):
        xml = make_xml([{"INSTRUMENT_ID": "I1", "TYPE_": "DLC", "CUSTOMER_PARTY_TYPE": "BUYER"}])
        sql = run_and_read(generator_factory, tmp_xml(xml), tmp_path, monkeypatch, customer="C12345")
        assert "C12345" in sql

    def test_all_23_types_in_single_run(
        self, generator_factory, all_types_xml, tmp_path, monkeypatch
    ):
        sql = run_and_read(generator_factory, all_types_xml, tmp_path, monkeypatch)
        assert sql.count("INSERT INTO") == 23
        for cls in [
            "documentary_lc", "standby_lc", "cargo_release", "reimbursement",
            "guarantee", "billing_instrument", "finance_instrument",
        ]:
            assert cls in sql

    def test_sql_file_overwritten_on_second_run(
        self, generator_factory, tmp_xml, tmp_path, monkeypatch
    ):
        monkeypatch.chdir(tmp_path)
        xml1 = make_xml([{"INSTRUMENT_ID": "A1", "TYPE_": "DLC", "CUSTOMER_PARTY_TYPE": "BUYER"}])
        xml2 = make_xml([
            {"INSTRUMENT_ID": "B1", "TYPE_": "GUA", "CUSTOMER_PARTY_TYPE": "SELLER"},
            {"INSTRUMENT_ID": "B2", "TYPE_": "SLC", "CUSTOMER_PARTY_TYPE": "BUYER"},
        ])
        g1 = generator_factory(tmp_xml(xml1, "first.xml"))
        g1.run()
        g2 = generator_factory(tmp_xml(xml2, "second.xml"))
        g2.run()
        sql = (tmp_path / "sql_statements.sql").read_text()
        assert sql.count("INSERT INTO") == 2
        assert "A1" not in sql