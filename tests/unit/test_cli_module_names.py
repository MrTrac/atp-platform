"""Guard: a module in cli/ must never share its name with a standard-library module.

`python cli/<script>.py` puts cli/ at sys.path[0]. A `cli/inspect.py` therefore SHADOWED the stdlib `inspect`, and the next stdlib import that needs it
(`dataclasses` on Python >= 3.12) died with `module 'inspect' has no attribute 'get_annotations'`. Measured 11/10/2026: every `python cli/*.py` crashed on
the server's Python 3.12.3 and on Python 3.14; the CI's 3.11 happened not to import it, so CI never saw it.
"""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_CLI = _ROOT / "cli"


class TestCliModuleNames(unittest.TestCase):
    def test_no_cli_module_shadows_the_standard_library(self) -> None:
        shadowing = sorted(p.name for p in _CLI.glob("*.py") if p.stem in sys.stdlib_module_names)
        self.assertEqual(shadowing, [], f"cli/ modules shadow the standard library: {shadowing}")

    def test_cli_scripts_start_on_this_interpreter(self) -> None:
        """Every script in cli/ must at least print its help when run the way the launcher runs it (script path, cli/ first on sys.path)."""
        failures = []
        for script in sorted(_CLI.glob("*.py")):
            if script.name == "__init__.py":
                continue
            r = subprocess.run([sys.executable, str(script), "-h"], capture_output=True, text=True, cwd=_ROOT, timeout=60)
            if r.returncode != 0:
                failures.append((script.name, r.stderr.strip().splitlines()[-1:] or r.stdout.strip().splitlines()[-1:]))
        self.assertEqual(failures, [])


if __name__ == "__main__":
    unittest.main()
