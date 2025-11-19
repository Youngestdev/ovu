# Redis Setup for Rate Limiting

## Overview

Ovu uses Redis for rate limiting partner API requests. This provides:
- Fast, distributed rate limiting
- Per-partner tracking
- Per-API-key tracking
- Automatic expiration of old data
- Real-time usage statistics

## Installation

### Using Docker (Recommended)

```bash
docker run -d \
  --name ovu-redis \
  -p 6379:6379 \
  redis:7-alpine
```

### Using Homebrew (Mac)

```bash
brew install redis
brew services start redis
```

### Using APT (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

## Configuration

Add to your `.env` file:

```bash
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
# REDIS_PASSWORD=your_password  # Optional
```

## Testing Connection

```bash
# Using redis-cli
redis-cli ping
# Should return: PONG

# Check if Redis is running
redis-cli info server
```

## Rate Limiting Keys

The rate limiter uses the following Redis key patterns:

### Per-Partner Limits
```
rate_limit:partner:{partner_id}:minute:{window}
rate_limit:partner:{partner_id}:day:{date}
```

### Per-API-Key Limits
```
rate_limit:api_key:{key_id}:minute:{window}
rate_limit:api_key:{key_id}:day:{date}
```

## Monitoring

### View Current Rate Limits

```bash
# List all rate limit keys
redis-cli KEYS "rate_limit:*"

# Get specific partner's minute count
redis-cli GET "rate_limit:partner:{partner_id}:minute:{window}"

# Get specific partner's daily count
redis-cli GET "rate_limit:partner:{partner_id}:day:2024-12-20"
```

### Clear Rate Limits (for testing)

```bash
# Clear all rate limit data
redis-cli KEYS "rate_limit:*" | xargs redis-cli DEL

# Clear specific partner's limits
redis-cli DEL "rate_limit:partner:{partner_id}:minute:{window}"
redis-cli DEL "rate_limit:partner:{partner_id}:day:{date}"
```

## Graceful Degradation

If Redis is unavailable, the rate limiter will:
- Log a warning
- Disable rate limiting
- Allow all requests through
- Continue normal operation

This ensures the API remains available even if Redis goes down.

## Production Recommendations

### 1. Use Redis Cluster

For high availability:

```bash
# docker-compose.yml
services:
  redis-master:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  redis-replica:
    image: redis:7-alpine
    command: redis-server --replicaof redis-master 6379
```

### 2. Enable Persistence

Add to `redis.conf`:

```
# Save to disk every 60 seconds if at least 1 key changed
save 60 1

# Use AOF for better durability
appendonly yes
appendfsync everysec
```

### 3. Set Memory Limits

```
# redis.conf
maxmemory 256mb
maxmemory-policy allkeys-lru
```

### 4. Enable Authentication

```bash
# In redis.conf
requirepass your_strong_password

# In .env
REDIS_PASSWORD=your_strong_password
```

### 5. Monitor Performance

```bash
# Monitor Redis in real-time
redis-cli --stat

# Get slow queries
redis-cli SLOWLOG GET 10
```

## Troubleshooting

### Redis Connection Failed

```
WARNING: Redis not available, rate limiting disabled
```

**Solution**: Check if Redis is running:
```bash
redis-cli ping
```

### High Memory Usage

**Solution**: Check memory usage and clear old keys:
```bash
redis-cli INFO memory
redis-cli KEYS "rate_limit:*" | wc -l
```

### Rate Limits Not Working

**Solution**: Verify Redis connection in application logs:
```bash
# Should see: "Rate limiter initialized with Redis"
tail -f logs/app.log | grep "Rate limiter"
```

## API Response Headers

When rate limiting is active, all responses include:

```
X-RateLimit-Limit-Minute: 100
X-RateLimit-Remaining-Minute: 95
X-RateLimit-Limit-Day: 50000
X-RateLimit-Remaining-Day: 49950
X-RateLimit-Reset-Minute: 1703088120
X-RateLimit-Reset-Day: 1703174520
```

## Rate Limit Exceeded Response

```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit-Minute: 100
X-RateLimit-Remaining-Minute: 0
Retry-After: 45

{
  "detail": "Rate limit exceeded. Please try again later."
}
```

## Testing Rate Limits

```bash
# Test with curl
for i in {1..150}; do
  curl -H "X-API-Key: your_key" \
    http://localhost:8000/api/v1/search \
    -s -o /dev/null -w "%{http_code}\n"
done

# Should see 200s followed by 429s after limit is reached
```

## Further Reading

- [Redis Documentation](https://redis.io/documentation)
- [Redis Best Practices](https://redis.io/topics/best-practices)
- [Rate Limiting Patterns](https://redis.io/topics/rate-limiting)
