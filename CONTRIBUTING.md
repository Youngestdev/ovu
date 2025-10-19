# Contributing to Ovu Transport Aggregator

Thank you for your interest in contributing to Ovu Transport Aggregator! This document provides guidelines for contributing to the project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and collaborative environment.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the bug
- Steps to reproduce
- Expected behavior
- Actual behavior
- Screenshots (if applicable)
- Environment details (OS, Python version, etc.)

### Suggesting Features

We welcome feature suggestions! Please create an issue with:
- Clear description of the feature
- Use cases and benefits
- Possible implementation approach
- Any relevant examples

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/Youngestdev/ovu.git
   cd ovu
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Write clean, readable code
   - Follow the existing code style
   - Add tests for new features
   - Update documentation

4. **Run tests**
   ```bash
   pytest
   ```

5. **Run linters**
   ```bash
   black .
   flake8
   mypy app
   ```

6. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: description"
   ```

7. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request**
   - Provide a clear description
   - Reference any related issues
   - Include screenshots for UI changes

## Development Setup

### Prerequisites
- Python 3.11+
- MongoDB 7.0+
- Redis 7+
- Git

### Setup Steps

1. Clone and install dependencies:
   ```bash
   git clone https://github.com/Youngestdev/ovu.git
   cd ovu
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Start services (using Docker):
   ```bash
   docker-compose up -d mongodb redis
   ```

4. Run the application:
   ```bash
   python main.py
   ```

## Coding Standards

### Python Style Guide

We follow PEP 8 with some modifications:
- Line length: 100 characters (enforced by Black)
- Use type hints where possible
- Use descriptive variable names
- Add docstrings for functions and classes

### Code Formatting

Use Black for code formatting:
```bash
black app tests
```

### Linting

Use Flake8 for linting:
```bash
flake8 app tests
```

### Type Checking

Use MyPy for type checking:
```bash
mypy app
```

## Testing Guidelines

### Writing Tests

- Write tests for all new features
- Maintain or improve code coverage
- Use descriptive test names
- Use fixtures for common setup

Example test:
```python
import pytest
from fastapi.testclient import TestClient

def test_create_booking(client: TestClient, auth_token: str):
    """Test booking creation"""
    response = client.post(
        "/api/v1/bookings",
        json={"provider_reference": "TEST-001", ...},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 201
    assert "booking_reference" in response.json()
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_bookings.py

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/test_bookings.py::test_create_booking
```

## Documentation

### Code Documentation

- Add docstrings to all public functions and classes
- Use clear and concise language
- Include parameter types and return types

Example:
```python
async def create_booking(
    booking_data: BookingCreate,
    user_id: str
) -> Booking:
    """
    Create a new booking.
    
    Args:
        booking_data: Booking creation data
        user_id: ID of the user creating the booking
        
    Returns:
        Created booking object
        
    Raises:
        HTTPException: If booking creation fails
    """
    ...
```

### API Documentation

- Update API_DOCUMENTATION.md for API changes
- Add examples for new endpoints
- Document error responses

## Commit Message Guidelines

Use clear and descriptive commit messages:

### Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples
```
feat(bookings): Add multi-passenger support

Add ability to book for multiple passengers in a single booking.
Includes passenger validation and seat assignment.

Closes #123
```

```
fix(payments): Handle payment webhook timeout

Add retry logic for payment webhook processing.
Improves reliability of payment confirmation.

Fixes #456
```

## Project Structure

```
ovu/
├── app/
│   ├── core/           # Configuration, database, security
│   ├── models/         # Database models
│   ├── schemas/        # API schemas
│   ├── routes/         # API routes
│   ├── services/       # Business logic
│   ├── middleware/     # Middleware
│   └── utils/          # Utilities
├── tests/              # Test files
├── docs/               # Documentation
└── scripts/            # Utility scripts
```

## Review Process

### Pull Request Review

Your PR will be reviewed for:
- Code quality and style
- Test coverage
- Documentation
- Performance implications
- Security concerns

### Review Timeline

- Initial review: 1-3 business days
- Follow-up reviews: 1-2 business days
- We appreciate your patience!

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open a GitHub Issue
- **Security**: See SECURITY.md
- **Chat**: Join our Discord (link in README)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Special mentions for significant contributions

Thank you for contributing to Ovu Transport Aggregator! 🚀
