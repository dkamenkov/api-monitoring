# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Open source project structure with LICENSE, CONTRIBUTING.md, and CODE_OF_CONDUCT.md
- GitHub Actions workflows for CI/CD
- Issue and pull request templates
- Security policy (SECURITY.md)
- Comprehensive documentation

## [2.0.0] - 2024-06-26

### Added
- Complete rewrite with modern asynchronous architecture
- Asynchronous architecture using asyncio and aiohttp
- AWS-compatible API monitoring with aiobotocore
- Maintenance mode detection
- Intelligent alerting with MTR traces to Telegram
- Custom alert comments support
- Auto-resolution notifications
- Structured JSON logging
- Docker and Docker Compose support
- Pydantic-based configuration validation
- Modular package structure
- Comprehensive test suite
- Type hints throughout the codebase

### Changed
- Migrated from synchronous to asynchronous architecture
- Updated to Python 3.13+
- Replaced requests with aiohttp
- Replaced boto3 with aiobotocore for async AWS operations
- Improved error handling and logging
- Enhanced configuration management with Pydantic
- Better project structure with proper Python packaging

### Removed
- Legacy synchronous code
- Old threading-based implementation
- Deprecated configuration methods

## [1.0.0] - 2023-10-16

### Added
- Initial release
- Basic API monitoring functionality
- Telegram alerting
- MTR network tracing
- Simple configuration with environment variables
- Basic logging to file
- Synchronous implementation with threading

### Features
- API availability checking
- Maintenance mode detection
- Telegram notifications
- Network trace collection
- Basic error handling

[Unreleased]: https://github.com/dkamenkov/api-monitoring/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/dkamenkov/api-monitoring/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/dkamenkov/api-monitoring/releases/tag/v1.0.0