#!/usr/bin/env python3
"""
Parallel processing utilities using Pathos multiprocessing library.

This module provides convenient wrappers and decorators around Pathos pools
for easy parallel processing. It includes a context manager for pool management
and decorators for common parallel mapping operations.

Example:
    from twat_multi import pathos_with, amap, imap, pmap

    # Using context manager directly
    with pathos_with() as pool:
        results = pool.map(lambda x: x*2, range(1000))

    # Using decorators
    @amap
    def parallel_square(x):
        return x * x

    results = parallel_square(range(1000))
"""

import multiprocessing
import time
from functools import wraps
from typing import (
    Any,
    Callable,
    Iterable,
    Iterator,
    Literal,
    Optional,
    TypeVar,
    cast,
    overload,
)

from pathos.pools import ProcessPool

T = TypeVar("T")
U = TypeVar("U")


class pathos_with:
    """
    Context manager for Pathos parallel processing pools.

    Handles creation and cleanup of Pathos pools with proper resource management.
    Automatically determines optimal number of processes based on CPU count.

    Args:
        pool_class: The Pathos pool class to use (default: ProcessPool)
        nodes: Number of processes to use. If None, uses CPU count (default: None)

    Example:
        >>> with pathos_with() as pool:
        ...     results = pool.map(lambda x: x*2, range(100))
        >>> print(results[:5])
        [0, 2, 4, 6, 8]
    """

    def __init__(
        self, pool_class: type = ProcessPool, nodes: Optional[int] = None
    ) -> None:
        self.pool_class = pool_class
        self.nodes = nodes if nodes is not None else multiprocessing.cpu_count()
        self.pool: Optional[ProcessPool] = None

    def __enter__(self) -> ProcessPool:
        """Initialize and return the process pool."""
        if self.pool is None:
            self.pool = self.pool_class(nodes=self.nodes)
        assert self.pool is not None
        return self.pool

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> Literal[False]:
        """Clean up pool resources."""
        if self.pool:
            self.pool.close()
            self.pool.join()
            self.pool.clear()
        return False  # Propagate exceptions


@overload
def pathos_map_decorator(
    method_name: str, get_result: Literal[True] = True
) -> Callable[[Callable[[T], U]], Callable[[Iterable[T]], list[U]]]: ...


@overload
def pathos_map_decorator(
    method_name: str, get_result: Literal[False] = False
) -> Callable[[Callable[[T], U]], Callable[[Iterable[T]], Iterator[U]]]: ...


def pathos_map_decorator(
    method_name: str, get_result: bool = False
) -> Callable[[Callable[[T], U]], Callable[[Iterable[T]], Any]]:
    """
    Creates a decorator for parallel mapping operations using Pathos pools.

    Args:
        method_name: Name of the pool method to use ('map', 'imap', or 'amap')
        get_result: Whether to call .get() on the result (for amap) (default: False)

    Returns:
        A decorator function that wraps the target function for parallel execution

    Example:
        >>> @pathos_map_decorator('map')
        ... def parallel_func(x):
        ...     return x * 2
        >>> results = parallel_func(range(5))
        >>> list(results)
        [0, 2, 4, 6, 8]
    """

    def decorator(func: Callable[[T], U]) -> Callable[[Iterable[T]], Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with pathos_with() as pool:
                if not args:
                    raise ValueError("No iterable provided to parallel function")
                method = getattr(pool, method_name)
                result = method(func, args[0])
                if get_result:
                    result = result.get()
                return result

        return wrapper

    return decorator


# Convenience decorators for different mapping strategies
imap = pathos_map_decorator("imap")  # Lazy evaluation, returns iterator
amap = pathos_map_decorator("amap", get_result=True)  # Async evaluation with .get()
pmap = pathos_map_decorator("map")  # Standard parallel map


# Example functions demonstrating decorator usage
@amap
def isquare(x: int) -> int:
    """Square a number using async parallel processing."""
    return x * x


@amap
def isubs(x: int) -> int:
    """Subtract 1 from a number using async parallel processing."""
    return x - 1


def square(x: int) -> int:
    """Square a number (sequential version for comparison)."""
    return x * x


def subs(x: int) -> int:
    """Subtract 1 from a number (sequential version for comparison)."""
    return x - 1


def benchmark_parallel_vs_sequential(size: int = 200) -> None:
    """
    Benchmark parallel vs sequential processing performance.

    Compares execution time of parallel and sequential operations
    on a range of numbers using various mapping strategies.

    Args:
        size: Size of the input range to process (default: 200)
    """
    # Example 1: Sequential map vs parallel map for squaring
    start_time = time.perf_counter()
    results = list(map(square, range(size)))
    print(f"Sequential map results: {results[:5]}...")
    print(f"Sequential time: {time.perf_counter() - start_time:.4f}s")

    start_time = time.perf_counter()
    results = list(isquare(range(size)))
    print(f"Parallel map results: {results[:5]}...")
    print(f"Parallel time: {time.perf_counter() - start_time:.4f}s")

    # Example 2: Sequential vs parallel composition of functions
    start_time = time.perf_counter()
    results = list(map(subs, map(square, range(size))))
    print(f"Sequential composition results: {results[:5]}...")
    print(f"Sequential composition time: {time.perf_counter() - start_time:.4f}s")

    start_time = time.perf_counter()
    results = list(isubs(isquare(range(size))))
    print(f"Parallel composition results: {results[:5]}...")
    print(f"Parallel composition time: {time.perf_counter() - start_time:.4f}s")
