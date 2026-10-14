"""Guard: a module in cli/ must never share its name with a standard-library module.

`python cli/<script>.py` puts cli/ at sys.path[0]. A `cli/inspect.py` therefore SHADOWED the stdlib `inspect`, and the next stdlib import that needs it
(`dataclasses` on Python >= 3.12) died with `module 'inspect' has no attribute 'get_annotations'`. Measured 11/10/2026: every `python cli/*.py` crashed on
the server's Python 3.12.3 and on Python 3.14; the CI's 3.11 happened not to import it, so CI never saw it.
"""

from __future__ import annotations

import ast
import re
import subprocess
import sys
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_CLI = _ROOT / "cli"


def _is_entry_point(path: Path) -> bool:
    """True when the module has an `if __name__ == "__main__":` guard, i.e. it is meant to be run, not imported."""
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        t = node.test if isinstance(node, ast.If) else None
        if (
            isinstance(t, ast.Compare)
            and isinstance(t.left, ast.Name) and t.left.id == "__name__"
            and len(t.ops) == 1 and isinstance(t.ops[0], ast.Eq)
            and len(t.comparators) == 1 and isinstance(t.comparators[0], ast.Constant) and t.comparators[0].value == "__main__"
        ):
            return True
    return False


def _entry_points() -> list[Path]:
    return [p for p in sorted(_CLI.glob("*.py")) if p.name != "__init__.py" and _is_entry_point(p)]


class TestCliModuleNames(unittest.TestCase):
    def test_no_cli_module_shadows_the_standard_library(self) -> None:
        shadowing = sorted(p.name for p in _CLI.glob("*.py") if p.stem in sys.stdlib_module_names)
        self.assertEqual(shadowing, [], f"cli/ modules shadow the standard library: {shadowing}")

    def test_cli_scripts_start_on_this_interpreter(self) -> None:
        """Every ENTRY POINT in cli/ must at least print its help when run the way the launcher runs it (script path, cli/ first on sys.path).

        Only modules with a `__main__` guard are launched. cli/output_contract.py is a library imported by eight of the scripts (`from output_contract import ...`); it has no
        `__main__`, no argparse, and ./atp never runs it. Launching it bare failed with `No module named 'core'` — it has no sys.path shim because it never needed one, since its
        importers carry theirs. That made `python3 -m pytest` red while `make test` (which exports PYTHONPATH=.) stayed green (KD-ATP-003, found 14/10/2026).
        """
        failures = []
        for script in _entry_points():
            r = subprocess.run([sys.executable, str(script), "-h"], capture_output=True, text=True, cwd=_ROOT, timeout=60)
            if r.returncode != 0:
                failures.append((script.name, r.stderr.strip().splitlines()[-1:] or r.stdout.strip().splitlines()[-1:]))
        self.assertEqual(failures, [])

    def test_every_script_the_launcher_runs_is_an_entry_point(self) -> None:
        """Ties the entry-point classification to ground truth: if ./atp runs cli/x.py but x.py lost its `__main__` guard, the launch test above would silently stop covering it."""
        launched = sorted(set(re.findall(r"cli/([A-Za-z0-9_]+)\.py", (_ROOT / "atp").read_text(encoding="utf-8"))))
        self.assertGreaterEqual(len(launched), 8, f"could not read the scripts ./atp launches: {launched}")
        entry_names = {p.stem for p in _entry_points()}
        self.assertEqual([n for n in launched if n not in entry_names], [], "./atp launches a cli/ module that is not an entry point (no __main__ guard)")


if __name__ == "__main__":
    unittest.main()
