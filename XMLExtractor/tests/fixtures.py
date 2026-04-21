import importlib.util as _ilu
import io
import pathlib as _pathlib
import sys
from contextlib import contextmanager
from unittest.mock import patch
from xml.etree import ElementTree as ET

import xml_extractor as xe  # type: ignore

# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

# Now import works reliably

"""
fixtures.py
===========
Shared constants, XML payloads, and helper functions used across all
test modules.
"""


# Now import works reliably


# ---------------------------------------------------------------------------
# Ensure src/ is in PYTHONPATH (CRITICAL FIX)
# ---------------------------------------------------------------------------

ROOT_DIR = _pathlib.Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


# ---------------------------------------------------------------------------
# XML payloads
# ---------------------------------------------------------------------------

SINGLE_ROW_XML = """\
<?xml version='1.0' encoding='UTF8'?>
<RESULTS>
  <ROW>
    <COLUMN NAME="RICH_TEXT_NCLOB"><![CDATA[<Proponix><Header><MessageID>MSG001</MessageID></Header>
    </Proponix>]]></COLUMN>
  </ROW>
</RESULTS>"""

MULTI_ROW_XML = """\
<?xml version='1.0' encoding='UTF8'?>
<RESULTS>
  <ROW>
    <COLUMN NAME="RICH_TEXT_NCLOB"><![CDATA[<Proponix><Header><MessageID>MSG001</MessageID></Header>
    </Proponix>]]></COLUMN>
  </ROW>
  <ROW>
    <COLUMN NAME="RICH_TEXT_NCLOB"><![CDATA[<Proponix><Header><MessageID>MSG002</MessageID>
    </Header></Proponix>]]></COLUMN>
  </ROW>
  <ROW>
    <COLUMN NAME="RICH_TEXT_NCLOB"><![CDATA[<Proponix><Header><MessageID>MSG003</MessageID></Header>
    </Proponix>]]></COLUMN>
  </ROW>
</RESULTS>"""

MISSING_COLUMN_XML = """\
<?xml version='1.0' encoding='UTF8'?>
<RESULTS>
  <ROW>
    <COLUMN NAME="OTHER_COL"><![CDATA[data]]></COLUMN>
  </ROW>
</RESULTS>"""

WRONG_ROOT_XML = """\
<?xml version='1.0' encoding='UTF8'?>
<NOT_RESULTS>
  <ROW/>
</NOT_RESULTS>"""

EMPTY_RESULTS_XML = """\
<?xml version='1.0' encoding='UTF8'?>
<RESULTS/>"""

INVALID_XML = "<<not xml at all>>"

DIRTY_XML_CONTENT = "Hello\x02World\x1aEnd"

REPLACE_MAP = {"*": "-", "\x02": "", "\x1a": ""}

# ---------------------------------------------------------------------------
# Factory helper
# ---------------------------------------------------------------------------


def make_extractor(**overrides):
    defaults = dict(
        input_file="input.xml",
        output_dir="output",
        output_file_name="archive",
        column_name="RICH_TEXT_NCLOB",
        create_zip=False,
        zip_password=None,
        file_id_tag="MessageID",
        mute=True,
        dry_run=False,
    )
    defaults.update(overrides)
    return xe.XMLExtractor(**defaults)


# ---------------------------------------------------------------------------
# iterparse patch helper
# ---------------------------------------------------------------------------


@contextmanager
def patch_iterparse(xml_string: str):
    _real_iterparse = ET.iterparse

    def fake_iterparse(source, events=None):
        return _real_iterparse(
            io.BytesIO(xml_string.encode()),
            events=events or ("end",),
        )

    with patch("xml_extractor.xml_extractor.ET.iterparse", side_effect=fake_iterparse):
        yield


# ---------------------------------------------------------------------------
# Real log_exceptions loader (FIXED)
# ---------------------------------------------------------------------------


def load_real_log_exceptions():
    candidates = [
        ROOT_DIR / "src" / "xml_extractor" / "logging_decorators.py",
        ROOT_DIR / "logging_decorators.py",
    ]

    for path in candidates:
        if path.exists():
            spec = _ilu.spec_from_file_location("_dec_real", str(path))
            mod = _ilu.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod.log_exceptions

    raise FileNotFoundError(
        "logging_decorators.py not found in: " + ", ".join(str(p) for p in candidates)
    )
