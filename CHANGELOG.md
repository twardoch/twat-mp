# Changelog

All notable changes to the `twat-mp` project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Created comprehensive API reference documentation
- Added architecture diagrams explaining component relationships and workflows
- Added real-world examples for image processing, data processing, web scraping, and file operations
- Implemented better error handling with descriptive error messages and suggestions
- Added interactive examples in Jupyter notebooks
- Implemented debug mode with detailed logging

### Changed
- Improved resource cleanup in AsyncMultiPool.__aexit__ using close() instead of terminate()
- Enhanced error handling during pool cleanup to ensure proper resource management
- Updated docstrings with more examples and clearer explanations
- Improved compatibility with Python 3.12+ async features
- Enhanced exception propagation from worker processes

### Fixed
- Fixed AttributeError handling in exception handling code
- Improved graceful shutdown mechanism with better signal handling
- Fixed keyboard interrupt handling during parallel execution
- Addressed linter warnings and improved code quality

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
### Changed
- Optimized CI/CD pipeline with improved GitHub Actions workflow
- Enhanced stability and performance optimizations in core multiprocessing functions
- Updated documentation and README with clearer usage examples

[Unreleased]: https://github.com/twardoch/twat-mp/compare/v1.8.0...HEAD
[1.8.0]: https://github.com/twardoch/twat-mp/compare/v1.7.5...v1.8.0
[1.7.5]: https://github.com/twardoch/twat-mp/compare/v1.7.3...v1.7.5
// ... existing references ...
