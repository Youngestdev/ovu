# Fly.io Deployment Guide

This guide walks you through deploying the Ovu Transport application to Fly.io.

## Prerequisites

1. **Install Fly CLI**: Follow the [official installation guide](https://fly.io/docs/hands-on/install-flyctl/)
2. **Create a Fly.io account**: Sign up at [fly.io](https://fly.io)
3. **MongoDB Atlas account**: For the production database (or use Fly Postgres)
4. **Resend account**: For email service
5. **Paystack account**: For payment processing

## Initial Setup

### 1. Login to Fly.io

```bash
fly auth login
```

### 2. Create a New App

```bash
fly launch --no-deploy
```

This will:
- Detect the Dockerfile
- Create a `fly.toml` configuration file (already included)
- Allocate an app name

**Note**: If `fly.toml` already exists, it will use that configuration.

### 3. Set Required Secrets

Fly.io uses secrets for sensitive configuration. Set all required secrets:

```bash
# Application secrets
fly secrets set SECRET_KEY="$(openssl rand -hex 32)"
fly secrets set DATA_ENCRYPTION_KEY="$(openssl rand -hex 32)"

# MongoDB
fly secrets set MONGODB_URL="mongodb+srv://username:password@cluster.mongodb.net/ovu_transport"

# Paystack
fly secrets set PAYSTACK_SECRET_KEY="sk_live_your_secret_key"
fly secrets set PAYSTACK_PUBLIC_KEY="pk_live_your_public_key"
fly secrets set PAYSTACK_WEBHOOK_SECRET="your_webhook_secret"

# Resend (Email)
fly secrets set RESEND_API_KEY="re_your_api_key"
fly secrets set SMTP_FROM_EMAIL="noreply@ovu.ng"

# Optional: Twilio (for SMS/WhatsApp)
fly secrets set TWILIO_ACCOUNT_SID="your_account_sid"
fly secrets set TWILIO_AUTH_TOKEN="your_auth_token"
fly secrets set TWILIO_PHONE_NUMBER="+1234567890"
fly secrets set TWILIO_WHATSAPP_NUMBER="whatsapp:+1234567890"

# Optional: Transport APIs
fly secrets set TRAVU_API_KEY="your_travu_api_key"
fly secrets set TRAVU_API_SECRET="your_travu_api_secret"
fly secrets set NRC_API_KEY="your_nrc_api_key"
fly secrets set NRC_API_SECRET="your_nrc_api_secret"
```

### 4. Add Redis (Optional but Recommended)

If using Celery for background tasks:

```bash
# Option 1: Use Upstash Redis (recommended)
fly redis create

# Option 2: Use Fly Redis
fly redis create --name ovu-redis

# Set the Redis URL
fly secrets set REDIS_URL="redis://your-redis-url"
```

### 5. Configure Domain (ovu.ng)

```bash
# Add your custom domain
fly certs add ovu.ng
fly certs add www.ovu.ng

# Follow the DNS instructions provided
```

Update your DNS records:
- Add an A record pointing to Fly.io's IP address
- Add an AAAA record for IPv6 (optional but recommended)

## Deployment

### Deploy the Application

```bash
fly deploy
```

This will:
1. Build the Docker image
2. Push it to Fly.io's registry
3. Deploy it to your app
4. Run health checks

### Monitor Deployment

```bash
# View logs
fly logs

# Check app status
fly status

# Open the app
fly open
```

## Post-Deployment

### 1. Verify Email Configuration

Ensure your Resend domain (ovu.ng) is verified:
1. Log in to [Resend Dashboard](https://resend.com/domains)
2. Verify DNS records are configured correctly
3. Test email sending via the `/docs` endpoint

### 2. Configure Webhooks

#### Paystack Webhook
Set your webhook URL in Paystack dashboard:
```
https://ovu.ng/api/v1/payments/webhook
```

### 3. Scale Your App

Start with 1 machine, scale as needed:

```bash
# Scale up
fly scale count 2

# Scale memory
fly scale memory 1024

# Scale CPU
fly scale vm shared-cpu-2x
```

### 4. Set Up Monitoring

```bash
# View metrics
fly dashboard

# Set up alerts (in the Fly.io dashboard)
```

## Database Setup

### MongoDB Atlas (Recommended)

1. Create a cluster in MongoDB Atlas
2. Whitelist Fly.io IP addresses (or use `0.0.0.0/0` for testing)
3. Create a database user
4. Get the connection string
5. Set it as `MONGODB_URL` secret

### Alternative: Use Fly Postgres

```bash
fly postgres create --name ovu-db
fly postgres attach ovu-db

# Update your app to use PostgreSQL instead of MongoDB
# (requires code changes)
```

## Environment-Specific Configuration

### Production Settings

The `fly.toml` already sets production defaults:
- `APP_ENV=production`
- `DEBUG=false`
- HTTPS enforced
- Auto-scaling enabled

### Staging Environment

To create a staging environment:

```bash
# Create staging app
fly launch --name ovu-transport-staging --no-deploy

# Set secrets for staging
fly secrets set SECRET_KEY="..." -a ovu-transport-staging
# ... set other secrets

# Deploy to staging
fly deploy -a ovu-transport-staging
```

## Troubleshooting

### View Logs

```bash
# Tail logs
fly logs

# Get last 200 lines
fly logs --lines 200
```

### SSH into Machine

```bash
fly ssh console
```

### Check Health

```bash
curl https://ovu.ng/health
```

### Common Issues

**Issue**: Application fails to start
- **Solution**: Check logs with `fly logs` and verify all required secrets are set

**Issue**: Database connection fails
- **Solution**: Verify MongoDB URL and ensure IP whitelist includes Fly.io IPs

**Issue**: Emails not sending
- **Solution**: Verify Resend API key and domain verification

**Issue**: Health check fails
- **Solution**: Ensure `/health` endpoint returns 200 status

## Costs

Approximate costs for Fly.io:

- **Shared CPU VM (256MB RAM)**: ~$2/month
- **Shared CPU VM (512MB RAM)**: ~$4/month
- **Bandwidth**: $0.02/GB after free tier (100GB/month)

MongoDB Atlas has a free tier (512MB) suitable for development.

## CI/CD Integration

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Fly.io

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: superfly/flyctl-actions/setup-flyctl@master
      
      - run: flyctl deploy --remote-only
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

Add `FLY_API_TOKEN` to your GitHub repository secrets.

## Backup and Recovery

### Database Backups

MongoDB Atlas provides automatic backups. For manual backups:

```bash
# Using mongodump
mongodump --uri="$MONGODB_URL" --out=./backup

# Restore
mongorestore --uri="$MONGODB_URL" ./backup
```

### Application Backup

Your application code is in Git. Secrets are managed by Fly.io.

## Support

- **Fly.io Documentation**: https://fly.io/docs
- **Fly.io Community**: https://community.fly.io
- **Application Issues**: Open an issue on GitHub

## Security Checklist

- [ ] All secrets set via `fly secrets` (not in code)
- [ ] HTTPS enforced (configured in `fly.toml`)
- [ ] MongoDB authentication enabled
- [ ] IP whitelisting configured
- [ ] Resend domain verified with SPF/DKIM
- [ ] Rate limiting enabled
- [ ] Environment set to `production`
- [ ] Debug mode disabled
- [ ] Strong secret keys generated
- [ ] Webhook signatures verified

## Next Steps

1. Configure monitoring and alerting
2. Set up automated backups
3. Configure CDN for static assets
4. Implement log aggregation
5. Set up APM (Application Performance Monitoring)

---

For questions or issues with deployment, contact support at tech@ovu.ng
