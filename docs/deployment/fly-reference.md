# Fly.io Quick Reference

Quick commands for managing the Ovu Transport application on Fly.io.

## Essential Commands

### Deployment
```bash
fly deploy                    # Deploy the app
fly deploy --remote-only      # Build on Fly's servers (recommended for slow internet)
fly deploy --ha=false         # Deploy without high availability (saves costs)
```

### Monitoring
```bash
fly status                    # Check app status
fly logs                      # View logs (live tail)
fly logs -a ovu-transport     # Logs for specific app
fly dashboard                 # Open web dashboard
fly open                      # Open app in browser
```

### Secrets Management
```bash
fly secrets list              # List secret names (not values)
fly secrets set KEY=value     # Set a secret
fly secrets unset KEY         # Remove a secret
```

### Scaling
```bash
fly scale count 2             # Scale to 2 machines
fly scale count 1             # Scale down to 1 machine
fly scale memory 512          # Set memory to 512MB
fly scale vm shared-cpu-1x    # Change VM size
```

### SSH & Debugging
```bash
fly ssh console               # SSH into running machine
fly ssh console -C "ls -la"   # Run a command
fly ssh console -C "cat .env" # View environment variables
```

### App Management
```bash
fly apps list                 # List all your apps
fly apps destroy ovu-transport # Delete the app (careful!)
fly regions list              # List available regions
fly regions add lhr           # Add London region
```

### Certificates & Domains
```bash
fly certs list                # List SSL certificates
fly certs add ovu.ng          # Add custom domain
fly certs show ovu.ng         # Show cert details
fly certs check ovu.ng        # Check certificate status
```

### Database & Services
```bash
fly redis list                # List Redis instances
fly postgres list             # List Postgres databases
fly redis create              # Create Redis instance
```

### Releases & Rollback
```bash
fly releases                  # List app releases
fly deploy --image registry.fly.io/ovu-transport:deployment-01XXXXXX  # Rollback to specific version
```

## Environment-Specific Commands

### Staging
```bash
fly deploy -a ovu-transport-staging
fly logs -a ovu-transport-staging
fly ssh console -a ovu-transport-staging
```

### Production
```bash
fly deploy -a ovu-transport
fly logs -a ovu-transport
```

## Useful Flags

- `-a APP_NAME` - Target specific app
- `--config fly.staging.toml` - Use different config file
- `--remote-only` - Build remotely
- `--local-only` - Build locally
- `--detach` - Don't wait for deployment to complete

## Quick Troubleshooting

### App won't start
```bash
fly logs                      # Check error logs
fly ssh console               # SSH and investigate
fly secrets list              # Verify secrets are set
```

### Slow performance
```bash
fly scale memory 1024         # Increase memory
fly scale count 2             # Add more machines
fly regions add lhr jnb       # Add regions closer to users
```

### Database connection issues
```bash
fly ssh console -C "ping your-mongodb-url"
fly secrets list              # Check MONGODB_URL is set
```

## Best Practices

1. **Always use secrets for sensitive data**
   ```bash
   fly secrets set API_KEY=xxx
   ```

2. **Enable auto-start/stop for cost savings**
   Already configured in `fly.toml`

3. **Use --remote-only for deployment**
   ```bash
   fly deploy --remote-only
   ```

4. **Monitor regularly**
   ```bash
   fly dashboard
   ```

5. **Test before production**
   ```bash
   fly deploy -a ovu-transport-staging
   ```

## Support

- Fly.io Docs: https://fly.io/docs
- Community: https://community.fly.io
- Status: https://status.flyio.net

---

Save this file as a bookmark for quick reference!
