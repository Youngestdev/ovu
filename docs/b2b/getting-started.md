# B2B Integration Guide

Welcome to the Ovu Transport Aggregator B2B API! This guide will help you integrate Ovu's transport booking services into your platform.

## Overview

Ovu provides a comprehensive B2B API that allows businesses to:
- Search across flights, buses, and trains
- Create and manage bookings
- Process payments
- Receive real-time updates via webhooks
- Track usage and analytics

## Getting Started

### 1. Register as a Business Partner

Contact our team to register as a business partner:
- Email: partnerships@ovutransport.com
- Provide your company information and use case

### 2. Receive API Credentials

Once approved, you'll receive:
- **Partner Code**: Your unique identifier (e.g., `TRAVELAG-ABC123`)
- **API Key**: Public key for authentication (e.g., `ovu_live_...`)
- **API Secret**: Secret key for authentication (e.g., `sk_live_...`)

> **Important**: Store your API secret securely. It will only be shown once!

### 3. Authentication

All API requests must include your API key in the header:

```bash
X-API-Key: your_api_key_here
```

Example request:
```bash
curl -X POST "https://api.ovutransport.com/api/v1/search" \
  -H "X-API-Key: ovu_live_abc123..." \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "Lagos",
    "destination": "Abuja",
    "departure_date": "2024-12-25T08:00:00",
    "passengers": 2,
    "transport_types": ["flight", "bus", "train"]
  }'
```

## Core Features

### Search Transport Options

Search across all transport types with a single API call:

**Endpoint**: `POST /api/v1/search`

**Request**:
```json
{
  "origin": "Lagos",
  "destination": "Abuja",
  "departure_date": "2024-12-25T08:00:00",
  "passengers": 2,
  "transport_types": ["flight", "bus", "train"]
}
```

**Response**:
```json
[
  {
    "transport_type": "flight",
    "provider": "travu",
    "origin": "Lagos",
    "destination": "Abuja",
    "departure_date": "2024-12-25T08:00:00",
    "arrival_date": "2024-12-25T09:30:00",
    "price": 45000.0,
    "currency": "NGN",
    "available_seats": 50,
    "provider_reference": "TRV-FL-001"
  }
]
```

### Create Booking

**Endpoint**: `POST /api/v1/bookings`

**Request**:
```json
{
  "provider_reference": "TRV-FL-001",
  "transport_type": "flight",
  "passengers": [
    {
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com",
      "phone": "+2348012345678",
      "date_of_birth": "1990-01-01T00:00:00",
      "gender": "male"
    }
  ]
}
```

**Response**:
```json
{
  "id": "64a1b2c3d4e5f6g7h8i9j0k1",
  "booking_reference": "BKG-20241225120000-ABC123",
  "status": "pending",
  "transport_type": "flight",
  "total_passengers": 1,
  "total_price": 47000.0,
  "currency": "NGN"
}
```

### Get Booking Details

**Endpoint**: `GET /api/v1/bookings/{booking_reference}`

## API Key Management

### Generate Additional API Keys

Create multiple API keys for different environments or applications:

**Endpoint**: `POST /api/v1/partners/api-keys`

**Request**:
```json
{
  "name": "Production Key",
  "scopes": ["search", "booking", "payment"],
  "expires_in_days": 365,
  "allowed_ips": ["203.0.113.0", "203.0.113.1"]
}
```

### List API Keys

**Endpoint**: `GET /api/v1/partners/api-keys`

### Revoke API Key

**Endpoint**: `DELETE /api/v1/partners/api-keys/{key_id}`

### Rotate API Key

**Endpoint**: `PUT /api/v1/partners/api-keys/{key_id}/rotate`

## Webhooks

Receive real-time notifications for booking and payment events.

### Configure Webhooks

**Endpoint**: `PUT /api/v1/partners/webhooks`

**Request**:
```json
{
  "webhook_url": "https://your-domain.com/webhooks/ovu",
  "webhook_events": [
    "booking.created",
    "booking.confirmed",
    "payment.success"
  ],
  "webhook_secret": "your_webhook_secret_min_32_chars"
}
```

### Webhook Events

Available events:
- `booking.created` - New booking created
- `booking.confirmed` - Booking confirmed
- `booking.cancelled` - Booking cancelled
- `payment.success` - Payment successful
- `payment.failed` - Payment failed
- `ticket.generated` - E-ticket generated

### Webhook Payload

```json
{
  "event": "booking.created",
  "timestamp": "2024-12-20T12:00:00Z",
  "partner_code": "TRAVELAG-ABC123",
  "data": {
    "booking_reference": "BKG-20241225120000-ABC123",
    "status": "pending",
    "transport_type": "flight"
  }
}
```

### Webhook Signature Verification

All webhooks include an `X-Ovu-Signature` header with HMAC-SHA256 signature:

```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

### Test Webhook

**Endpoint**: `POST /api/v1/partners/webhooks/test`

## Usage Analytics

### Get Usage Statistics

**Endpoint**: `GET /api/v1/partners/usage?days=30`

**Response**:
```json
{
  "partner_id": "64a1b2c3d4e5f6g7h8i9j0k1",
  "partner_name": "Travel Agency Inc",
  "period_start": "2024-11-20T00:00:00Z",
  "period_end": "2024-12-20T00:00:00Z",
  "total_requests": 15420,
  "total_bookings": 342,
  "total_revenue": 15750000.0,
  "active_api_keys": 3,
  "total_api_keys": 5
}
```

## Rate Limits

Default rate limits:
- **60 requests per minute**
- **10,000 requests per day**

Rate limits can be customized based on your business tier. Contact us for higher limits.

### Rate Limit Headers

All responses include rate limit information:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1640000000
```

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message",
  "type": "error_type"
}
```

### HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized (invalid API key)
- `403` - Forbidden (inactive partner)
- `404` - Not Found
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error

## Best Practices

### Security

1. **Never expose your API secret** in client-side code
2. **Use HTTPS** for all API requests
3. **Rotate API keys** regularly
4. **Implement webhook signature verification**
5. **Use IP whitelisting** for production keys

### Performance

1. **Cache search results** appropriately
2. **Implement retry logic** with exponential backoff
3. **Use pagination** for list endpoints
4. **Monitor rate limits** and adjust request frequency

### Integration

1. **Test in sandbox** before production
2. **Handle all webhook events** gracefully
3. **Log all API interactions** for debugging
4. **Implement proper error handling**
5. **Monitor usage analytics** regularly

## Support

### Technical Support

- **Email**: tech@ovutransport.com
- **Documentation**: https://docs.ovutransport.com
- **Status Page**: https://status.ovutransport.com

### Business Inquiries

- **Email**: partnerships@ovutransport.com
- **Phone**: +234-xxx-xxx-xxxx

## Next Steps

1. Review the [API Reference](../API_DOCUMENTATION.md)
2. Check out [code examples](examples.md)
3. Learn about [webhooks](webhooks.md)
4. Understand [rate limits](rate-limits.md)

---

**Ready to get started?** Contact our partnerships team to begin your integration journey!
