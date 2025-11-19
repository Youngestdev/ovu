# B2B Partner API Endpoints

## Partner Management (Admin Only)

### Create Partner
```http
POST /api/v1/partners
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "name": "Travel Agency Inc",
  "email": "contact@travelagency.com",
  "phone": "+2348012345678",
  "website": "https://travelagency.com",
  "company_name": "Travel Agency Inc",
  "business_type": "travel_agency",
  "tax_id": "12345678",
  "rate_limit_per_minute": 100,
  "rate_limit_per_day": 50000
}
```

Response (201):
```json
{
  "partner": {
    "id": "64a1b2c3d4e5f6g7h8i9j0k1",
    "partner_code": "TRAVELAG-ABC123",
    "name": "Travel Agency Inc",
    "email": "contact@travelagency.com",
    "status": "active"
  },
  "credentials": {
    "api_key": "ovu_live_abc123def456...",
    "api_secret": "sk_live_xyz789uvw456...",
    "note": "Store these credentials securely. The secret will not be shown again."
  }
}
```

## Partner Self-Service

### Get Current Partner Info
```http
GET /api/v1/partners/me
X-API-Key: <partner_api_key>
```

### Update Partner Info
```http
PUT /api/v1/partners/me
X-API-Key: <partner_api_key>
Content-Type: application/json

{
  "name": "Updated Name",
  "phone": "+2348012345679",
  "rate_limit_per_minute": 120
}
```

## API Key Management

### Create New API Key
```http
POST /api/v1/partners/api-keys
X-API-Key: <partner_api_key>
Content-Type: application/json

{
  "name": "Production Key",
  "scopes": ["search", "booking", "payment"],
  "rate_limit_per_minute": 100,
  "expires_in_days": 365,
  "allowed_ips": ["203.0.113.0"]
}
```

Response (201):
```json
{
  "key_id": "key_abc123",
  "name": "Production Key",
  "api_key": "ovu_live_newkey123...",
  "api_secret": "sk_live_newsecret456...",
  "status": "active",
  "scopes": ["search", "booking", "payment"],
  "created_at": "2024-12-20T12:00:00Z",
  "expires_at": "2025-12-20T12:00:00Z"
}
```

### List API Keys
```http
GET /api/v1/partners/api-keys
X-API-Key: <partner_api_key>
```

### Revoke API Key
```http
DELETE /api/v1/partners/api-keys/{key_id}
X-API-Key: <partner_api_key>
```

### Rotate API Key
```http
PUT /api/v1/partners/api-keys/{key_id}/rotate
X-API-Key: <partner_api_key>
```

Response (200):
```json
{
  "old_key_id": "key_abc123",
  "new_key_id": "key_xyz789",
  "new_api_key": "ovu_live_rotated123...",
  "new_api_secret": "sk_live_rotatedsecret456...",
  "message": "API key rotated successfully. Old key has been revoked."
}
```

## Usage Analytics

### Get Usage Statistics
```http
GET /api/v1/partners/usage?days=30
X-API-Key: <partner_api_key>
```

Response (200):
```json
{
  "partner_id": "64a1b2c3d4e5f6g7h8i9j0k1",
  "partner_name": "Travel Agency Inc",
  "period_start": "2024-11-20T00:00:00Z",
  "period_end": "2024-12-20T00:00:00Z",
  "total_requests": 15420,
  "total_bookings": 342,
  "total_revenue": 15750000.0,
  "daily_stats": [
    {
      "date": "2024-12-01",
      "total_requests": 520,
      "search_requests": 380,
      "booking_requests": 120,
      "payment_requests": 20,
      "successful_requests": 510,
      "failed_requests": 10
    }
  ],
  "current_rate_limit_per_minute": 100,
  "current_rate_limit_per_day": 50000,
  "requests_today": 1250,
  "active_api_keys": 3,
  "total_api_keys": 5
}
```

## Webhook Configuration

### Configure Webhooks
```http
PUT /api/v1/partners/webhooks
X-API-Key: <partner_api_key>
Content-Type: application/json

{
  "webhook_url": "https://your-domain.com/webhooks/ovu",
  "webhook_events": [
    "booking.created",
    "booking.confirmed",
    "payment.success"
  ],
  "webhook_secret": "your_webhook_secret_min_32_chars_long"
}
```

### Get Webhook Configuration
```http
GET /api/v1/partners/webhooks
X-API-Key: <partner_api_key>
```

### Test Webhook
```http
POST /api/v1/partners/webhooks/test
X-API-Key: <partner_api_key>
Content-Type: application/json

{
  "event_type": "booking.created"
}
```

Response (200):
```json
{
  "success": true,
  "message": "Webhook test successful",
  "status_code": 200,
  "response_time_ms": 145.5
}
```

## Webhook Events

Available webhook events:
- `booking.created` - New booking created
- `booking.confirmed` - Booking confirmed by provider
- `booking.cancelled` - Booking cancelled
- `payment.success` - Payment completed successfully
- `payment.failed` - Payment failed
- `ticket.generated` - E-ticket generated and ready

### Webhook Payload Format

All webhooks are sent as POST requests with the following format:

```json
{
  "event": "booking.created",
  "timestamp": "2024-12-20T12:00:00Z",
  "partner_code": "TRAVELAG-ABC123",
  "data": {
    "booking_reference": "BKG-20241225120000-ABC123",
    "status": "pending",
    "transport_type": "flight",
    "total_price": 47000.0,
    "currency": "NGN"
  }
}
```

### Webhook Signature Verification

All webhooks include an `X-Ovu-Signature` header containing an HMAC-SHA256 signature:

```python
import hmac
import hashlib

def verify_webhook_signature(payload, signature, secret):
    expected_signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_signature, signature)
```

## Rate Limits

Partner API rate limits are configurable per partner:
- Default: 60 requests/minute, 10,000 requests/day
- Can be customized based on business tier
- Rate limit information included in response headers:
  - `X-RateLimit-Limit`: Total requests allowed
  - `X-RateLimit-Remaining`: Requests remaining
  - `X-RateLimit-Reset`: Unix timestamp when limit resets
