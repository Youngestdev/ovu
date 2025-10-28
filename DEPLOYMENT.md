# Deployment Guide

## Production Deployment Checklist

### Pre-Deployment

- [ ] Update all API keys in `.env` file
- [ ] Configure production MongoDB instance
- [ ] Set up Redis instance
- [ ] Configure Paystack production keys
- [ ] Set up Twilio for SMS/WhatsApp
- [ ] Configure SMTP for email
- [ ] Update CORS origins for production domains
- [ ] Generate strong SECRET_KEY
- [ ] Enable HTTPS/SSL certificates
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy

### Environment Variables

Required production environment variables:

```bash
# Application
APP_ENV=production
DEBUG=False
SECRET_KEY=<strong-random-key>

# MongoDB
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net

# APIs
TRAVU_API_KEY=<production-key>
NRC_API_KEY=<production-key>

# Paystack
PAYSTACK_SECRET_KEY=sk_live_...
PAYSTACK_PUBLIC_KEY=pk_live_...

# Security
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

## Deployment Options

### Option 1: Docker Compose (Recommended for VPS)

1. Install Docker and Docker Compose on your server
2. Clone the repository
3. Create production `.env` file
4. Run:
```bash
docker-compose up -d
```

### Option 2: Kubernetes

1. Build and push Docker image:
```bash
docker build -t ovu-transport:latest .
docker tag ovu-transport:latest your-registry/ovu-transport:latest
docker push your-registry/ovu-transport:latest
```

2. Create Kubernetes manifests (example):

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ovu-transport
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ovu-transport
  template:
    metadata:
      labels:
        app: ovu-transport
    spec:
      containers:
      - name: ovu-transport
        image: your-registry/ovu-transport:latest
        ports:
        - containerPort: 8000
        env:
        - name: MONGODB_URL
          valueFrom:
            secretKeyRef:
              name: ovu-secrets
              key: mongodb-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: ovu-secrets
              key: secret-key
---
apiVersion: v1
kind: Service
metadata:
  name: ovu-transport-service
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
  selector:
    app: ovu-transport
```

3. Apply manifests:
```bash
kubectl apply -f deployment.yaml
```

### Option 3: Cloud Platforms

#### AWS Elastic Beanstalk
```bash
eb init -p docker ovu-transport
eb create ovu-transport-prod
eb deploy
```

#### Google Cloud Run
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/ovu-transport
gcloud run deploy ovu-transport \
  --image gcr.io/PROJECT_ID/ovu-transport \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Azure Container Instances
```bash
az container create \
  --resource-group ovu-rg \
  --name ovu-transport \
  --image your-registry/ovu-transport:latest \
  --dns-name-label ovu-transport \
  --ports 8000
```

#### Heroku
```bash
heroku create ovu-transport
heroku container:push web
heroku container:release web
```

## Database Setup

### MongoDB Atlas (Recommended)

1. Create MongoDB Atlas cluster
2. Create database user
3. Whitelist IP addresses or use 0.0.0.0/0 for all
4. Get connection string
5. Update MONGODB_URL in `.env`

### Self-Hosted MongoDB

1. Install MongoDB 7.0+
2. Configure authentication
3. Enable replication for high availability
4. Set up automatic backups
5. Configure firewall rules

## SSL/TLS Configuration

### Using Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Get SSL certificate:
```bash
certbot --nginx -d yourdomain.com
```

## Monitoring and Logging

### Application Monitoring

Integrate with monitoring services:
- Sentry for error tracking
- New Relic for APM
- DataDog for infrastructure monitoring

Add to requirements.txt:
```
sentry-sdk[fastapi]
```

Configure in main.py:
```python
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    environment=settings.APP_ENV,
    traces_sample_rate=1.0,
)
```

### Log Aggregation

Use services like:
- AWS CloudWatch
- Google Cloud Logging
- ELK Stack (Elasticsearch, Logstash, Kibana)

### Health Checks

Configure health check endpoint monitoring:
- Uptime monitoring (UptimeRobot, Pingdom)
- Response time tracking
- Alert on failures

## Performance Optimization

### Database Indexing

Ensure proper indexes are created:
```python
# Already configured in models
# MongoDB will create indexes on startup
```

### Caching

Add Redis caching for frequent queries:
```python
# Add to requirements.txt
redis

# Implement caching in services
import redis
cache = redis.Redis(host='localhost', port=6379, db=0)
```

### Load Balancing

Use load balancer to distribute traffic:
- AWS Application Load Balancer
- Google Cloud Load Balancing
- Nginx load balancing
- HAProxy

## Backup Strategy

### MongoDB Backups

Automated backups:
```bash
# Daily backup script
mongodump --uri="$MONGODB_URL" --out=/backups/$(date +%Y%m%d)

# Upload to S3
aws s3 cp /backups/ s3://your-bucket/backups/ --recursive
```

### Application State

- Store uploaded files in S3 or similar
- Backup environment configurations
- Document recovery procedures

## Security Hardening

### Application Security

1. Enable rate limiting (already implemented)
2. Use strong JWT secrets
3. Implement IP whitelisting for admin endpoints
4. Regular dependency updates
5. Security headers

Add security headers:
```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
)
```

### Database Security

1. Use strong passwords
2. Enable MongoDB authentication
3. Use TLS/SSL for connections
4. Regular security audits
5. Principle of least privilege for database users

### API Security

1. API key rotation policy
2. Webhook signature verification (implemented)
3. Input validation (implemented with Pydantic)
4. SQL injection prevention (MongoDB queries)
5. CSRF protection for web interfaces

## Scaling Strategies

### Horizontal Scaling

1. Run multiple app instances
2. Use load balancer
3. Stateless application design
4. Session management with Redis

### Database Scaling

1. MongoDB sharding for large datasets
2. Read replicas for read-heavy workloads
3. Connection pooling
4. Query optimization

### Caching Strategy

1. Cache search results (short TTL)
2. Cache static data (longer TTL)
3. Invalidate cache on updates
4. Use Redis for distributed caching

## Compliance

### PCI-DSS Compliance

- No credit card data stored
- All payments through Paystack
- Secure communication (HTTPS)
- Access logging
- Regular security audits

### NDPA Compliance

- Data encryption at rest and in transit
- User consent for data collection
- Right to data deletion
- Data breach notification procedures
- Privacy policy

## Rollback Procedures

### Application Rollback

Docker:
```bash
docker-compose down
docker-compose up -d --build <previous-tag>
```

Kubernetes:
```bash
kubectl rollout undo deployment/ovu-transport
```

### Database Migration Rollback

Keep migration scripts versioned:
```bash
# In case of issues
python manage.py migrate previous_version
```

## Post-Deployment

### Verification

1. Check health endpoint
2. Test critical user flows
3. Verify database connections
4. Check external API integrations
5. Monitor error rates
6. Verify payment processing

### Monitoring

Set up alerts for:
- Application errors
- High response times
- Failed payments
- Database issues
- Low disk space
- High CPU/memory usage

## Support and Maintenance

### Regular Tasks

- [ ] Daily: Check error logs
- [ ] Weekly: Review system metrics
- [ ] Monthly: Security updates
- [ ] Monthly: Dependency updates
- [ ] Quarterly: Performance review
- [ ] Quarterly: Security audit

### Documentation

Maintain documentation for:
- Deployment procedures
- Configuration changes
- API changes
- Known issues
- Troubleshooting guides

## Troubleshooting

### Common Issues

#### Application won't start
```bash
# Check logs
docker-compose logs app

# Check environment variables
docker-compose config

# Verify MongoDB connection
docker-compose exec app python -c "from pymongo import MongoClient; print(MongoClient(os.getenv('MONGODB_URL')).server_info())"
```

#### High memory usage
```bash
# Check container stats
docker stats

# Increase container memory limit
# Update docker-compose.yml
```

#### Payment webhook failures
```bash
# Verify webhook URL is accessible
# Check Paystack webhook signature
# Review webhook logs
```

## Disaster Recovery

### Backup Restoration

1. Stop application
2. Restore MongoDB from backup
3. Verify data integrity
4. Restart application
5. Test critical functions

### Incident Response

1. Identify issue
2. Assess impact
3. Implement fix or rollback
4. Communicate with users
5. Post-mortem analysis
6. Update procedures

## Contact and Support

- Technical Issues: tech@ovutransport.com
- Security Issues: security@ovutransport.com
- Emergency: +234-xxx-xxx-xxxx
