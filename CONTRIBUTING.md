# Contributing to P2P File Sharing System

Thank you for your interest in contributing. This document describes how to report issues, propose changes, and submit pull requests.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

By participating in this project, you agree to:

- Be respectful and inclusive
- Help newcomers get started
- Provide constructive feedback
- Accept feedback on your contributions

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/P2P-File-Sharing-System.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make and test your changes
5. Commit and push to your fork
6. Open a pull request

## How to Contribute

### Reporting Bugs

- Open an issue on GitHub
- Search existing issues first
- Include a clear title, steps to reproduce, and expected vs. actual behavior
- Note your OS and Python version

### Suggesting Features

- Open an issue with the enhancement label
- Describe the feature, use cases, and expected behavior

### Code Contributions

- Bug fixes
- New features
- Documentation improvements
- Tests and performance improvements

## Development Setup

```bash
git clone https://github.com/itsowanga/P2P-File-Sharing-System.git
cd P2P-File-Sharing-System

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -e ".[dev]"

python -m pytest tests/
```

## Coding Standards

### Python Style

- Follow [PEP 8](https://pep8.org/)
- Use clear names for variables and functions
- Prefer a maximum line length of 100 characters
- Use type hints where they add clarity

### Documentation

- Add docstrings to public functions and classes
- Use Google-style docstrings
- Keep comments aligned with the current implementation

### Example

```python
def compute_file_hash(filename: str, algorithm: str = "sha256") -> Optional[str]:
    """
    Compute the hash of a file using the specified algorithm.

    Args:
        filename: Path to the file to hash.
        algorithm: Hashing algorithm (default: sha256).

    Returns:
        Hexadecimal hash string, or None if the file does not exist.
    """
    ...
```

## Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting only
- `refactor`: Code change without behavior change
- `test`: Tests
- `chore`: Maintenance

### Examples

```
feat(gui): add verification progress indicator

fix(tracker): correct peer timeout removal

docs(readme): update installation steps
```

## Pull Request Process

1. Update documentation when behavior or setup changes
2. Add or update tests for new behavior
3. Follow the coding standards above
4. Keep each pull request focused on one change
5. Describe what changed and why in the PR description

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for non-obvious logic
- [ ] Documentation updated as needed
- [ ] No new warnings introduced
- [ ] Tests pass locally

## Project Structure

```
P2P-File-Sharing-System/
├── Client.py           # CLI client
├── ClientGUI.py        # GUI client
├── Tracker.py          # Tracker server
├── HashUtils.py        # File hashing utilities
├── config.py           # Configuration
├── README.md
├── CONTRIBUTING.md
├── LICENSE
├── pyproject.toml
├── .gitignore
└── tests/
```

## Questions

Open an issue if you need clarification on contributing or project setup.

Thank you for contributing.
