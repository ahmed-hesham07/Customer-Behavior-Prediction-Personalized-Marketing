# Contributing to Customer Behavior Prediction & Personalized Marketing System

Thank you for your interest in contributing to this project! We welcome contributions from the community.

## How to Contribute

### Reporting Bugs

1. **Check existing issues** first to avoid duplicates
2. **Use the bug report template** when creating new issues
3. **Provide detailed information** including:
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (Python version, OS, etc.)
   - Sample data (if applicable and safe to share)

### Suggesting Features

1. **Open an issue** with the "enhancement" label
2. **Describe the feature** and its business value
3. **Provide use cases** and examples
4. **Consider implementation** complexity and alternatives

### Code Contributions

#### Development Setup

1. **Fork the repository**
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Customer-Behavior-Prediction-Personalized-Marketing.git
   cd Customer-Behavior-Prediction-Personalized-Marketing
   ```

3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-cov flake8 black
   ```

#### Making Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Write tests** for new functionality
3. **Follow code style guidelines**:
   - Use `black` for code formatting
   - Follow PEP 8 standards
   - Add docstrings for new functions/classes
   - Keep lines under 100 characters

4. **Run tests locally**:
   ```bash
   pytest tests/ -v
   flake8 src/
   black --check src/
   ```

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add feature: description of your changes"
   ```

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**

#### Pull Request Guidelines

- **Clear description** of changes and motivation
- **Reference related issues** (e.g., "Fixes #123")
- **Include tests** for new functionality
- **Update documentation** if needed
- **Ensure all CI checks pass**

### Code Style

We follow these conventions:

- **Python**: PEP 8, formatted with `black`
- **Docstrings**: Google style
- **Imports**: Organized and minimal
- **Naming**: Clear and descriptive
- **Comments**: Explain "why", not "what"

### Testing

- **Unit tests** for all new functions
- **Integration tests** for workflows
- **Test coverage** should not decrease
- **Use meaningful test names**

### Documentation

- **Update README.md** for new features
- **Add docstrings** for new code
- **Include examples** in docstrings
- **Update type hints**

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all.

### Our Standards

- **Be respectful** and inclusive
- **Accept constructive criticism**
- **Focus on what's best** for the community
- **Show empathy** towards others

### Enforcement

Unacceptable behavior may result in temporary or permanent exclusion from the project.

## Recognition

Contributors will be acknowledged in:
- **README.md** contributors section
- **Release notes** for significant contributions
- **GitHub contributors** page

Thank you for helping make this project better! 🚀
