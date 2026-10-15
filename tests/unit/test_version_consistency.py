"""Anti-drift guard (G-VERSTAMP-1 §4).

Every place that carries the platform version or the release timestamp must agree, and RELEASED
is checked against an independent witness (the date of the matching CHANGELOG entry), not merely
"the file exists" — a stale RELEASED still exists.
"""

from __future__ import annotations

import re
import sys
import unittest
from datetime import datetime
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from bridge.bridge_server import SERVER_VERSION, _build_health_response  # noqa: E402
from core import version as core_version  # noqa: E402

_ISO_WITH_TZ = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})$")


def _read(name: str) -> str:
    return (_ROOT / name).read_text(encoding="utf-8")


class TestVersionConsistency(unittest.TestCase):
    def setUp(self) -> None:
        self.version = _read("VERSION").strip()
        self.released = _read("RELEASED").strip()

    def test_pyproject_matches_version_file(self) -> None:
        m = re.search(r'^version\s*=\s*"([^"]+)"', _read("pyproject.toml"), re.M)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), self.version)

    def test_core_version_constant_matches_version_file(self) -> None:
        self.assertEqual(core_version.VERSION, self.version)

    def test_released_is_iso8601_with_timezone(self) -> None:
        self.assertRegex(self.released, _ISO_WITH_TZ)
        datetime.fromisoformat(self.released)  # raises if not a real timestamp

    def test_core_released_constant_matches_released_file(self) -> None:
        self.assertEqual(core_version.RELEASED, self.released)

    def test_released_date_equals_changelog_entry_date(self) -> None:
        esc = re.escape(self.version)
        m = re.search(rf"^## \[{esc}\] — (\d{{4}}-\d{{2}}-\d{{2}})", _read("CHANGELOG.md"), re.M)
        self.assertIsNotNone(m, f'no "## [{self.version}] — YYYY-MM-DD" entry in CHANGELOG.md')
        self.assertEqual(self.released[:10], m.group(1))


# Hand-written lines that name the CURRENT version (KD-ATP-024). Nothing generates them, so before this
# guard 2.7.1 shipped with AGENTS.md still saying v2.7.0 and every other check stayed green. Each entry is
# (file, what the line is, a pattern with ONE capture group = the version it names). The managed block
# between the AI_OS markers is not listed: `aios sync` regenerates it from the pack.
_HAND_WRITTEN_VERSION_LINES = (
    ("README.md", "baseline sentence", r"governance-first platform tại baseline \*\*v(\d+\.\d+\.\d+)\*\*"),
    ("README.md", "'current released baseline' bullet", r"^- \*\*`v(\d+\.\d+\.\d+)`\*\* — \*\*current released baseline\*\*"),
    ("README.md", "runtime components heading", r"^Runtime components \(v(\d+\.\d+\.\d+)\):"),
    ("AGENTS.md", "baseline sentence", r"governance-first platform at v(\d+\.\d+\.\d+) baseline"),
    ("AGENTS.md", "runtime components heading", r"^Current runtime components \(v(\d+\.\d+\.\d+)\):"),
)


class TestHandWrittenVersionLines(unittest.TestCase):
    """The docs a person or an AI reads first must name the version that is released."""

    def test_every_hand_written_version_line_names_the_current_version(self) -> None:
        version = _read("VERSION").strip()
        for name, what, pattern in _HAND_WRITTEN_VERSION_LINES:
            with self.subTest(file=name, line=what):
                found = re.findall(pattern, _read(name), re.M)
                self.assertEqual(
                    len(found), 1,
                    f"{name}: expected exactly one {what} (pattern {pattern!r}), found {len(found)}. "
                    "If the sentence was reworded on purpose, update _HAND_WRITTEN_VERSION_LINES — "
                    "a guard that matches nothing guards nothing.",
                )
                self.assertEqual(found[0], version, f"{name}: the {what} says v{found[0]}, VERSION is {version}")


class TestHealthReportsRealVersion(unittest.TestCase):
    def test_health_serves_platform_version_and_release_time(self) -> None:
        body = _build_health_response()
        self.assertEqual(body["status"], "ok")
        self.assertEqual(body["version"], core_version.VERSION)
        self.assertEqual(body["released"], core_version.RELEASED)

    def test_health_keeps_the_bridge_revision_under_its_own_name(self) -> None:
        body = _build_health_response()
        self.assertEqual(body["bridge_version"], SERVER_VERSION)
        self.assertNotEqual(body["version"], body["bridge_version"])


if __name__ == "__main__":
    unittest.main()
