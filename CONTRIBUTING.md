# Contributing to P2P File Sharing System

Thank you for your interest in contributing to this project! This document provides guidelines and information for contributors.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)

## 📜 Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code:

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive criticism
- Accept feedback gracefully

## 🚀 Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/P2P-File-Sharing-System.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes
6. Commit and push
7. Open a Pull Request

## 💡 How to Contribute

### Reporting Bugs

- Use the GitHub Issues page
- Check if the issue already exists
- Include a clear title and description
- Provide steps to reproduce
- Include system information (OS, Python version)

### Suggesting Features

- Open an issue with the "enhancement" label
- Clearly describe the feature and its benefits
- Provide use cases if possible

### Code Contributions

- Fix bugs
- Implement new features
- Improve documentation
- Write tests
- Optimize performance

## 🛠️ Development Setup

```bash
# Clone the repository
git clone https://github.com/itsowanga/P2P-File-Sharing-System.git
cd P2P-File-Sharing-System

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies (if any)
pip install -e ".[dev]"

# Run tests
python -m pytest tests/
```

## 📝 Coding Standards

### Python Style

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use meaningful variable and function names
- Maximum line length: 100 characters
- Use type hints where appropriate

### Documentation

- Add docstrings to all public functions and classes
- Use Google-style docstrings format
- Keep comments up to date with code changes

### Example

```python
def compute_file_hash(filename: str, algorithm: str = "sha256") -> Optional[str]:
    """
    Compute the hash of a file using the specified algorithm.
    
    Args:
        filename: Path to the file to hash.
        algorithm: Hashing algorithm to use (default: 'sha256').
    
    Returns:
        Hexadecimal hash string, or None if the file doesn't exist.
    
    Raises:
        IOError: If the file cannot be read.
    """
    ...
```

## 📌 Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```
feat(gui): add file verification progress bar

fix(tracker): resolve peer timeout calculation bug

docs(readme): update installation instructions
```

## 🔄 Pull Request Process

1. **Update Documentation**: Update README.md if needed
2. **Add Tests**: Include tests for new functionality
3. **Follow Style Guide**: Ensure code follows project standards
4. **Single Purpose**: Each PR should address one concern
5. **Clear Description**: Explain what and why

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings introduced
- [ ] Tests pass locally

## 🏗️ Project Structure

```
P2P-File-Sharing-System/
├── Client.py           # CLI client
├── ClientGUI.py        # GUI client
├── Tracker.py          # Tracker server
├── HashUtils.py        # File hashing utilities
├── config.py           # Configuration settings
├── README.md           # Project documentation
├── CONTRIBUTING.md     # This file
├── LICENSE             # MIT License
├── pyproject.toml      # Project metadata
├── .gitignore          # Git ignore rules
└── tests/              # Test files
    └── ...
```

## ❓ Questions?

Feel free to open an issue for any questions or concerns. We're happy to help!

---

Thank you for contributing! 🎉
