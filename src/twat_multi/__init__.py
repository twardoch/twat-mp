"""
twat_multi - Parallel processing utilities using Pathos multiprocessing library.

This package provides convenient wrappers and decorators around Pathos pools
for easy parallel processing. It includes a context manager for pool management
and decorators for common parallel mapping operations.
"""

from importlib import metadata

from .__main__ import (
    amap,
    benchmark_parallel_vs_sequential,
    imap,
    pathos_with,
    pmap,
)

__version__ = metadata.version(__name__)
__all__ = [
    "__version__",
    "amap",
    "benchmark_parallel_vs_sequential",
    "imap",
    "pathos_with",
    "pmap",
]
