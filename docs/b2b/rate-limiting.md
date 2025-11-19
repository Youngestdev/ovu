# Rate Limiting Implementation Summary

## Overview

Implemented comprehensive Redis-based rate limiting for the Ovu B2B API with per-partner and per-API-key tracking.

## Features Implemented

### 1. Redis-Based Rate Limiter
**File**: `app/middleware/rate_limit.py`

- **Per-Partner Tracking**: Tracks requests per partner with configurable limits
- **Per-API-Key Tracking**: Individual API keys can have custom rate limits
- **Dual Time Windows**: 
  - Per-minute limits (default: 60 requests/min)
  - Per-day limits (default: 10,000 requests/day)
- **Graceful Degradation**: Falls back gracefully if Redis is unavailable
- **Usage Statistics**: Built-in method to retrieve usage stats from Redis

### 2. Integration with Authentication
**File**: `app/middleware/auth.py`

Updated `verify_partner_api_key` to:
- Check rate limits before processing requests
- Support both legacy API keys and new APIKey model
- Track usage for both partner and individual API keys
- Raise HTTP 429 when limits exceeded

### 3. Response Headers
**File**: `main.py`

Added middleware to inject rate limit headers on all responses:
```
X-RateLimit-Limit-Minute: 100
X-RateLimit-Remaining-Minute: 95
X-RateLimit-Limit-Day: 50000
X-RateLimit-Remaining-Day: 49950
X-RateLimit-Reset-Minute: 1703088120
X-RateLimit-Reset-Day: 1703174520
```

### 4. Configuration
**Files**: `.env.example`, `docs/guides/redis-setup.md`

- Added Redis configuration options
- Created comprehensive setup guide
- Documented monitoring and troubleshooting

## How It Works

### Rate Limit Check Flow

1. Partner makes API request with `X-API-Key` header
2. `verify_partner_api_key` validates the key
3. Rate limiter checks Redis counters:
   - `rate_limit:partner:{id}:minute:{window}`
   - `rate_limit:partner:{id}:day:{date}`
4. If within limits:
   - Increment counters
   - Add rate limit info to request state
   - Continue processing
5. If exceeded:
   - Raise HTTP 429 with retry headers
   - Include rate limit info in error response

### Redis Key Structure

```
rate_limit:partner:{partner_id}:minute:{window}  # TTL: 120s
rate_limit:partner:{partner_id}:day:{date}       # TTL: 2 days
rate_limit:api_key:{key_id}:minute:{window}      # TTL: 120s
rate_limit:api_key:{key_id}:day:{date}           # TTL: 2 days
```

### API Key Override

If an API key has custom rate limits:
```python
api_key.rate_limit_per_minute = 200  # Override partner's 100
```

The system uses the API key's limit instead of the partner's default.

## Testing

### Start Redis

```bash
docker run -d --name ovu-redis -p 6379:6379 redis:7-alpine
```

### Test Rate Limiting

```bash
# Make 150 requests (should hit limit at 60)
for i in {1..150}; do
  curl -H "X-API-Key: your_key" \
    http://localhost:8000/api/v1/search \
    -s -o /dev/null -w "%{http_code}\n"
done
```

### Monitor Redis

```bash
# Watch rate limit keys
redis-cli KEYS "rate_limit:*"

# Get current count
redis-cli GET "rate_limit:partner:123:minute:28123456"
```

## Error Response

When rate limit is exceeded:

```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit-Minute: 100
X-RateLimit-Remaining-Minute: 0
X-RateLimit-Limit-Day: 50000
X-RateLimit-Remaining-Day: 49850
X-RateLimit-Reset-Minute: 1703088120
X-RateLimit-Reset-Day: 1703174520
Retry-After: 45

{
  "detail": "Rate limit exceeded. Please try again later."
}
```

## Production Considerations

1. **Redis Cluster**: Use Redis cluster for high availability
2. **Monitoring**: Set up alerts for rate limit violations
3. **Tuning**: Adjust limits based on partner tiers
4. **Persistence**: Enable Redis persistence (AOF)
5. **Memory**: Set `maxmemory` and `maxmemory-policy`

## Dependencies Added

- `redis==5.0.1` - Python Redis client

## Files Modified

1. `app/middleware/rate_limit.py` - Complete rewrite with Redis
2. `app/middleware/auth.py` - Added rate limit checks
3. `main.py` - Added rate limit headers middleware
4. `.env.example` - Added Redis configuration
5. `requirements.txt` - Added redis package
6. `docs/guides/redis-setup.md` - Setup and monitoring guide
