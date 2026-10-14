"""Guard: README.md and AGENTS.md must list exactly the routes bridge/bridge_server.py serves, and must not carry a hand-counted "N endpoints".

Both files said "12 endpoints incl. ...". That figure is ambiguous (12 distinct paths, but 13 method+path pairs: /runs/<id> serves GET and DELETE) and nothing kept it in step with the
code. Listing the routes and checking the list against the code is verifiable; a count is not (KD-ATP-011, 14/10/2026). The routes are read from the server's own `do_GET` / `do_POST` / `do_DELETE` with `ast`, not with a regex: a regex
pass done by hand on 14/10/2026 missed the `startswith` branches and the `!=` guard on /run and returned 10 instead of 13.
"""

from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_MANAGED = "AI_OS:BEGIN MANAGED BLOCK"


def _is_self_path(node: ast.AST) -> bool:
    return isinstance(node, ast.Attribute) and node.attr == "path" and isinstance(node.value, ast.Name) and node.value.id == "self"


def bridge_routes() -> set[tuple[str, str]]:
    """(METHOD, path) for every route in bridge_server.py. A `startswith("/runs/")` branch is the parameterised route "/runs/<id>"."""
    tree = ast.parse((_ROOT / "bridge" / "bridge_server.py").read_text(encoding="utf-8"))
    routes: set[tuple[str, str]] = set()
    for fn in (n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name in ("do_GET", "do_POST", "do_DELETE")):
        method = fn.name[3:]
        for n in ast.walk(fn):
            if isinstance(n, ast.Compare) and _is_self_path(n.left) and len(n.comparators) == 1:
                c = n.comparators[0]
                if isinstance(c, ast.Constant) and isinstance(c.value, str) and isinstance(n.ops[0], (ast.Eq, ast.NotEq)):
                    routes.add((method, c.value))
            elif isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "startswith" and _is_self_path(n.func.value):
                if n.args and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str):
                    routes.add((method, n.args[0].value + "<id>"))
    return routes


def _bridge_bullet(doc: str) -> str:
    """The hand-written `- **Bridge server...` line (before the generated managed block, which describes the bridge in its own words)."""
    hand_written = doc.split(_MANAGED, 1)[0]
    m = re.search(r"^- \*\*Bridge server[^\n]*$", hand_written, re.M)
    assert m, "no '- **Bridge server' bullet in the hand-written part"
    return m.group(0)


def _documented_paths(bullet: str) -> set[str]:
    return set(re.findall(r"(?<![\w.:])/(?:[A-Za-z0-9_<>\-]+(?:/[A-Za-z0-9_<>\-]+)*)?", bullet))


class TestBridgeRoutesDocumented(unittest.TestCase):
    def test_route_reader_finds_the_routes_it_must_find(self) -> None:
        """Guards the reader itself: if it stops seeing these, the comparison below would pass vacuously."""
        routes = bridge_routes()
        for must in (("POST", "/run"), ("POST", "/run/stream"), ("GET", "/health"), ("GET", "/"), ("GET", "/runs/<id>"), ("DELETE", "/runs/<id>")):
            self.assertIn(must, routes)

    def test_docs_list_exactly_the_served_paths(self) -> None:
        served = {path for _method, path in bridge_routes()}
        for name in ("README.md", "AGENTS.md"):
            documented = _documented_paths(_bridge_bullet((_ROOT / name).read_text(encoding="utf-8")))
            self.assertEqual(documented - served, set(), f"{name} documents routes the bridge does not serve")
            self.assertEqual(served - documented, set(), f"{name} omits routes the bridge serves")

    def test_docs_do_not_hand_count_bridge_endpoints(self) -> None:
        for name in ("README.md", "AGENTS.md"):
            bullet = _bridge_bullet((_ROOT / name).read_text(encoding="utf-8"))
            self.assertIsNone(re.search(r"\b\d+\s+endpoints?\b", bullet, re.I), f"{name}: the Bridge server bullet carries a hand-counted number")


if __name__ == "__main__":
    unittest.main()
