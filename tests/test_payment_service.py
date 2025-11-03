"""
Tests for payment service with environment-based behavior
"""
import pytest
from unittest.mock import patch, MagicMock
from app.services.payment_service import PaystackService
from app.core.config import Settings


@pytest.mark.asyncio
async def test_paystack_service_dev_environment():
    """Test that PaystackService behaves correctly in development"""
    with patch('app.services.payment_service.settings') as mock_settings:
        mock_settings.is_development = True
        mock_settings.PAYSTACK_SECRET_KEY = "sk_test_12345"
        
        service = PaystackService()
        assert service.base_url == "https://api.paystack.co"
        assert service.secret_key == "sk_test_12345"


@pytest.mark.asyncio
async def test_paystack_service_prod_environment():
    """Test that PaystackService behaves correctly in production"""
    with patch('app.services.payment_service.settings') as mock_settings:
        mock_settings.is_development = False
        mock_settings.is_production = True
        mock_settings.PAYSTACK_SECRET_KEY = "sk_live_12345"
        
        service = PaystackService()
        assert service.base_url == "https://api.paystack.co"
        assert service.secret_key == "sk_live_12345"


def test_settings_is_production():
    """Test production environment detection"""
    settings = Settings(
        APP_ENV="production",
        SECRET_KEY="test",
        MONGODB_URL="mongodb://localhost",
        PAYSTACK_SECRET_KEY="sk_test",
        PAYSTACK_PUBLIC_KEY="pk_test",
        PAYSTACK_WEBHOOK_SECRET="test",
        RESEND_API_KEY="test",
        SMTP_FROM_EMAIL="test@example.com",
        DATA_ENCRYPTION_KEY="test"
    )
    assert settings.is_production is True
    assert settings.is_development is False


def test_settings_is_development():
    """Test development environment detection"""
    settings = Settings(
        APP_ENV="development",
        SECRET_KEY="test",
        MONGODB_URL="mongodb://localhost",
        PAYSTACK_SECRET_KEY="sk_test",
        PAYSTACK_PUBLIC_KEY="pk_test",
        PAYSTACK_WEBHOOK_SECRET="test",
        RESEND_API_KEY="test",
        SMTP_FROM_EMAIL="test@example.com",
        DATA_ENCRYPTION_KEY="test"
    )
    assert settings.is_development is True
    assert settings.is_production is False


def test_settings_prod_alias():
    """Test that 'prod' is recognized as production"""
    settings = Settings(
        APP_ENV="prod",
        SECRET_KEY="test",
        MONGODB_URL="mongodb://localhost",
        PAYSTACK_SECRET_KEY="sk_test",
        PAYSTACK_PUBLIC_KEY="pk_test",
        PAYSTACK_WEBHOOK_SECRET="test",
        RESEND_API_KEY="test",
        SMTP_FROM_EMAIL="test@example.com",
        DATA_ENCRYPTION_KEY="test"
    )
    assert settings.is_production is True
    assert settings.is_development is False


def test_settings_dev_alias():
    """Test that 'dev' is recognized as development"""
    settings = Settings(
        APP_ENV="dev",
        SECRET_KEY="test",
        MONGODB_URL="mongodb://localhost",
        PAYSTACK_SECRET_KEY="sk_test",
        PAYSTACK_PUBLIC_KEY="pk_test",
        PAYSTACK_WEBHOOK_SECRET="test",
        RESEND_API_KEY="test",
        SMTP_FROM_EMAIL="test@example.com",
        DATA_ENCRYPTION_KEY="test"
    )
    assert settings.is_development is True
    assert settings.is_production is False
