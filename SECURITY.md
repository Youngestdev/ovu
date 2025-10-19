# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: **security@ovutransport.com**

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

### What to Include

Please include the following information:
- Type of vulnerability
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

### Response Process

1. **Acknowledgment**: We will acknowledge receipt of your vulnerability report within 48 hours
2. **Investigation**: We will investigate and validate the vulnerability
3. **Fix Development**: We will develop a fix for the vulnerability
4. **Disclosure**: We will coordinate disclosure with you
5. **Release**: We will release a security update

## Security Measures

### Authentication & Authorization
- JWT-based authentication with secure token generation
- Role-based access control (RBAC)
- API key authentication for partners
- Password hashing using bcrypt
- Token expiration and refresh mechanisms

### Data Protection
- All sensitive data encrypted in transit (HTTPS/TLS)
- Database connection encryption
- API keys and secrets stored securely
- No storage of credit card information (PCI-DSS compliant)
- Password hashing with strong algorithms

### API Security
- Rate limiting to prevent abuse
- Input validation using Pydantic
- SQL injection prevention (using MongoDB)
- CORS configuration
- Webhook signature verification
- Request size limits

### Compliance
- **PCI-DSS**: Payment data handled by Paystack (Level 1 certified)
- **NDPA**: Nigerian Data Protection Act compliance measures
  - Data encryption
  - Access controls
  - Audit logging
  - User consent mechanisms
  - Right to deletion

### Infrastructure Security
- Docker container isolation
- Environment variable management
- Secure secret management
- Regular dependency updates
- Security scanning in CI/CD

## Security Best Practices for Deployment

### Environment Variables
```bash
# Use strong, random secrets
SECRET_KEY=$(openssl rand -hex 32)
DATA_ENCRYPTION_KEY=$(openssl rand -hex 32)

# Rotate secrets regularly
# Never commit .env files to version control
```

### Database Security
```bash
# Enable MongoDB authentication
# Use strong passwords
# Enable TLS/SSL for connections
# Restrict network access
# Regular backups
```

### API Security
```bash
# Use HTTPS in production
# Configure CORS properly
# Enable rate limiting
# Implement request logging
# Monitor for suspicious activity
```

### Dependencies
```bash
# Regularly update dependencies
pip list --outdated

# Check for known vulnerabilities
pip install safety
safety check

# Use dependabot for automatic updates
```

## Known Security Considerations

### Payment Processing
- All payment processing goes through Paystack
- No credit card data is stored in the application
- Webhook signatures are verified
- Payment references are unique and unpredictable

### User Data
- Passwords are hashed using bcrypt
- Personal information is encrypted
- User data access is logged
- Users can request data deletion

### API Keys
- API keys are generated using secure random functions
- Keys can be rotated
- Failed authentication attempts are logged
- Rate limiting prevents brute force attacks

## Security Updates

We will publish security advisories for:
- Critical vulnerabilities
- High severity issues
- Issues affecting multiple versions

Subscribe to security advisories on our GitHub repository.

## Bug Bounty Program

We currently do not have a formal bug bounty program, but we appreciate security researchers' efforts and will:
- Acknowledge your contribution
- Credit you in release notes (if desired)
- Provide swag/recognition for significant findings

## Security Contact

- **Email**: security@ovutransport.com
- **PGP Key**: Available on request
- **Response Time**: Within 48 hours

## Disclosure Policy

- We follow coordinated disclosure
- We will work with you to understand and fix the issue
- We will credit you for the discovery (unless you prefer to remain anonymous)
- We ask that you do not publicly disclose the vulnerability until we have released a fix

## Security Checklist for Contributors

Before submitting code:
- [ ] No hardcoded secrets or credentials
- [ ] Input validation implemented
- [ ] Proper error handling (don't leak sensitive info)
- [ ] Authentication/authorization checked
- [ ] Dependencies are up to date
- [ ] Security implications considered
- [ ] Tests include security scenarios

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [MongoDB Security](https://docs.mongodb.com/manual/security/)
- [PCI-DSS Compliance](https://www.pcisecuritystandards.org/)
- [NDPA Guidelines](https://nitda.gov.ng/ndpr/)

## Past Security Advisories

None at this time. This is the initial release.

---

**Note**: This security policy is subject to change. Please check back regularly for updates.

Last updated: 2024-12-20
