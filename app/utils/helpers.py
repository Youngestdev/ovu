"""
Utility functions
"""
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional


def generate_reference(prefix: str = "REF") -> str:
    """Generate a unique reference code"""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    random_part = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    return f"{prefix}-{timestamp}-{random_part}"


def generate_api_key() -> str:
    """Generate a secure API key"""
    return secrets.token_urlsafe(32)


def generate_api_secret() -> str:
    """Generate a secure API secret"""
    return secrets.token_urlsafe(48)


def calculate_commission(amount: float, percentage: float) -> float:
    """Calculate commission amount"""
    return round(amount * (percentage / 100), 2)


def format_currency(amount: float, currency: str = "NGN") -> str:
    """Format currency amount"""
    return f"{currency} {amount:,.2f}"


def parse_phone_number(phone: str) -> str:
    """Parse and format phone number"""
    # Remove all non-digit characters
    digits = ''.join(filter(str.isdigit, phone))
    
    # Add country code if missing (assuming Nigeria)
    if len(digits) == 10:
        return f"+234{digits}"
    elif len(digits) == 11 and digits.startswith('0'):
        return f"+234{digits[1:]}"
    elif digits.startswith('234'):
        return f"+{digits}"
    
    return phone


def calculate_expiry_date(days: int = 7) -> datetime:
    """Calculate expiry date"""
    return datetime.utcnow() + timedelta(days=days)
