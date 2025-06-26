# Contributing to API Monitoring

Thank you for your interest in contributing to API Monitoring! We welcome contributions from everyone.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Community](#community)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment
4. Create a new branch for your feature or bug fix
5. Make your changes
6. Test your changes
7. Submit a pull request

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, please include as many details as possible:

- Use a clear and descriptive title
- Describe the exact steps to reproduce the problem
- Provide specific examples to demonstrate the steps
- Describe the behavior you observed and what behavior you expected
- Include screenshots if applicable
- Include your environment details (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- Use a clear and descriptive title
- Provide a step-by-step description of the suggested enhancement
- Provide specific examples to demonstrate the steps
- Describe the current behavior and explain which behavior you expected to see and why
- Explain why this enhancement would be useful

### Your First Code Contribution

Unsure where to begin contributing? You can start by looking through these issue labels:

- `good first issue` - issues which should only require a few lines of code
- `help wanted` - issues which should be a bit more involved than beginner issues

## Development Setup

### Prerequisites

- Python 3.13+
- Git
- MTR (My Traceroute) tool

### Setting up the development environment

1. Clone your fork:
```bash
git clone https://github.com/yourusername/api-monitoring.git
cd api-monitoring
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available
```

4. Install pre-commit hooks (if available):
```bash
pre-commit install
```

5. Copy the example configuration:
```bash
cp .env.example .env
```

6. Edit `.env` with your test configuration

### Running the application

```bash
python -m api_monitoring.main
```

### Running with Docker

```bash
docker-compose up -d
```

## Pull Request Process

1. Ensure any install or build dependencies are removed before the end of the layer when doing a build
2. Update the README.md with details of changes to the interface, if applicable
3. Update the CHANGELOG.md with a note describing your changes
4. Increase the version numbers in any examples files and the README.md to the new version that this Pull Request would represent
5. Your pull request will be merged once you have the sign-off of at least one maintainer

### Pull Request Guidelines

- Use a clear and descriptive title
- Reference any relevant issues in the PR description
- Include a comprehensive description of all changes
- Add tests for new functionality
- Ensure all tests pass
- Update documentation as needed
- Follow the existing code style

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints where appropriate
- Write docstrings for all public functions and classes
- Use meaningful variable and function names
- Keep functions small and focused

### Code Formatting

We use the following tools for code formatting and linting:

- `black` for code formatting
- `isort` for import sorting
- `flake8` for linting
- `mypy` for type checking

Run these tools before submitting your PR:

```bash
black .
isort .
flake8 .
mypy .
```

### Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line
- Consider starting the commit message with an applicable emoji:
  - 🎉 `:tada:` when adding a new feature
  - 🐛 `:bug:` when fixing a bug
  - 📚 `:books:` when writing docs
  - 🎨 `:art:` when improving the format/structure of the code
  - 🐎 `:racehorse:` when improving performance
  - 🔧 `:wrench:` when updating configuration files

## Testing

### Running Tests

```bash
python -m pytest
```

### Writing Tests

- Write tests for all new functionality
- Ensure tests are isolated and can run independently
- Use descriptive test names
- Include both positive and negative test cases
- Mock external dependencies

### Test Coverage

We aim for high test coverage. You can check coverage with:

```bash
python -m pytest --cov=api_monitoring
```

## Documentation

- Update the README.md if you change functionality
- Add docstrings to new functions and classes
- Update type hints
- Consider adding examples for new features

## Community

### Getting Help

- Check the [documentation](README.md)
- Search existing [issues](https://github.com/dkamenkov/api-monitoring/issues)
- Create a new issue if you can't find an answer

### Discussions

- Use GitHub Discussions for questions and general discussion
- Use GitHub Issues for bug reports and feature requests

## Recognition

Contributors will be recognized in the following ways:

- Listed in the CONTRIBUTORS.md file
- Mentioned in release notes for significant contributions
- Given credit in commit messages

Thank you for contributing to API Monitoring! 🎉