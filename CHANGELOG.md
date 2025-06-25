# Changelog

All notable changes to the `twat-mp` project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### MVP Focus and Streamlining ( omfattande förändringar för MVP v1.0)

(This section summarizes recent changes to focus the library on a robust synchronous MVP, with asynchronous features positioned as experimental/future.)

### Added
- `WorkerError` is now explicitly exported in `src/twat_mp/__init__.py`.
- `CLEANUP.txt` and `REPO_CONTENT.txt` added to `.gitignore`.

- Created comprehensive API reference documentation
- Added architecture diagrams explaining component relationships and workflows
- Added real-world examples for image processing, data processing, web scraping, and file operations
- Implemented better error handling with descriptive error messages and suggestions
- Added interactive examples in Jupyter notebooks
- Implemented debug mode with detailed logging

### Changed
- **Project Focus & Documentation:**
  - README, API Reference, and Architecture documents updated to emphasize synchronous features (Pathos-based) as the core MVP. Asynchronous features (aiomultiprocess-based) are now explicitly marked as experimental/future.
  - `src/twat_mp/__init__.py` updated to ensure only synchronous MVP components and `WorkerError` are exported; async components are clearly isolated.
- **Dependencies & Configuration:**
  - `aiomultiprocess` is now an optional dependency installable via the `[aio]` extra in `pyproject.toml` (moved from core dependencies).
- **Development & CI Scripts:**
  - `cleanup.py` updated:
    - Removed dependency on `LOG.md`.
    - Default pytest execution now ignores `tests/test_async_mp.py` to align with MVP focus.
- **Testing:**
  - `tests/test_async_mp.py` imports changed to `from twat_mp.async_mp import ...` to allow independent execution if `aio` extras are installed, decoupling from `__init__.py`'s MVP isolation.
- Improved resource cleanup in AsyncMultiPool.__aexit__ using close() instead of terminate() (Note: AsyncMultiPool is now experimental)
- Enhanced error handling during pool cleanup to ensure proper resource management
- Updated docstrings with more examples and clearer explanations
- Improved compatibility with Python 3.12+ async features
- Enhanced exception propagation from worker processes
- Fixed build system configuration by adding proper `tool.hatch.version` settings
- Renamed `WorkerException` to `WorkerError` for consistency with Python naming conventions
- Updated tests to reflect the new error handling behavior
- Fixed `test_pool_reuse_failure` test to document current behavior
- Improved code quality by removing unused variables and lambda assignments

### Fixed
- Corrected project description in `.cursor/rules/0project.mdc` to accurately describe `twat-mp` instead of `twat-fs`.
- Fixed AttributeError handling in exception handling code
- Improved graceful shutdown mechanism with better signal handling
- Fixed keyboard interrupt handling during parallel execution
- Addressed linter warnings and improved code quality
- Fixed package build error by adding missing version configuration in pyproject.toml
- Fixed inconsistent exception naming across the codebase
- Fixed test assertions to properly check for error messages in `WorkerError`

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
