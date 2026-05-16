# this_file: src/twat_mp/__main__.py
"""Fire CLI entry point for twat-mp."""

from __future__ import annotations

import os
import time

import fire

from twat_mp.__version__ import __version__
from twat_mp.mp import ProcessPool


def _version() -> str:
    """Print the installed twat-mp version."""
    return __version__


def cmd_version() -> None:
    """Entry point: twat-mp-version."""
    fire.Fire(_version, name="twat-mp-version")


def cmd_pmap() -> None:
    """Entry point: twat-mp-pmap — show pmap decorator usage."""
    fire.Fire(_pmap_info, name="twat-mp-pmap")


def cmd_pfilter() -> None:
    """Entry point: twat-mp-pfilter — show pfilter usage."""
    fire.Fire(_pfilter_info, name="twat-mp-pfilter")


def cmd_bench() -> None:
    """Entry point: twat-mp-bench — run a quick parallel benchmark."""
    fire.Fire(_bench, name="twat-mp-bench")


def _pmap_info(workers: int | None = None) -> str:
    """Show pmap decorator info and worker count.

    Args:
        workers: Number of worker processes (default: os.cpu_count()).

    Returns:
        Informational string about pmap configuration.
    """
    n = workers or os.cpu_count() or 1
    return (
        f"pmap: parallel process-map decorator using pathos ProcessPool.\n"
        f"Workers: {n}\n"
        f"Usage: @pmap  # decorates a single-arg function to map over an iterable in parallel.\n"
        f"Example: from twat_mp import pmap; @pmap\ndef double(x): return x*2\nresult = list(double(range(10)))"
    )


def _pfilter_info(workers: int | None = None) -> str:
    """Show pfilter usage info (parallel filter via pmap).

    Args:
        workers: Number of worker processes (default: os.cpu_count()).

    Returns:
        Informational string about parallel filtering.
    """
    n = workers or os.cpu_count() or 1
    return (
        f"pfilter: parallel filter via pmap decorator using pathos ProcessPool.\n"
        f"Workers: {n}\n"
        f"Usage: apply @pmap to a predicate function, then filter results.\n"
        f"Example: from twat_mp import pmap\n@pmap\ndef is_even(x): return x % 2 == 0\nresult = [x for x, keep in zip(data, is_even(data)) if keep]"
    )


def _bench(n: int = 100, workers: int | None = None) -> dict:
    """Run a quick parallel benchmark (squares of 0..n-1).

    Args:
        n: Number of items to process (default: 100).
        workers: Number of worker processes (default: os.cpu_count()).

    Returns:
        Dict with item count, worker count, and timing results.
    """
    actual_workers = workers or os.cpu_count() or 1
    items = list(range(n))

    # Sequential baseline
    t0 = time.perf_counter()
    seq_results = [x * x for x in items]
    seq_time = time.perf_counter() - t0

    # Parallel
    t1 = time.perf_counter()
    with ProcessPool(nodes=actual_workers) as pool:
        par_results = pool.map(lambda x: x * x, items)
    par_time = time.perf_counter() - t1

    if list(seq_results) != list(par_results):
        msg = "Results mismatch between sequential and parallel execution"
        raise RuntimeError(msg)

    return {
        "n": n,
        "workers": actual_workers,
        "sequential_s": round(seq_time, 6),
        "parallel_s": round(par_time, 6),
        "speedup": round(seq_time / par_time, 3) if par_time > 0 else None,
    }


COMMANDS: dict[str, object] = {
    "version": _version,
    "pmap": _pmap_info,
    "pfilter": _pfilter_info,
    "bench": _bench,
}


def main() -> None:
    """Fire CLI dispatcher for twat-mp."""
    fire.Fire(COMMANDS, name="twat-mp")


if __name__ == "__main__":
    main()
