"""SSH execution adapter placeholder for ATP M6.

DEFERRED — remote SSH exec is not implemented in M6 (returns a clear ``deferred``
result so callers degrade cleanly).

TODO (M6 build → M1 compliance): when remote SSH exec IS implemented, it MUST go
through the MCCM platform — never a private SSH path. AI_OS rule M1 (one connection
authority): every Mac↔ManagAIR SSH connection routes through MCCM, which owns the
route, the transport argv (incl. ``-J dbm`` / anchor-relay for TWR), the credentials,
and the audit. Do NOT re-implement subnet→anchor tables, ProxyJump logic, or password
fallbacks here.

Intended wiring (when un-deferred)::

    import sys, os
    sys.path.insert(0, os.path.expanduser("~/SOURCE_DEV/platforms/MCCM/python"))
    from mccm import ssh as mccm_ssh   # build_ssh_argv(host, remote_cmd, proxy_jump=...)
    from mccm import route as mccm_route

    argv = await mccm_ssh.build_ssh_argv(host, command_argv)   # mac-external anchor relay
    proc = await asyncio.create_subprocess_exec(*argv, ...)

(Or, once MCCM is pip-installed in the ATP venv: ``from mccm import ssh, route``.)
SSOT: ``platforms/MCCM/core/data/anchors.default.yaml``; engine: ``mccm.ssh`` / ``mccm.route``.
"""

from __future__ import annotations

from typing import Any


def execute_remote(execution_request: dict[str, Any]) -> dict[str, Any]:
    """Return a clear deferred remote execution result.

    When implemented (M6), delegate to MCCM ``ssh``/``route`` (M1) — see the module
    docstring. Until then this never executes anything."""

    return {
        "command": execution_request.get("payload", {}).get("command_argv", []),
        "exit_code": None,
        "stdout": "",
        "stderr": "Remote SSH execution is deferred in ATP M6.",
        "status": "deferred",
        "notes": [
            "SSH remote execution is not implemented in M6.",
            "When implemented, route through MCCM (mccm.ssh / mccm.route) per rule M1 — "
            "no private SSH/subnet/ProxyJump logic in ATP.",
        ],
    }
