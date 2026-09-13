#!/usr/bin/env python3
"""DEPRECATED — replaced by .agent/scripts/wireframes/build.py

The v1 generator drew the uncorrected data model (reserve as a ledger type,
rented stock excluded from valuation, no deposit liability). It has been
replaced by a modular generator with a shared component DSL.

    python3 .agent/scripts/wireframes/build.py
"""
import subprocess
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "wireframes" / "build.py"

if __name__ == "__main__":
    print(__doc__)
    print(f"Running {TARGET} …\n")
    sys.exit(subprocess.call([sys.executable, str(TARGET)]))
