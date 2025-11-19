# B2B API Testing Guide

## Overview

Comprehensive test suite for the Ovu B2B API covering:
- Partner service unit tests
- Webhook delivery tests
- API integration tests
- Rate limiting tests
- Authentication tests

## Test Files

### 1. `test_partner_management.py`
**Unit tests for partner service**

Tests:
- Partner code generation
- API credentials generation
- Secret hashing and verification
- Partner creation
- API key CRUD operations
- Key rotation and revocation
- Usage tracking

**Test Classes:**
- `TestPartnerService` - Main service tests (15+ tests)
- `TestPartnerCodeGeneration` - Edge cases for code generation
- `TestSecretHashing` - Security and hashing tests

### 2. `test_webhook_service.py`
**Unit tests for webhook delivery**

Tests:
- HMAC signature generation
- Webhook delivery (success/failure)
- Retry logic with exponential backoff
- Event subscription filtering
- Payload structure validation
- Security features

**Test Classes:**
- `TestWebhookService` - Core webhook tests (15+ tests)
- `TestWebhookPayload` - Payload structure tests
- `TestWebhookSecurity` - Security feature tests

### 3. `test_b2b_api.py`
**Integration tests for B2B API endpoints**

Tests:
- Partner management endpoints
- API key management endpoints
- Usage analytics endpoints
- Webhook configuration endpoints
- Search and booking endpoints
- Rate limiting
- Authentication

**Test Classes:**
- `TestPartnerManagementEndpoints` - Partner CRUD
- `TestAPIKeyManagementEndpoints` - API key operations
- `TestUsageAnalyticsEndpoints` - Analytics
- `TestWebhookConfigurationEndpoints` - Webhooks
- `TestPartnerAPIEndpoints` - Search/booking
- `TestRateLimiting` - Rate limits
- `TestAuthentication` - Auth/authz

## Running Tests

### Run All Tests

```bash
pytest tests/
```

### Run Specific Test File

```bash
# Partner management tests
pytest tests/test_partner_management.py -v

# Webhook tests
pytest tests/test_webhook_service.py -v

# Integration tests
pytest tests/test_b2b_api.py -v
```

### Run Specific Test Class

```bash
pytest tests/test_partner_management.py::TestPartnerService -v
```

### Run Specific Test

```bash
pytest tests/test_partner_management.py::TestPartnerService::test_create_partner -v
```

### Run with Coverage

```bash
# Generate coverage report
pytest --cov=app --cov-report=html tests/

# View coverage report
open htmlcov/index.html
```

### Run Tests Matching Pattern

```bash
# Run all tests with "webhook" in the name
pytest -k webhook -v

# Run all tests with "api_key" in the name
pytest -k api_key -v
```

## Test Setup

### Prerequisites

1. **MongoDB**: Running instance for database tests
2. **Redis** (optional): For rate limiting tests
3. **Environment**: Test environment variables

### Environment Setup

Create `.env.test` file:

```bash
# Test Database
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=ovu_transport_test

# Redis (optional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=1  # Use different DB for tests

# Test Keys
SECRET_KEY=test_secret_key_for_testing_only
JWT_ALGORITHM=HS256
```

### Install Test Dependencies

```bash
pip install pytest pytest-asyncio pytest-cov
```

## Test Fixtures

### Available Fixtures

- `client` - FastAPI test client
- `admin_user` - Admin user for testing
- `test_partner` - Test partner with API credentials

### Using Fixtures

```python
@pytest.mark.asyncio
async def test_example(client, test_partner):
    response = client.get(
        "/api/v1/partners/me",
        headers={"X-API-Key": test_partner.test_api_key}
    )
    assert response.status_code == 200
```

## Mocking External Services

### Mock Webhook Delivery

```python
@patch('httpx.AsyncClient')
async def test_webhook(mock_client):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_client.return_value.__aenter__.return_value.post = AsyncMock(
        return_value=mock_response
    )
    # Test code here
```

### Mock Redis

```python
@patch('redis.Redis')
def test_rate_limit(mock_redis):
    mock_redis.return_value.get.return_value = "5"
    # Test code here
```

## Test Coverage Goals

Target coverage by module:
- `app/services/partner_service.py` - 95%+
- `app/services/webhook_service.py` - 90%+
- `app/routes/partners.py` - 85%+
- `app/middleware/rate_limit.py` - 80%+

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      mongodb:
        image: mongo:7
        ports:
          - 27017:27017
      
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      
      - name: Run tests
        run: pytest --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Troubleshooting

### MongoDB Connection Issues

```bash
# Check if MongoDB is running
mongosh --eval "db.runCommand({ ping: 1 })"

# Start MongoDB with Docker
docker run -d -p 27017:27017 --name test-mongo mongo:7
```

### Redis Connection Issues

```bash
# Check if Redis is running
redis-cli ping

# Start Redis with Docker
docker run -d -p 6379:6379 --name test-redis redis:7-alpine
```

### Async Test Issues

Make sure to use `@pytest.mark.asyncio` decorator:

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result is not None
```

### Fixture Cleanup

Ensure fixtures clean up after themselves:

```python
@pytest.fixture
async def test_partner():
    partner = await create_partner()
    yield partner
    await partner.delete()  # Cleanup
```

## Best Practices

1. **Isolation**: Each test should be independent
2. **Cleanup**: Always clean up test data
3. **Mocking**: Mock external services (APIs, webhooks)
4. **Assertions**: Use specific, meaningful assertions
5. **Coverage**: Aim for high coverage but focus on critical paths
6. **Speed**: Keep tests fast (mock slow operations)
7. **Documentation**: Add docstrings to complex tests

## Example Test Run Output

```bash
$ pytest tests/test_partner_management.py -v

tests/test_partner_management.py::TestPartnerService::test_generate_partner_code PASSED
tests/test_partner_management.py::TestPartnerService::test_generate_api_credentials PASSED
tests/test_partner_management.py::TestPartnerService::test_hash_secret PASSED
tests/test_partner_management.py::TestPartnerService::test_verify_secret PASSED
tests/test_partner_management.py::TestPartnerService::test_create_partner PASSED
tests/test_partner_management.py::TestPartnerService::test_create_api_key PASSED
tests/test_partner_management.py::TestPartnerService::test_list_api_keys PASSED
tests/test_partner_management.py::TestPartnerService::test_revoke_api_key PASSED
tests/test_partner_management.py::TestPartnerService::test_rotate_api_key PASSED

========================= 9 passed in 2.34s =========================
```

## Next Steps

1. Run tests locally to verify setup
2. Fix any failing tests
3. Add more edge case tests as needed
4. Set up CI/CD pipeline
5. Monitor coverage reports
6. Add performance tests for high-load scenarios
