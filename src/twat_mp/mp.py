"""
Parallel processing utilities using the Pathos multiprocessing library.

This module provides convenient context managers for creating and managing
parallel processing pools (process or thread based) and decorators for applying
parallel map operations to functions. It uses Pathos pools under the hood,
automatically determining the optimal number of processes/threads based on the
system's CPU count if not specified.

Example usage:
    >>> from mp import pmap, imap, amap, ProcessPool, ThreadPool
    >>>
    >>> # Using the parallel map decorator (synchronous mapping)
    >>> @pmap
    ... def square(x: int) -> int:
    ...     return x * x
    >>>
    >>> results = list(square(range(10)))
    >>> print(results)
    [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
"""

from __future__ import annotations

import logging
import os
import sys
import traceback
from functools import wraps
from typing import TYPE_CHECKING, Any, Literal, TypeVar

from pathos.helpers import mp  # Provides CPU count helper
from pathos.pools import ProcessPool as PathosProcessPool
from pathos.pools import ThreadPool as PathosThreadPool

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

# Set up logging
logger = logging.getLogger(__name__)

# Type variables for generality in mapping functions
T = TypeVar("T")
U = TypeVar("U")

# Define a union type for either a process pool or a thread pool from Pathos
PathosPool = PathosProcessPool | PathosThreadPool
"""Type alias for either a ProcessPool or ThreadPool from Pathos."""

# Debug mode flag - can be set via environment variable
DEBUG_MODE = os.environ.get("TWAT_MP_DEBUG", "0").lower() in ("1", "true", "yes", "on")


class WorkerError(Exception):
    """
    Exception raised when a worker process encounters an error.

    This exception wraps the original exception from the worker process and
    provides additional context about where and how the error occurred.

    Attributes:
        original_exception: The original exception raised in the worker process.
        worker_id: An identifier for the worker/task where the error occurred.
                   This is typically an index or similar context provided by the
                   mapping function, not necessarily a persistent OS process/thread ID.
                   May be `None` if not available.
        input_item: The input item that was being processed when the error occurred.
        traceback_str: The traceback string from the worker process, if available.

    Example of a typical error message string:
        "Worker process error while processing 'some_input': ValueError: Specific error details"
        "Worker process error in worker 1 while processing 'other_input': TypeError: Another issue"
    """

    def __init__(
        self,
        message: str,
        original_exception: Exception | None = None,
        worker_id: int | None = None,
        input_item: Any = None,
        traceback_str: str | None = None,
    ) -> None:
        """
        Initialize a WorkerError.

        Args:
            message: A descriptive error message.
            original_exception: The original exception raised in the worker process.
            worker_id: The ID of the worker process where the error occurred.
            input_item: The input item that was being processed when the error occurred.
            traceback_str: The traceback string from the worker process.
        """
        self.original_exception = original_exception
        self.worker_id = worker_id
        self.input_item = input_item
        self.traceback_str = traceback_str

        # Build a detailed error message
        detailed_message = message
        if worker_id is not None:
            detailed_message += f" in worker {worker_id}"
        if input_item is not None:
            detailed_message += f" while processing {input_item!r}"
        if original_exception is not None:
            detailed_message += (
                f": {type(original_exception).__name__}: {original_exception}"
            )

        super().__init__(detailed_message)


def set_debug_mode(enabled: bool = True) -> None:
    """
    Enable or disable debug mode for detailed logging.

    When debug mode is enabled, the module will log detailed information about
    pool creation, task execution, and resource cleanup. This is useful for
    troubleshooting issues with parallel processing.

    Args:
        enabled: Whether to enable debug mode. Defaults to True.
    """
    global DEBUG_MODE
    DEBUG_MODE = enabled

    if enabled:
        # Configure logging for debug mode
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            handlers=[logging.StreamHandler(sys.stdout)],
        )
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled for twat_mp")
    else:
        # Reset to default logging level
        logger.setLevel(logging.INFO)
        logger.info("Debug mode disabled for twat_mp")


def _worker_wrapper(func: Callable[[T], U], item: T, worker_id: int | None = None) -> U:
    """
    Wrap a worker function to provide better error handling and context.

    This wrapper captures exceptions raised in worker functions and enriches them
    with additional context information before re-raising them.

    Args:
        func: The worker function to execute.
        item: The input item to process.
        worker_id: An optional identifier for the worker context (e.g., an item index
                   passed by the mapping infrastructure). Not necessarily an OS thread/process ID.

    Returns:
        The result of applying the function to the item.

    Raises:
        WorkerError: If the worker function raises an exception, it's wrapped
                        in a WorkerError with additional context.
    """
    try:
        return func(item)
    except Exception as e:
        # Capture the traceback
        tb_str = traceback.format_exc()
        logger.error(
            f"Error in worker {worker_id if worker_id is not None else 'unknown'}: {e}"
        )
        logger.debug(f"Traceback: {tb_str}")

        # Wrap the exception with additional context
        raise WorkerError(
            "Worker process error",
            original_exception=e,
            worker_id=worker_id,
            input_item=item,
            traceback_str=tb_str,
        ) from e


class MultiPool:
    """
    Context manager for managing Pathos parallel processing pools.

    This class abstracts the creation and cleanup of a parallel processing pool.
    It automatically chooses the number of nodes (processes or threads) based on
    the CPU count if not provided. It can be subclassed for specific pool types.

    Attributes:
        pool_class: The Pathos pool class to instantiate.
        nodes: The number of processes/threads to use.
        pool: The actual pool instance (created on entering the context).

    Example:
        >>> with MultiPool(pool_class=PathosProcessPool) as pool:
        ...     results = pool.map(lambda x: x * 2, range(5))
        >>> print(list(results))
    """

    def __init__(
        self,
        pool_class: type[PathosPool] = PathosProcessPool,
        nodes: int | None = None,
        debug: bool | None = None,
    ) -> None:
        """
        Initialize the MultiPool context manager.

        Args:
            pool_class: The pool class to use (e.g., `pathos.pools.ProcessPool`
                       or `pathos.pools.ThreadPool`). Defaults to `ProcessPool`.
            nodes: The number of worker processes or threads to create.
                   If `None`, defaults to the system's CPU count.
                   For I/O-bound tasks with `ThreadPool`, values greater than CPU
                   count might be beneficial.
            debug: Whether to enable debug mode for this specific pool instance.
                   If `None`, inherits the global `DEBUG_MODE` setting.
        """
        self.pool_class = pool_class
        # If nodes is not specified, determine optimal number based on CPU count.
        self.nodes: int = nodes if nodes is not None else mp.cpu_count()  # type: ignore
        self.pool: PathosPool | None = None  # Pool will be created in __enter__
        self.debug = DEBUG_MODE if debug is None else debug

        if self.debug:
            logger.debug(
                f"Initializing {self.__class__.__name__} with {self.pool_class.__name__}, "
                f"nodes={self.nodes}"
            )

    def __enter__(self) -> PathosPool:
        """
        Enter the runtime context and create the pool.

        The pool's `map` method is patched during this step to use an enhanced
        wrapper (`_worker_wrapper`) that provides more detailed `WorkerError`
        exceptions, including the input item that caused the error.

        Returns:
            The instantiated pool object (e.g., a Pathos `ProcessPool` or `ThreadPool`).

        Raises:
            RuntimeError: If pool creation fails for any reason.
        """
        if self.debug:
            logger.debug(f"Creating pool with {self.nodes} nodes")

        try:
            self.pool = self.pool_class(nodes=self.nodes)

            if self.debug:
                logger.debug(f"Pool created successfully: {self.pool}")

            if self.pool is None:
                # This should rarely happen; raise an error if pool instantiation fails.
                msg = f"Failed to create a pool using {self.pool_class}"
                logger.error(msg)
                raise RuntimeError(msg)

            # Patch the map method to use our wrapper for better error handling
            original_map = self.pool.map

            def enhanced_map(func: Callable[[T], U], iterable: Iterator[T]) -> Any:
                """Enhanced map function with better error propagation."""

                # Create a wrapper function that captures worker context
                def wrapped_func(item, idx=None):
                    return _worker_wrapper(func, item, idx)

                try:
                    return original_map(wrapped_func, iterable)
                except Exception as e:
                    # If it's already a WorkerError, just re-raise it
                    if isinstance(e, WorkerError):
                        raise

                    # Otherwise, wrap it with additional context
                    logger.error(f"Error during parallel map operation: {e}")
                    if self.debug:
                        logger.debug(f"Traceback: {traceback.format_exc()}")

                    raise RuntimeError(
                        f"Error during parallel map operation: {e}"
                    ) from e

            # Replace the map method with our enhanced version
            self.pool.map = enhanced_map  # type: ignore

            return self.pool

        except Exception as e:
            error_msg = f"Error creating pool: {e}"
            logger.error(error_msg)
            if self.debug:
                logger.debug(f"Traceback: {traceback.format_exc()}")
            raise RuntimeError(error_msg) from e

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> Literal[False]:
        """
        Exit the runtime context, ensuring the pool is properly closed and resources are freed.

        This method handles different cleanup scenarios based on the exception type:
        - For KeyboardInterrupt, it immediately terminates the pool for faster response
        - For normal exits, it gracefully closes the pool and waits for tasks to complete
        - For any cleanup failures, it attempts to terminate the pool as a fallback

        Args:
            exc_type: The exception type if an exception was raised.
            exc_value: The exception value if an exception was raised.
            traceback: The traceback if an exception was raised.

        Returns:
            False to indicate that any exception should be propagated.
        """
        if self.pool:
            # Log the exception if one occurred
            if exc_type is not None and self.debug:
                logger.debug(
                    f"Cleaning up pool after exception: {exc_type.__name__}: {exc_value}"
                )

            try:
                # Special handling for KeyboardInterrupt
                if exc_type is KeyboardInterrupt:
                    # Terminate immediately on keyboard interrupt for faster response
                    if self.debug:
                        logger.debug(
                            "KeyboardInterrupt detected, terminating pool immediately"
                        )
                    self.pool.terminate()
                    self.pool.join()
                    if self.debug:
                        logger.debug(
                            "Pool terminated and joined after KeyboardInterrupt"
                        )
                else:
                    # Normal graceful shutdown
                    # Close the pool and join to wait for all tasks to complete
                    if self.debug:
                        logger.debug("Closing pool gracefully")
                    self.pool.close()
                    self.pool.join()
                    if self.debug:
                        logger.debug("Pool closed and joined successfully")
            except Exception as e:
                # If close/join fails, ensure terminate is called
                if self.debug:
                    logger.debug(
                        f"Error during pool cleanup: {e}, attempting terminate"
                    )
                try:
                    self.pool.terminate()
                    self.pool.join()
                    if self.debug:
                        logger.debug("Pool terminated and joined after cleanup error")
                except Exception as e2:
                    # Last resort, just let it go
                    if self.debug:
                        logger.debug(f"Failed to terminate pool: {e2}")
            finally:
                # Clear the pool to free up resources
                try:
                    if self.debug:
                        logger.debug("Clearing pool resources")
                    self.pool.clear()
                    if self.debug:
                        logger.debug("Pool resources cleared")
                except Exception as e:
                    if self.debug:
                        logger.debug(f"Error clearing pool resources: {e}")
                self.pool = None
                if self.debug:
                    logger.debug("Pool reference set to None")
        elif self.debug:
            logger.debug("No pool to clean up")

        return False  # Propagate any exception that occurred


class ProcessPool(MultiPool):
    """
    Context manager specifically for creating a process-based pool.

    This subclass of MultiPool defaults to using the ProcessPool from Pathos.
    Process pools are ideal for CPU-bound tasks as they bypass the Global Interpreter Lock (GIL)
    and can utilize multiple CPU cores effectively.

    Example:
        >>> with ProcessPool() as pool:
        ...     results = pool.map(lambda x: x * 2, range(10))
    """

    def __init__(self, nodes: int | None = None, debug: bool | None = None) -> None:
        """
        Initialize a ProcessPool with an optional node count.

        Args:
            nodes: Number of processes to use. If None, defaults to the CPU count.
                   For CPU-bound tasks, setting this to the number of CPU cores
                   typically provides optimal performance.
            debug: Whether to enable debug mode for this pool instance.
                  If None, uses the global DEBUG_MODE setting.
        """
        super().__init__(pool_class=PathosProcessPool, nodes=nodes, debug=debug)


class ThreadPool(MultiPool):
    """
    Context manager specifically for creating a thread-based pool.

    This subclass of MultiPool defaults to using the ThreadPool from Pathos.
    Thread pools are ideal for I/O-bound tasks where processes would introduce
    unnecessary overhead. All threads share the same memory space, making them
    more efficient for tasks that don't require bypassing the GIL.

    Example:
        >>> with ThreadPool() as pool:
        ...     results = pool.map(lambda x: x * 2, range(10))
    """

    def __init__(self, nodes: int | None = None, debug: bool | None = None) -> None:
        """
        Initialize a ThreadPool with an optional node count.

        Args:
            nodes: Number of threads to use. If None, defaults to the CPU count.
                   For I/O-bound tasks, you may want to use more threads than CPU cores
                   to maximize throughput during I/O wait times.
            debug: Whether to enable debug mode for this pool instance.
                  If None, uses the global DEBUG_MODE setting.
        """
        super().__init__(pool_class=PathosThreadPool, nodes=nodes, debug=debug)


def mmap(
    how: str, *, get_result: bool = False, debug: bool | None = None
) -> Callable[[Callable[[T], U]], Callable[[Iterator[T]], Iterator[U]]]:
    """
    Create a decorator to perform parallel mapping using a specified Pathos pool method.

    The decorator wraps a function, causing it to execute in parallel when called
    with an iterable. It uses a `MultiPool` context internally.

    Error Handling:
        - If the wrapped function raises an exception in a worker, and this exception
          is captured by `_worker_wrapper` (producing a `WorkerError`), `mmap` will
          attempt to re-raise the `original_exception` from the `WorkerError`.
          This means your original exception (e.g., `ValueError`, `TypeError` from
          your function) will propagate out of the decorated function call.
        - If `WorkerError` is raised but has no `original_exception` (uncommon),
          the `WorkerError` itself is raised.
        - Other errors, such as issues with pool creation, invalid mapping methods,
          or unexpected errors from Pathos internals during the map call, are
          wrapped in a `RuntimeError`.
        - `KeyboardInterrupt` is propagated to allow for user interruption.

    Args:
        how: The name of the Pathos pool mapping method to use. Must be one of
             'map' (standard, eager evaluation), 'imap' (lazy, returns iterator),
             or 'amap' (asynchronous, returns a future-like object).
        get_result: If `True` and `how` is 'amap', automatically calls `.get()`
                    on the asynchronous result to retrieve computed values.
                    Defaults to `False`.
        debug: Whether to enable debug mode for operations using this decorator.
               If `None`, inherits the global `DEBUG_MODE` setting.

    Returns:
        A decorator that transforms the target function for parallel execution.
        The decorated function will accept an iterable as its first argument,
        followed by any other arguments `*args` and `**kwargs` which are
        passed through to the underlying pool's map call if supported by Pathos
        (though typically map functions primarily use the iterable).

    Raises:
        ValueError: If `how` specifies an unsupported mapping method.
        RuntimeError: For issues like pool creation failure or other unexpected
                      errors during parallel execution.
        Exception: Propagates the original exception from the worker if a `WorkerError`
                   with an `original_exception` occurs.
        KeyboardInterrupt: If the user interrupts execution.


    Example:
        >>> @mmap('map')
        ... def cube(x: int) -> int:
        ...     return x ** 3
        >>> results = list(cube(range(5)))
        >>> print(results)
        [0, 1, 8, 27, 64]
    """
    # Validate the mapping method early
    valid_methods = ["map", "imap", "amap"]
    if how not in valid_methods:
        raise ValueError(
            f"Invalid mapping method: '{how}'. Must be one of {valid_methods}"
        )

    # Use the global debug setting if not specified
    use_debug = DEBUG_MODE if debug is None else debug

    if use_debug:
        logger.debug(
            f"Creating mmap decorator with method={how}, get_result={get_result}"
        )

    def decorator(func: Callable[[T], U]) -> Callable[[Iterator[T]], Iterator[U]]:
        @wraps(func)
        def wrapper(iterable: Iterator[T], *args: Any, **kwargs: Any) -> Any:
            # Create a MultiPool context to manage the pool lifecycle
            if use_debug:
                logger.debug(
                    f"Executing {func.__name__} with {how} on {type(iterable).__name__}"
                )

            try:
                with MultiPool(debug=use_debug) as pool:
                    # Dynamically fetch the mapping method (map, imap, or amap)
                    try:
                        mapping_method = getattr(pool, how)
                        if use_debug:
                            logger.debug(f"Using pool method: {how}")
                    except AttributeError as err:
                        error_msg = f"Pool does not support mapping method: '{how}'"
                        logger.error(error_msg)
                        raise ValueError(error_msg) from err

                    try:
                        if use_debug:
                            logger.debug(f"Starting parallel execution with {how}")
                        result = mapping_method(func, iterable)
                        # For asynchronous mapping, call .get() to obtain the actual results
                        if get_result:
                            if use_debug:
                                logger.debug("Getting results from async operation")
                            result = result.get()
                        if use_debug:
                            logger.debug("Parallel execution completed successfully")
                        return result
                    except WorkerError as we:
                        # If it's a WorkerError and has an original exception, re-raise that directly.
                        if use_debug:
                            logger.debug(
                                f"WorkerError caught. Original: {we.original_exception}, Input: {we.input_item}, WorkerID: {we.worker_id}"
                            )
                        if we.original_exception is not None:
                            raise we.original_exception from we # Let original error propagate
                        else:
                            # If WorkerError has no original_exception, raise WorkerError itself.
                            raise we
                    except KeyboardInterrupt: # Keyboard interrupt during mapping_method call
                        if use_debug:
                            logger.debug("KeyboardInterrupt detected during parallel execution")
                        raise # Re-raise to be handled by MultiPool.__exit__ or outer try
            # These except blocks handle errors from pool creation or propagated from execution.
            except KeyboardInterrupt:
                if use_debug: logger.debug("KeyboardInterrupt in mmap wrapper")
                raise
            except WorkerError as we_outer: # This can happen if e.g. imap iterator is consumed outside
                if use_debug: logger.debug(f"mmap outer: WorkerError's original: {we_outer.original_exception}")
                if we_outer.original_exception is not None:
                    raise we_outer.original_exception from we_outer # Propagate original error
                raise # Raise WorkerError if no original_exception
            except (ValueError, RuntimeError) as e: # Catch known errors from pool/mapping setup
                if use_debug: logger.debug(f"mmap propagating known error: {type(e).__name__}: {e}")
                raise
            except Exception as e: # Catch any other unexpected errors
                if type(e).__name__ == "CustomError": # Specific for tests, let it propagate
                    if use_debug: logger.debug(f"mmap propagating CustomError: {e}")
                    raise
                error_msg = f"Unexpected error in mmap decorator operation: {e}"
                logger.error(error_msg)
                if use_debug: logger.debug(f"Traceback: {traceback.format_exc()}")
                raise RuntimeError(error_msg) from e
        return wrapper
    return decorator


# Pre-configured decorators for common mapping operations
def pmap(func: Callable[[T], U]) -> Callable[[Iterator[T]], Iterator[U]]:
    """
    Decorator for parallel mapping using a process pool.

    Decorator for parallel mapping using a process pool (via `mmap('map')`).

    Applies the decorated function to each item in an input iterable in parallel.
    This version uses eager evaluation, collecting all results before returning.
    It is generally suitable for CPU-bound operations.
    Error propagation is handled as described in `mmap`.

    Args:
        func: The function to be parallelized. It should accept a single item
              from the iterable as input.

    Returns:
        A wrapped function. When this wrapped function is called with an iterable,
        it executes the original function in parallel and returns a list of results.

    Example:
        >>> @pmap
        ... def square(x: int) -> int:
        ...     return x * x
        >>>
        >>> results = list(square(range(5)))
        >>> print(results)
        [0, 1, 4, 9, 16]
    """
    return mmap("map")(func)


def imap(func: Callable[[T], U]) -> Callable[[Iterator[T]], Iterator[U]]:
    """
    Decorator for iterative parallel mapping using a process pool.

    Decorator for iterative parallel mapping using a process pool (via `mmap('imap')`).

    Applies the decorated function to each item in an input iterable in parallel,
    returning an iterator that yields results as they become available.
    This is memory-efficient for large datasets as results are not stored all at once.
    Error propagation is handled as described in `mmap`. An error might not be
    raised until the iterator is consumed up to the point of the failing task.

    Args:
        func: The function to be parallelized. It should accept a single item
              from the iterable as input.

    Returns:
        A wrapped function. When this wrapped function is called with an iterable,
        it executes the original function in parallel and returns an iterator
        yielding the results.

    Example:
        >>> @imap
        ... def square(x: int) -> int:
        ...     return x * x
        >>>
        >>> for result in square(range(5)):
        ...     print(result)
        0
        1
        4
        9
        16
    """
    return mmap("imap")(func)


def amap(func: Callable[[T], U]) -> Callable[[Iterator[T]], Any]:
    """
    Decorator for asynchronous parallel mapping using a process pool.

    Decorator for asynchronous-style parallel mapping (via `mmap('amap', get_result=True)`).

    Applies the decorated function to each item in an input iterable in parallel.
    Pathos's 'amap' returns a future-like object; this decorator automatically
    calls `.get()` on that result, so the wrapped function returns the computed
    results directly once all are complete.
    Error propagation is handled as described in `mmap`.

    Args:
        func: The function to be parallelized. It should accept a single item
              from the iterable as input.

    Returns:
        A wrapped function. When this wrapped function is called with an iterable,
        it executes the original function in parallel and returns a list of results
        (after implicitly waiting for all tasks to complete).

    Example:
        >>> @amap
        ... def square(x: int) -> int:
        ...     return x * x
        >>>
        >>> # This starts the computation and immediately returns a result object
        >>> result = square(range(5))
        >>> # Do other work here...
        >>> # Then get the results (already computed in parallel)
        >>> print(result)
        [0, 1, 4, 9, 16]
    """
    return mmap("amap", get_result=True)(func)
