"""twat-mp: Parallel processing utilities for twat using pathos and aiomultiprocess."""

from __future__ import annotations
from .__version__ import __version__


from twat_mp.mp import (
    MultiPool,
    ProcessPool,
    ThreadPool,
    WorkerError,
    amap,
    imap,
    mmap,
    pmap,
    set_debug_mode,
)

# TODO: MVP Isolation - Async features temporarily disabled due to test environment hangs.
# from twat_mp.async_mp import AsyncMultiPool, apmap


def main() -> None:
    """CLI entry point for twat-mp."""
    from twat_mp.__main__ import main as cli_main

    cli_main()


__all__ = [
    # "AsyncMultiPool",  # Temporarily disabled for MVP
    "MultiPool",
    "ProcessPool",
    "ThreadPool",
    "WorkerError",
    "__version__",
    "amap",
    # "apmap",           # Temporarily disabled for MVP
    "imap",
    "main",
    "mmap",
    "pmap",
    "set_debug_mode",
]
