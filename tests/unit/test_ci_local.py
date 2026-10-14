"""Guard: scripts/ci_local.sh (`make ci-local`) keeps doing what it promises: test a CLEAN CLONE of a commit, in a SCRUBBED environment, on the Python versions of the CI matrix.

It exists because CI went red twice while `make test` was green on the developer's machine: in 2.6.2 (CI had no `pytest`, and nothing declared `jinja2`; the
developer's machine had both) and at c501335 (a test that needed ~/AI_OS/30_RUNTIME/bin/aios-gate). `make test` runs in the working copy with the machine's environment; CI does not have either.

These tests do not run the whole thing: that creates a venv, installs from PyPI and would run this very suite inside itself. They pin the parts that make
the result mean something, each with a seeded defect, and the script is sourced (it supports that) so the pieces can be called one by one:

  * the isolation probe flags every kind of leak it is meant to flag (variables, real HOME, non-empty HOME, ~/AI_OS, PATH under the real home, AI_OS tools);
  * the sandbox builder passes nothing from the caller and keeps Homebrew/user directories off PATH;
  * the clone holds the commit and nothing else (no uncommitted, untracked or ignored file) and fires no git hook;
  * the Python matrix is read from the ref's ci.yml, and an unreadable matrix stops the run instead of being guessed;
  * the Makefile target exists, `make test` does not call it, and README/AGENTS tell people to use it.
"""

from __future__ import annotations

import os
import re
import shlex
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _ROOT / "scripts" / "ci_local.sh"
_BASH = "/bin/bash"
# No hook, no signing, no identity from the machine: the throwaway repos behave the same here and on CI.
_GIT = ["git", "-c", "core.hooksPath=/dev/null", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c", "commit.gpgsign=false"]

_CI_INLINE = (
    "jobs:\n  test:\n    strategy:\n      matrix:\n        python-version: [\"3.10\", \"3.12\", \"3.13\"]\n"
    "    steps:\n      - uses: actions/setup-python@v5\n        with:\n          python-version: ${{ matrix.python-version }}\n"
)
_CI_BLOCK = "jobs:\n  test:\n    strategy:\n      matrix:\n        python-version:\n          - \"3.11\"\n          - \"3.12\"\n"

_LEAKY_VARS = ("ATP_SECRET", "AIOS_GATE", "ANTHROPIC_API_KEY", "OPENAI_API_KEY", "CLAUDE_CODE_X", "AWS_PROFILE", "GITHUB_TOKEN", "SSH_AUTH_SOCK", "VIRTUAL_ENV", "PYTHONPATH")


def _env() -> dict[str, str]:
    """The caller's environment minus the variables git sets inside a hook, so a pre-push run does not point the throwaway repos at the real one."""
    return {k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_PREFIX")}


def _run(args: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, env=env if env is not None else _env(), capture_output=True, text=True, timeout=90, check=False)


def _git(repo: Path, *args: str) -> str:
    r = _run([*_GIT, *args], cwd=repo)
    assert r.returncode == 0, f"git {' '.join(args)} failed: {r.stderr}"
    return r.stdout.strip()


def _make_repo(tmp: Path, ci_yml: str | None) -> Path:
    """A throwaway repo that holds a copy of the script: the script finds its repo from its own location."""
    repo = tmp / "repo"
    (repo / "scripts").mkdir(parents=True)
    shutil.copy2(_SCRIPT, repo / "scripts" / "ci_local.sh")
    if ci_yml is not None:
        (repo / ".github" / "workflows").mkdir(parents=True)
        (repo / ".github" / "workflows" / "ci.yml").write_text(ci_yml, encoding="utf-8")
    _git(repo, "init", "-q")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "init")
    return repo


def _sourced(script: Path, body: str, *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    """Source the script, drop errexit (the script sets it) so a failing function's status can be read, then run `body`."""
    return _run([_BASH, "-c", f"source {shlex.quote(str(script))}; set +e; {body}"], env=env)


def _executable(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return path


class TestScriptAndMakefile(unittest.TestCase):
    def test_script_is_executable_and_valid_bash(self) -> None:
        self.assertTrue(_SCRIPT.is_file(), "scripts/ci_local.sh is gone")
        self.assertTrue(os.access(_SCRIPT, os.X_OK), "scripts/ci_local.sh is not executable (git add --chmod=+x)")
        r = _run([_BASH, "-n", str(_SCRIPT)])
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_makefile_target_exists_and_make_test_does_not_call_it(self) -> None:
        text = (_ROOT / "Makefile").read_text(encoding="utf-8")
        phony = " ".join(re.findall(r"^\.PHONY:(.*(?:\\\n.*)*)", text, re.M)).replace("\\", " ")
        self.assertIn("ci-local", phony.split(), "ci-local is not in .PHONY")
        self.assertRegex(text, r"(?m)^ci-local:\n\t@\./scripts/ci_local\.sh \$\(CI_LOCAL_ARGS\)\n", "the ci-local recipe does not call scripts/ci_local.sh with CI_LOCAL_ARGS")
        self.assertRegex(text, r"(?m)^\t@printf '  ci-local ", "make help does not list ci-local")
        for target in re.findall(r"(?m)^(test(?:-unit|-integration)?):(.*)$", text):
            self.assertNotIn("ci-local", target[1], f"`make {target[0]}` must not call ci-local: it would run this suite inside itself")

    def test_documented_where_people_look(self) -> None:
        for name in ("README.md", "AGENTS.md", "scripts/README.md"):
            self.assertIn("ci-local", (_ROOT / name).read_text(encoding="utf-8"), f"{name} does not mention ci-local")

    def test_help_lists_every_option_and_unknown_options_are_refused(self) -> None:
        r = _run([str(_SCRIPT), "--help"])
        self.assertEqual(r.returncode, 0, r.stderr)
        for opt in ("--ref", "--python", "--strict", "--keep", "--print-matrix", "--self-check"):
            self.assertIn(opt, r.stdout, f"--help does not describe {opt}")
        bad = _run([str(_SCRIPT), "--nope"])
        self.assertEqual(bad.returncode, 2)
        self.assertIn("unknown option", bad.stderr)

    @unittest.skipUnless(shutil.which("git") and (_ROOT / ".git").exists(), "needs a git checkout")
    def test_an_unknown_ref_stops_before_anything_is_cloned(self) -> None:
        r = _run([str(_SCRIPT), "--ref", "no-such-ref-xyz"])
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("unknown ref", r.stderr)


class TestMatrix(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)

    def _matrix(self, repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return _run([str(repo / "scripts" / "ci_local.sh"), "--print-matrix", *args])

    def test_inline_matrix_is_read(self) -> None:
        r = self._matrix(_make_repo(self.tmp, _CI_INLINE))
        self.assertEqual(r.stdout.split(), ["3.10", "3.12", "3.13"], r.stderr)

    def test_matrix_comes_from_the_ref_not_from_the_working_tree(self) -> None:
        repo = _make_repo(self.tmp, _CI_INLINE)
        first = _git(repo, "rev-parse", "HEAD")
        (repo / ".github" / "workflows" / "ci.yml").write_text(_CI_INLINE.replace('"3.10", "3.12", "3.13"', '"3.9"'), encoding="utf-8")
        self.assertEqual(self._matrix(repo).stdout.split(), ["3.10", "3.12", "3.13"], "an uncommitted edit of ci.yml leaked into the matrix")
        _git(repo, "commit", "-q", "-am", "narrow the matrix")
        self.assertEqual(self._matrix(repo).stdout.split(), ["3.9"])
        self.assertEqual(self._matrix(repo, "--ref", first).stdout.split(), ["3.10", "3.12", "3.13"], "--ref did not select the older ci.yml")

    def test_an_unreadable_matrix_stops_the_run_instead_of_being_guessed(self) -> None:
        for name, ci in (("block list", _CI_BLOCK), ("no matrix at all", "name: ci\n"), ("no workflow file", None)):
            with self.subTest(name):
                r = self._matrix(_make_repo(self.tmp / name.replace(" ", "_"), ci))
                self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
                self.assertEqual(r.stdout, "", "printed a matrix it could not read")
                self.assertIn("cannot read the Python matrix", r.stderr)

    def test_python_option_replaces_the_matrix_even_when_it_is_unreadable(self) -> None:
        repo = _make_repo(self.tmp, _CI_BLOCK)
        self.assertEqual(self._matrix(repo, "--python", "3.12,3.13").stdout.split(), ["3.12", "3.13"])
        self.assertEqual(self._matrix(repo, "--python", "3.11 3.12").stdout.split(), ["3.11", "3.12"])

    @unittest.skipUnless(shutil.which("git") and (_ROOT / ".git").exists(), "needs a git checkout")
    def test_the_real_ci_matrix_is_readable(self) -> None:
        r = _run([str(_SCRIPT), "--print-matrix"])
        self.assertEqual(r.returncode, 0, r.stderr)
        committed = _run([*_GIT, "show", "HEAD:.github/workflows/ci.yml"], cwd=_ROOT).stdout
        expected = re.findall(r'"(\d+\.\d+)"', re.search(r"python-version: *\[(.*)\]", committed).group(1))  # type: ignore[union-attr]
        self.assertTrue(expected, "ci.yml has no inline python-version list any more: update matrix_of in scripts/ci_local.sh and this test")
        self.assertEqual(r.stdout.split(), expected)


class TestFindPython(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)

    def _find(self, version: str) -> str:
        bin_dir = self.tmp / "bin"
        env = {**_env(), "PATH": f"{bin_dir}:{_env().get('PATH', '/usr/bin:/bin')}"}
        return _sourced(_SCRIPT, f"find_python {shlex.quote(version)}", env=env).stdout.strip()

    def test_a_python_whose_minor_version_does_not_match_is_refused(self) -> None:
        fake = _executable(self.tmp / "bin" / "python3.77", "#!/bin/sh\nexit 0\n")
        _executable(self.tmp / "bin" / "python3.78", "#!/bin/sh\nexit 1\n")  # answers like an interpreter of another version
        self.assertEqual(self._find("3.77"), str(fake))
        self.assertEqual(self._find("3.78"), "", "an interpreter that fails the version check was used")

    def test_a_version_that_is_not_installed_yields_nothing_and_nothing_is_downloaded(self) -> None:
        self.assertEqual(self._find("9.99"), "")


class TestIsolationProbe(unittest.TestCase):
    """Every kind of leak the probe is meant to catch is seeded once; the control shows the same setup passing."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.real_home = self.tmp / "real_home"
        (self.real_home / "bin").mkdir(parents=True)
        self.parent = self.tmp / "parent"
        self.parent.mkdir()
        self.home = self.tmp / "sandbox_home"
        self.home.mkdir()

    def _probe(self, *, home: Path | None = None, path: str = "/usr/bin:/bin", extra: tuple[str, ...] = (), want_bin: str = "") -> subprocess.CompletedProcess[str]:
        sandbox = " ".join(shlex.quote(x) for x in ["env", "-i", f"HOME={home or self.home}", f"PATH={path}", "CI=true", *extra])
        return _sourced(_SCRIPT, f"SANDBOX=({sandbox}); sandbox_probe {shlex.quote(str(self.real_home))} {shlex.quote(str(self.parent))} {shlex.quote(want_bin)}")

    def _assert_leak(self, r: subprocess.CompletedProcess[str], needle: str) -> None:
        self.assertNotEqual(r.returncode, 0, f"the probe let this through:\n{r.stdout}")
        self.assertIn("LEAK", r.stdout)
        self.assertIn(needle, r.stdout)

    def test_control_a_clean_sandbox_passes(self) -> None:
        r = self._probe()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn("LEAK", r.stdout)

    def test_seeded_environment_variables_are_flagged(self) -> None:
        for var in _LEAKY_VARS:
            with self.subTest(var):
                self._assert_leak(self._probe(extra=(f"{var}=x",)), var)

    def test_seeded_home_problems_are_flagged(self) -> None:
        with self.subTest("HOME is the real home"):
            self._assert_leak(self._probe(home=self.real_home), "HOME is the real home")
        with self.subTest("HOME inside the real home"):
            inside = self.real_home / "sub"
            inside.mkdir()
            self._assert_leak(self._probe(home=inside), "HOME is the real home")
        with self.subTest("HOME not empty"):
            (self.home / "leftover").write_text("x", encoding="utf-8")
            self._assert_leak(self._probe(), "HOME is not empty")
        with self.subTest("~/AI_OS present"):
            shutil.rmtree(self.home)
            (self.home / "AI_OS").mkdir(parents=True)
            self._assert_leak(self._probe(), "~/AI_OS exists")

    def test_seeded_path_problems_are_flagged(self) -> None:
        with self.subTest("PATH entry under the real home"):
            self._assert_leak(self._probe(path=f"{self.real_home / 'bin'}:/usr/bin:/bin"), "PATH entries under the real home")
        with self.subTest("an AI_OS tool on PATH"):
            _executable(self.tmp / "tools" / "aios-gate", "#!/bin/sh\nexit 0\n")
            self._assert_leak(self._probe(path=f"{self.tmp / 'tools'}:/usr/bin:/bin"), "aios-gate")
        with self.subTest("python3 is not the venv one"):
            self._assert_leak(self._probe(want_bin=str(self.tmp / "venv" / "bin")), "python3 is")

    def test_the_sandbox_directory_itself_may_live_under_the_real_home(self) -> None:
        """TMPDIR can sit under HOME on some machines; the venv bin dir (inside the sandbox) must not be reported as a leak."""
        parent = self.real_home / "tmp" / "atp-ci-local.X"
        venv_bin = parent / "venv" / "bin"
        _executable(venv_bin / "python3", "#!/bin/sh\nexit 0\n")
        r = _sourced(
            _SCRIPT,
            f"SANDBOX=(env -i HOME={shlex.quote(str(self.home))} PATH={shlex.quote(str(venv_bin))}:/usr/bin:/bin); "
            f"sandbox_probe {shlex.quote(str(self.real_home))} {shlex.quote(str(parent))} {shlex.quote(str(venv_bin))}",
        )
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("python3 is the venv one", r.stdout)


class TestSandbox(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)

    def test_sandbox_passes_nothing_from_the_caller_and_keeps_user_directories_off_path(self) -> None:
        polluted = {**_env(), **{v: "leaked" for v in _LEAKY_VARS}, "HOMEBREW_PREFIX": "/opt/homebrew", "HTTPS_PROXY": "http://proxy.invalid"}
        r = _sourced(_SCRIPT, f"build_sandbox {shlex.quote(str(self.tmp))} {shlex.quote(str(self.tmp / 'venv'))}; printf '%s\\n' \"${{SANDBOX[@]}}\"", env=polluted)
        self.assertEqual(r.returncode, 0, r.stderr)
        words = r.stdout.splitlines()
        self.assertEqual(words[:2], ["env", "-i"], "the sandbox must start from an empty environment (env -i)")
        assigned = dict(w.split("=", 1) for w in words[2:])
        self.assertEqual(assigned["HOME"], str(self.tmp / "home"))
        self.assertEqual(assigned["CI"], "true")
        self.assertEqual(assigned["PATH"].split(":")[0], str(self.tmp / "venv" / "bin"))
        for entry in assigned["PATH"].split(":"):
            self.assertNotIn(entry, ("/opt/homebrew/bin", "/usr/local/bin"), "PATH reaches Homebrew/user-installed tools that CI does not have")
            self.assertFalse(entry.startswith(str(Path.home())) and entry != str(self.tmp / "venv" / "bin"), f"PATH entry under the real home: {entry}")
        self.assertFalse(set(assigned) & (set(_LEAKY_VARS) | {"HOMEBREW_PREFIX", "HTTPS_PROXY"}), "a variable from the caller reached the sandbox")

    def test_self_check_reports_a_polluted_caller_as_clean(self) -> None:
        polluted = {**_env(), **{v: "leaked" for v in _LEAKY_VARS}}
        r = _run([str(_SCRIPT), "--self-check"], env=polluted)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn("LEAK", r.stdout)
        self.assertIn("HOME is not the real home", r.stdout)


@unittest.skipUnless(shutil.which("git"), "needs git")
class TestCloneAndReport(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.repo = _make_repo(self.tmp, _CI_INLINE)
        self.script = self.repo / "scripts" / "ci_local.sh"

    def test_the_clone_holds_the_commit_and_nothing_else(self) -> None:
        (self.repo / "tracked.txt").write_text("v1", encoding="utf-8")
        (self.repo / ".gitignore").write_text("ignored.txt\n", encoding="utf-8")
        _git(self.repo, "add", "-A")
        _git(self.repo, "commit", "-q", "-m", "v1")
        v1 = _git(self.repo, "rev-parse", "HEAD")
        (self.repo / "tracked.txt").write_text("v2", encoding="utf-8")
        _git(self.repo, "commit", "-q", "-am", "v2")
        # Dirty state a plain `make test` would see and CI would not:
        (self.repo / "tracked.txt").write_text("uncommitted edit", encoding="utf-8")
        (self.repo / "untracked.txt").write_text("x", encoding="utf-8")
        (self.repo / "ignored.txt").write_text("x", encoding="utf-8")

        dst = self.tmp / "clone"
        r = _sourced(self.script, f"clone_at {shlex.quote(str(dst))} {shlex.quote(v1)}")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual((dst / "tracked.txt").read_text(encoding="utf-8"), "v1", "--ref was not checked out")
        for name in ("untracked.txt", "ignored.txt"):
            self.assertFalse((dst / name).exists(), f"{name} is in the clone: ci-local would hide a file CI does not have")
        self.assertEqual(_git(dst, "rev-parse", "HEAD"), v1)

    def test_the_clone_runs_no_git_hook_even_when_one_is_configured_globally(self) -> None:
        marker = self.tmp / "hook-ran"
        _executable(self.tmp / "hooks" / "post-checkout", f"#!/bin/sh\ntouch {shlex.quote(str(marker))}\n")
        # What this machine has: a global ~/.gitconfig whose core.hooksPath points at hooks that fire on every checkout.
        (self.tmp / "gitconfig").write_text(f"[core]\n\thooksPath = {self.tmp / 'hooks'}\n", encoding="utf-8")
        env = {**_env(), "GIT_CONFIG_GLOBAL": str(self.tmp / "gitconfig")}
        control = _run(["git", "clone", "-q", str(self.repo), str(self.tmp / "control")], env=env)
        self.assertEqual(control.returncode, 0, control.stderr)
        self.assertTrue(marker.exists(), "control: the configured hook should fire on a plain clone, or this test proves nothing")
        marker.unlink()
        r = _sourced(self.script, f"clone_at {shlex.quote(str(self.tmp / 'clone'))} HEAD", env=env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse(marker.exists(), "a git hook fired during the ci-local clone")

    def test_uncommitted_work_is_reported_and_a_clean_tree_is_silent(self) -> None:
        clean = _sourced(self.script, 'report_uncommitted "$ROOT_DIR"')
        self.assertEqual((clean.returncode, clean.stdout, clean.stderr), (0, "", ""), "a clean tree must print nothing")
        (self.repo / "tracked.txt").write_text("v1", encoding="utf-8")
        _git(self.repo, "add", "tracked.txt")
        _git(self.repo, "commit", "-q", "-m", "add tracked.txt")
        (self.repo / "tracked.txt").write_text("edited", encoding="utf-8")
        (self.repo / "new_test.py").write_text("x", encoding="utf-8")
        dirty = _sourced(self.script, 'report_uncommitted "$ROOT_DIR"')
        self.assertEqual(dirty.returncode, 0)
        self.assertIn("NOT in the commit under test", dirty.stderr)
        self.assertIn("?? new_test.py", dirty.stderr)
        self.assertIn("M tracked.txt", dirty.stderr)


if __name__ == "__main__":
    unittest.main()
