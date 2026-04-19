# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

import subprocess
from importlib.metadata import PackageNotFoundError, version


def get_version() -> str:
    try:
        return version("xml-extractor")
    except PackageNotFoundError:
        try:
            return subprocess.check_output(["git", "describe", "--tags"], text=True).strip()
        except Exception:
            return "dev"


__version__ = get_version()
