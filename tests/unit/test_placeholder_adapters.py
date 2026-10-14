"""Guard: a placeholder adapter directory stays a placeholder until someone deliberately changes that (KD-ATP-009).

`adapters/api`, `desktop_bridge`, `local_service` and `ui_bridge` are architectural slots kept on purpose since the v0 skeleton (14/3/2026): each holds a README and an empty `__init__.py`, and
nothing imports them. The decision of 14/10/2026 was to KEEP them (deleting changes the frozen adapter shape) and to make their status explicit. Without a check, "placeholder" is just a word:
someone adds a real module to one of them, the README keeps saying "placeholder", and nobody notices that a documented empty slot now runs code. These tests turn the status into a contract:

  * a placeholder holds no code beyond `__init__.py`, and its README still calls it a placeholder;
  * nothing imports a placeholder (so it cannot be depended on by accident);
  * `adapters/README.md` lists exactly these directories in its status table;
  * a NEW adapter directory that holds no code must be added to that table (no silent new placeholders).

To promote a placeholder to a real adapter, do the three things listed in `adapters/README.md`; these tests stay red until you do.
"""

from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_ADAPTERS = _ROOT / "adapters"
PLACEHOLDERS = ("api", "desktop_bridge", "local_service", "ui_bridge")


def _real_modules(d: Path) -> list[str]:
    return sorted(p.name for p in d.rglob("*.py") if p.name != "__init__.py" and "__pycache__" not in p.parts)


def _imported_adapter_names(tree: ast.AST) -> set[str]:
    """Names X for every `import adapters.X[...]`, `from adapters.X[...] import ...` and `from adapters import X`."""
    found: set[str] = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                parts = a.name.split(".")
                if parts[0] == "adapters" and len(parts) > 1:
                    found.add(parts[1])
        elif isinstance(n, ast.ImportFrom) and n.module:
            parts = n.module.split(".")
            if parts[0] == "adapters":
                if len(parts) > 1:
                    found.add(parts[1])
                else:
                    found.update(a.name for a in n.names)
    return found


def _documented_placeholders() -> set[str]:
    text = (_ADAPTERS / "README.md").read_text(encoding="utf-8")
    section = text.split("## Trạng thái placeholder và stub", 1)
    assert len(section) == 2, "adapters/README.md has no 'Trạng thái placeholder và stub' section"
    return set(re.findall(r"^\| `adapters/([a-z_]+)` \|", section[1], re.M))


class TestPlaceholderAdapters(unittest.TestCase):
    def test_placeholders_hold_no_code(self) -> None:
        for name in PLACEHOLDERS:
            d = _ADAPTERS / name
            self.assertTrue(d.is_dir(), f"adapters/{name} is gone")
            self.assertTrue((d / "README.md").is_file(), f"adapters/{name} has no README.md")
            self.assertEqual(_real_modules(d), [], f"adapters/{name} now holds code but is still listed as a placeholder: promote it (see adapters/README.md)")
            body = ast.parse((d / "__init__.py").read_text(encoding="utf-8")).body
            statements = [n for n in body if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str))]
            self.assertEqual(statements, [], f"adapters/{name}/__init__.py holds more than a docstring")

    def test_each_readme_still_calls_it_a_placeholder(self) -> None:
        for name in PLACEHOLDERS:
            text = (_ADAPTERS / name / "README.md").read_text(encoding="utf-8").lower()
            self.assertIn("placeholder", text, f"adapters/{name}/README.md no longer says it is a placeholder")

    def test_nothing_imports_a_placeholder(self) -> None:
        offenders = []
        for p in sorted(_ROOT.rglob("*.py")):
            rel = p.relative_to(_ROOT)
            if any(part in (".git", ".venv", "__pycache__", "node_modules") for part in rel.parts):
                continue
            if rel.parts[0] == "adapters" and len(rel.parts) > 1 and rel.parts[1] in PLACEHOLDERS:
                continue
            if rel == Path("tests/unit/test_placeholder_adapters.py"):
                continue
            hit = _imported_adapter_names(ast.parse(p.read_text(encoding="utf-8"))) & set(PLACEHOLDERS)
            if hit:
                offenders.append(f"{rel}: {sorted(hit)}")
        self.assertEqual(offenders, [], "a placeholder adapter is imported: it is no longer an unused slot")

    def test_readme_status_table_lists_exactly_the_placeholders(self) -> None:
        self.assertEqual(_documented_placeholders(), set(PLACEHOLDERS), "adapters/README.md status table and PLACEHOLDERS disagree")

    def test_a_new_code_less_adapter_directory_must_be_declared(self) -> None:
        undeclared = []
        for d in sorted(p for p in _ADAPTERS.iterdir() if p.is_dir() and p.name != "__pycache__"):
            if not _real_modules(d) and d.name not in PLACEHOLDERS:
                undeclared.append(d.name)
        self.assertEqual(undeclared, [], "adapter directories with no code that are not declared placeholders (add them to the table in adapters/README.md and to PLACEHOLDERS)")


if __name__ == "__main__":
    unittest.main()
