# Style Guide

This document describes the conventions used in `twat-mp` source code and tests.

## Python version target

- Minimum: **Python 3.10**
- Use `from __future__ import annotations` in every module for PEP 563 deferred evaluation.
- Use `X | Y` union syntax (not `Union[X, Y]`), `list[T]` (not `List[T]`), etc.

## Formatting and linting

- **Formatter**: `ruff format` — 120-character line limit, double quotes, LF line endings.
- **Linter**: `ruff check` — see `[tool.ruff.lint]` in `pyproject.toml` for active rules.
- **Type checker**: `mypy` with strict settings (see `[tool.mypy]` in `pyproject.toml`).

Run all checks at once:

```bash
ruff format . && ruff check --fix . && mypy src/twat_mp
```

## Naming conventions

- Public classes: `PascalCase` — e.g., `ProcessPool`, `WorkerError`.
- Public functions and decorators: `snake_case` — e.g., `pmap`, `set_debug_mode`.
- Private helpers: leading underscore — e.g., `_worker_wrapper`.
- Type variables: single uppercase letter — `T`, `U`.
- Constants: `UPPER_SNAKE_CASE` — e.g., `DEBUG_MODE`.

## Docstrings

- **Style**: Google-style (`Args:`, `Returns:`, `Raises:`, `Example:`).
- Every public function, method, and class **must** have a docstring.
- Private helpers should have a one-line summary at minimum.
- Include a runnable `Example:` block for all public decorators and context managers.

## Error handling

- Worker errors inside pool maps are wrapped as `WorkerError`.
- Decorator wrappers (`pmap`, `imap`, `amap`) re-raise the `original_exception` from `WorkerError` so callers see the original error type.
- Use `raise X from Y` to preserve exception chains.
- Never silence exceptions silently; log at `ERROR` level before re-raising.

## Parallel pool usage

- Use `ProcessPool` for CPU-bound work (bypasses GIL via separate processes).
- Use `ThreadPool` for I/O-bound work (avoids pickling overhead).
- Always use pools as context managers (`with ProcessPool() as pool:`).
- Do not share mutable state across worker processes.

## Tests

- Test files: `tests/test_*.py`.
- `test_async_mp.py` and `test_benchmark.py` are excluded from the default test run.
- Every public function must have at least one test covering the happy path.
- Error paths and edge cases (empty iterables, large data) should be tested.
- Module-level exception classes in tests must be defined at **module level** (not inside functions) for pickle compatibility across process boundaries.

## File headers

Every source file should include a `this_file:` comment near the top:

```python
# this_file: src/twat_mp/mp.py
```

## Commit style

- Imperative mood: `Add X`, `Fix Y`, `Remove Z`.
- Reference the module or symbol affected: `mp: fix WorkerError propagation in amap`.
