"""Platform version and release timestamp reported at runtime (G-VERSTAMP-1).

Single source for what /health and /status serve. A deployed release has no
git history, so these constants (not a file lookup) are what reaches a reader.
tests/unit/test_version_consistency.py keeps them equal to VERSION, RELEASED,
pyproject.toml and the CHANGELOG entry.
"""

VERSION = "2.6.3"
RELEASED = "2026-10-14T20:43:55+07:00"
