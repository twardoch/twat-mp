# this_file: tests/test_cli.py
"""CLI tests for twat-mp."""

from __future__ import annotations

import subprocess
import sys


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "twat_mp", *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_help_exits_zero() -> None:
    """twat-mp --help exits 0 and prints output (Fire writes help to stderr)."""
    r = _run("--help")
    assert r.returncode == 0
    out = r.stdout + r.stderr
    assert "version" in out.lower() or "bench" in out.lower()


def test_version_exits_zero() -> None:
    """twat-mp version prints a semver string."""
    r = _run("version")
    assert r.returncode == 0
    assert r.stdout.strip()


def test_version_looks_like_semver() -> None:
    """Version string contains at least one dot."""
    r = _run("version")
    assert "." in r.stdout


def test_pmap_help() -> None:
    """twat-mp pmap --help exits 0."""
    r = _run("pmap", "--help")
    assert r.returncode == 0


def test_pfilter_help() -> None:
    """twat-mp pfilter --help exits 0."""
    r = _run("pfilter", "--help")
    assert r.returncode == 0


def test_bench_help() -> None:
    """twat-mp bench --help exits 0."""
    r = _run("bench", "--help")
    assert r.returncode == 0


def test_bench_runs() -> None:
    """twat-mp bench with small n completes successfully."""
    r = _run("bench", "--n=4", "--workers=2")
    assert r.returncode == 0
    assert "sequential_s" in r.stdout or "speedup" in r.stdout
