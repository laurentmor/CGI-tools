# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

"""
Shared XML builders and string constants used across the test suite.

Imported directly by test modules as:
    from tests.fixtures import make_xml, SINGLE_ROW, ...

This module contains NO pytest fixtures (those live in conftest.py).
"""

from __future__ import annotations


def make_xml(rows: list[dict[str, str]]) -> str:
    """Build a minimal <ROWS> XML string from a list of column dicts."""
    parts = ["<ROWS>"]
    for row in rows:
        parts.append("  <ROW>")
        for name, value in row.items():
            parts.append(f'    <COLUMN NAME="{name}">{value}</COLUMN>')
        parts.append("  </ROW>")
    parts.append("</ROWS>")
    return "\n".join(parts)


SINGLE_ROW = make_xml([{"INSTRUMENT_ID": "INS001", "TYPE_": "DLC", "CUSTOMER_PARTY_TYPE": "BUYER"}])

MULTI_ROW = make_xml(
    [
        {"INSTRUMENT_ID": "INS001", "TYPE_": "DLC", "CUSTOMER_PARTY_TYPE": "BUYER"},
        {"INSTRUMENT_ID": "INS002", "TYPE_": "SLC", "CUSTOMER_PARTY_TYPE": "SELLER"},
        {"INSTRUMENT_ID": "INS003", "TYPE_": "GUA", "CUSTOMER_PARTY_TYPE": "BUYER"},
    ]
)

DUPLICATE_ROW = make_xml(
    [
        {"INSTRUMENT_ID": "INS001", "TYPE_": "DLC", "CUSTOMER_PARTY_TYPE": "BUYER"},
        {"INSTRUMENT_ID": "INS001", "TYPE_": "DLC", "CUSTOMER_PARTY_TYPE": "SELLER"},
    ]
)

ALL_TYPES_ROWS = make_xml(
    [
        {"INSTRUMENT_ID": f"INS{i:03d}", "TYPE_": t, "CUSTOMER_PARTY_TYPE": "BUYER"}
        for i, t in enumerate(
            [
                "DLC",
                "SLC",
                "CAR",
                "RMB",
                "DBA",
                "CBA",
                "RBA",
                "DFP",
                "ADV",
                "LOI",
                "DCO",
                "DIR",
                "TAC",
                "GUA",
                "PBD",
                "PBS",
                "SBS",
                "FIN",
                "ATP",
                "OAP",
                "RPM",
                "SRM",
                "BIL",
            ],
            start=1,
        )
    ]
)

MISSING_COLUMNS_ROW = make_xml(
    [{"INSTRUMENT_ID": "INS001", "TYPE_": "DLC"}]  # Missing CUSTOMER_PARTY_TYPE
)

LARGE_XML = make_xml(
    [
        {
            "INSTRUMENT_ID": f"INS{i:05d}",
            "TYPE_": "DLC",
            "CUSTOMER_PARTY_TYPE": "BUYER",
        }
        for i in range(1, 1001)
    ]
)
