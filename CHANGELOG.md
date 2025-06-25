# Changelog

All notable changes to the `twat-mp` project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - YYYY-MM-DD (MVP Streamline Release)

### Added
- `WorkerError` is now explicitly exported in `src/twat_mp/__init__.py` for better public API consistency.
- `CLEANUP.txt` and `REPO_CONTENT.txt` added to `.gitignore` as they are generated files.
- Comprehensive API reference documentation (`API_REFERENCE.md`) and architecture diagrams (`docs/architecture.md`) created.
- More real-world usage examples added to `README.md`.
- Debug mode with detailed logging implemented, controllable via `set_debug_mode()`.

### Changed
- **Project Focus & Documentation (MVP Streamlining):**
  - `README.md`, `API_REFERENCE.md`, and `docs/architecture.md` updated to emphasize synchronous features (Pathos-based) as the core MVP. Asynchronous features (`aiomultiprocess`-based: `AsyncMultiPool`, `apmap`) are now explicitly marked as "Experimental / Future Work".
  - `src/twat_mp/__init__.py` updated to export only synchronous MVP components and `WorkerError`. Async components (`AsyncMultiPool`, `apmap`) are commented out of `__all__` and their direct imports, with a note regarding MVP isolation. This ensures the public API for v1.0 is focused and stable.
- **Dependencies & Configuration:**
  - `aiomultiprocess` is now an optional dependency, installable via the `[aio]` extra in `pyproject.toml`. This aligns with async features being experimental.
- **Development & CI Scripts:**
  - `cleanup.py` updated:
    - Removed dependency on `LOG.md` (which has been deleted).
    - Pytest execution within `cleanup.py` now ignores `tests/test_async_mp.py` by default, aligning with the MVP's focus on synchronous functionality.
  - `pyproject.toml` test configurations (`tool.hatch.envs.test.scripts.test`) updated to ignore `tests/test_async_mp.py` by default.
- **Testing:**
  - `tests/test_async_mp.py` imports changed from `from twat_mp import ...` to `from twat_mp.async_mp import ...`. This allows these tests to be run independently if the `[aio]` extra is installed, without relying on `__init__.py`'s MVP-focused exports.
- **Error Handling:**
  - Renamed `WorkerException` to `WorkerError` for consistency with Python naming conventions for error classes. Tests have been updated accordingly.
  - Exception propagation from worker processes enhanced to provide more context.
- **Code Quality:**
  - Addressed various Ruff linter warnings, including unused variables and lambda assignments.
  - Improved docstrings across modules for clarity and added examples.

### Fixed
- Corrected project description in `.cursor/rules/0project.mdc` from `twat-fs` to `twat-mp`.
- Resolved issues with `hatch-vcs` build configuration by ensuring `[tool.hatch.version]` was correctly set up in `pyproject.toml`.
- Fixed test assertions related to error handling to align with the new `WorkerError` and improved propagation.
- `test_pool_reuse_failure` in `tests/test_twat_mp.py` updated to correctly reflect and document the behavior of Pathos pools after context exit.

### Removed
- `LOG.md`: Its content was largely redundant with `CHANGELOG.md` and development history.
- `VERSION.txt`: Made redundant by the use of `hatch-vcs` for dynamic versioning from Git tags.

## [2.5.3] - 2025-03-04

### Added

- Added proper version configuration in pyproject.toml using hatch-vcs
- Improved build system configuration for better package distribution
- Created LOG.md file to track development progress (now merged into CHANGELOG.md)
- Updated TODO.md with prioritized tasks

### Fixed

- Fixed package build error related to missing version configuration
- Ensured proper version extraction from Git tags

### Changed

- Updated CHANGELOG.md with recent changes
- Updated README.md with information about recent updates

## [2.0.0] - 2025-02-20

### Added

- Added async support via `aiomultiprocess` integration
- New `AsyncMultiPool` class for combining async/await with multiprocessing
- New `apmap` decorator for easy async parallel processing
- Comprehensive test suite for async functionality
- Documentation for async features

### Changed

- Updated project dependencies to include optional `aiomultiprocess` support
- Enhanced type hints and error handling across the codebase
- Changed version handling to use static version instead of VCS-based versioning

## [1.7.5] - 2025-02-15

### Added

- Implemented AsyncMultiPool class for combining async/await with multiprocessing
- Added apmap decorator for easy async parallel processing
- Created comprehensive test suite for async functionality

### Changed

- Optimized CI/CD pipeline with improved GitHub Actions workflow
- Enhanced stability and performance optimizations in core multiprocessing functions
- Updated documentation and README with clearer usage examples
- Updated project dependencies to include optional aiomultiprocess support
- Enhanced type hints and error handling across the codebase

[Unreleased]: https://github.com/twardoch/twat-mp/compare/v2.5.3...HEAD
[2.5.3]: https://github.com/twardoch/twat-mp/compare/v2.0.0...v2.5.3
[2.0.0]: https://github.com/twardoch/twat-mp/compare/v1.7.5...v2.0.0
[1.7.5]: https://github.com/twardoch/twat-mp/compare/v1.7.3...v1.7.5
// ... existing references ...
