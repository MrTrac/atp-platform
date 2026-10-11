"""Guard: every third-party module the code imports must be declared in pyproject.toml (dependencies or an optional extra).

Found 11/10/2026: adapters/claude_code.py, codex.py and cursor.py import `jinja2` but pyproject declared nothing (`dependencies = []`), and the server's venv
has none — those adapters would die with ModuleNotFoundError the first time they render a prompt. Nothing noticed because the unit tests ran on a machine that had jinja2.
"""

from __future__ import annotations

import ast
import re
import sys
import tomllib
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_CODE_DIRS = ("adapters", "bridge", "cli", "core", "generators")
# import name -> distribution name, where they differ
_DIST = {"yaml": "pyyaml"}
# test-only tooling is declared in the `dev` extra and is allowed outside shipped code (tests/ is not scanned)


def _declared() -> set[str]:
    data = tomllib.loads((_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    specs = list(data["project"].get("dependencies", []))
    for extra in data["project"].get("optional-dependencies", {}).values():
        specs.extend(extra)
    return {re.split(r"[<>=!~\[; ]", s, maxsplit=1)[0].lower().replace("_", "-") for s in specs}


def _third_party_imports() -> dict[str, set[str]]:
    local = {p.name for p in _ROOT.iterdir() if p.is_dir() or p.suffix == ".py"} | {p.stem for p in _ROOT.glob("*.py")}
    found: dict[str, set[str]] = {}
    for d in _CODE_DIRS:
        for path in (_ROOT / d).rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                names: list[str] = []
                if isinstance(node, ast.Import):
                    names = [a.name.split(".")[0] for a in node.names]
                elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                    names = [node.module.split(".")[0]]
                for n in names:
                    sibling = (path.parent / f"{n}.py").exists() or (path.parent / n).is_dir()   # script-style `from output_contract import ...`
                    if n in sys.stdlib_module_names or n in local or sibling or n == "__future__":
                        continue
                    found.setdefault(n, set()).add(str(path.relative_to(_ROOT)))
    return found


class TestDeclaredDependencies(unittest.TestCase):
    def test_every_third_party_import_is_declared(self) -> None:
        declared = _declared()
        missing = {
            mod: sorted(files)
            for mod, files in _third_party_imports().items()
            if _DIST.get(mod, mod).lower().replace("_", "-") not in declared
        }
        self.assertEqual(missing, {}, f"imported but not declared in pyproject.toml: {missing}")


if __name__ == "__main__":
    unittest.main()
