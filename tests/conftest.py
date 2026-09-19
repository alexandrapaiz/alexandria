"""Put the repository root on sys.path so tests can import `pipeline` and `mcp`.

Without this, `python3 -m pytest` works (it adds the working directory) and a
bare `pytest tests/` does not. Making both work means a contributor who runs the
obvious command gets a result rather than a collection error.
"""

import sys
from pathlib import Path

ROOT = str(Path(__file__).resolve().parent.parent)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
