# Contributing to Marketing Automation MCP Server

We love your input! We want to make contributing to the Marketing Automation MCP Server as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Pull Request Process

1. Update the README.md with details of changes to the interface, this includes new environment variables, exposed ports, useful file locations and container parameters.
2. Increase the version numbers in any examples files and the README.md to the new version that this Pull Request would represent.
3. You may merge the Pull Request in once you have the sign-off of two other developers, or if you do not have permission to do that, you may request the second reviewer to merge it for you.

## Any contributions you make will be under the MIT Software License
In short, when you submit code changes, your submissions are understood to be under the same [MIT License](http://choosealicense.com/licenses/mit/) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report bugs using GitHub's [issues](https://github.com/Mohit4022-cloud/Marketing-Automation-MCP-Server/issues)
We use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/Mohit4022-cloud/Marketing-Automation-MCP-Server/issues/new/choose); it's that easy!

## Write bug reports with detail, background, and sample code

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Mohit4022-cloud/Marketing-Automation-MCP-Server.git
   cd Marketing-Automation-MCP-Server
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

4. **Set up pre-commit hooks**
   ```bash
   pre-commit install
   ```

5. **Copy environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API credentials
   ```

## Code Style Guidelines

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with the following specifications:

- Use 4 spaces for indentation (no tabs)
- Maximum line length is 88 characters (Black default)
- Use type hints for all function signatures
- Write docstrings for all public modules, functions, classes, and methods

### Code Formatting

We use the following tools to maintain code quality:

- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

Run all formatters and linters:
```bash
# Format code
black src/ tests/
isort src/ tests/

# Lint code
flake8 src/ tests/
mypy src/

# Or use pre-commit to run everything
pre-commit run --all-files
```

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, missing semicolons, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Examples:
```
feat: add budget optimization algorithm
fix: correct ROI calculation in reporting module
docs: update API documentation for campaign endpoints
```

## Testing Guidelines

### Writing Tests

- Write tests for all new features
- Maintain test coverage above 90%
- Use pytest for all tests
- Mock external API calls
- Use fixtures for reusable test data

### Test Structure

```python
# tests/unit/test_feature.py
import pytest
from unittest.mock import Mock, patch

class TestFeature:
    """Test suite for Feature functionality."""
    
    @pytest.fixture
    def sample_data(self):
        """Fixture providing sample test data."""
        return {...}
    
    def test_feature_basic_functionality(self, sample_data):
        """Test basic feature functionality."""
        # Arrange
        expected = ...
        
        # Act
        result = feature_function(sample_data)
        
        # Assert
        assert result == expected
    
    @patch('src.integrations.google_ads.GoogleAdsClient')
    def test_external_api_call(self, mock_client):
        """Test feature with mocked external API."""
        # Arrange
        mock_client.return_value.fetch_data.return_value = {...}
        
        # Act & Assert
        ...
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_campaigns.py

# Run tests matching pattern
pytest -k "test_optimization"

# Run tests in parallel
pytest -n auto
```

## Adding New Features

When adding a new feature:

1. **Discuss First**: Open an issue to discuss the feature before implementing
2. **Design Document**: For major features, create a design document
3. **Tests First**: Write tests before implementation (TDD)
4. **Documentation**: Update all relevant documentation
5. **Examples**: Add usage examples to the docs

### Feature Checklist

- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] Type hints added
- [ ] Docstrings complete
- [ ] Example added to docs
- [ ] Performance impact considered
- [ ] Security implications reviewed
- [ ] Backwards compatibility maintained

## Performance Guidelines

- Profile code for performance bottlenecks
- Use async/await for I/O operations
- Implement caching where appropriate
- Consider batch operations for bulk data
- Monitor memory usage

## Security Guidelines

- Never commit secrets or API keys
- Use environment variables for sensitive data
- Validate all user inputs
- Sanitize data before database operations
- Follow OWASP guidelines
- Regular dependency updates

## Documentation

### Docstring Format

We use Google style docstrings:

```python
def optimize_campaign_budget(
    campaign_ids: List[str],
    total_budget: float,
    constraints: Dict[str, Any]
) -> BudgetOptimizationResult:
    """Optimize budget allocation across multiple campaigns.
    
    Uses AI-powered algorithms to redistribute budget for maximum ROI.
    
    Args:
        campaign_ids: List of campaign IDs to optimize
        total_budget: Total budget to allocate
        constraints: Optimization constraints
            - min_budget: Minimum budget per campaign
            - max_budget: Maximum budget per campaign
            - performance_threshold: Minimum ROI threshold
    
    Returns:
        BudgetOptimizationResult containing:
            - allocations: Dict mapping campaign_id to budget
            - projected_roi: Expected ROI improvement
            - confidence_score: Algorithm confidence (0-1)
    
    Raises:
        ValueError: If total_budget is negative
        OptimizationError: If constraints cannot be satisfied
    
    Example:
        >>> result = optimize_campaign_budget(
        ...     campaign_ids=["camp_001", "camp_002"],
        ...     total_budget=10000,
        ...     constraints={"min_budget": 1000}
        ... )
        >>> print(f"Projected ROI: {result.projected_roi}%")
        Projected ROI: 23.5%
    """
```

### API Documentation

When adding new API endpoints or tools:

1. Update `docs/api.md` with endpoint details
2. Include request/response examples
3. Document error codes and handling
4. Add to the tool reference in README

## Review Process

### Code Review Checklist

Reviewers should check:

- [ ] Code follows style guidelines
- [ ] Tests are comprehensive
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] Performance is acceptable
- [ ] Error handling is robust
- [ ] Backwards compatibility

### Review Etiquette

- Be constructive and respectful
- Explain the reasoning behind suggestions
- Acknowledge good solutions
- Ask questions if something is unclear
- Approve PRs promptly when satisfied

## Community

### Getting Help

- Check the [documentation](docs/)
- Search [existing issues](https://github.com/Mohit4022-cloud/Marketing-Automation-MCP-Server/issues)
- Join our [discussions](https://github.com/Mohit4022-cloud/Marketing-Automation-MCP-Server/discussions)
- Ask in the appropriate channel

### Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please:

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on what is best for the community
- Show empathy towards other community members

## License

By contributing, you agree that your contributions will be licensed under its MIT License.

## Recognition

Contributors will be recognized in:
- The README.md contributors section
- Release notes for significant contributions
- The project's GitHub insights

Thank you for contributing to Marketing Automation MCP Server! 🚀