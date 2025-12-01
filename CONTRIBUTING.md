# Contributing to Pokemon Strategy Agent

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## Code Standards

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Maximum line length: 100 characters

### Testing

- Write tests for all new features
- Maintain >90% code coverage
- Run tests before committing:
  ```bash
  pytest tests/ -v
  ```

### Git Workflow

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit:
   ```bash
   git add .
   git commit -m "Add: description of changes"
   ```

3. Push and create Pull Request:
   ```bash
   git push origin feature/your-feature-name
   ```

## Commit Message Format

Use conventional commits:

- `Add:` New feature
- `Fix:` Bug fix
- `Update:` Changes to existing functionality
- `Docs:` Documentation changes
- `Test:` Adding or updating tests
- `Refactor:` Code refactoring

Example:
```
Add: personality analysis feature with AI interpretation

- Implemented analyze_personality_from_text endpoint
- Added support for 27 Pokemon starters
- Created comprehensive tests
```

## Pull Request Guidelines

1. **Description**: Clearly describe what your PR does and why
2. **Tests**: Include tests for new functionality
3. **Documentation**: Update relevant documentation
4. **Code Quality**: Ensure all tests pass and code follows standards

## Questions?

If you have questions or need help, please open an issue or reach out to the maintainers.

Thank you for contributing! 🎮
