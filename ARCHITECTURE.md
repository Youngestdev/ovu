# System Architecture

## Overview

Ovu Transport Aggregator is a comprehensive FastAPI-based platform that unifies multiple transport booking systems (flights, buses, and trains) into a single, easy-to-use API.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │   Web    │  │  Mobile  │  │ Partners │  │ Operators│       │
│  │   App    │  │   App    │  │   APIs   │  │Dashboard │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway / Load Balancer                 │
│                         (Nginx / AWS ALB)                        │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Application Layer                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Authentication & Authorization (JWT)                     │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │  Rate Limiting & Security Middleware                      │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │  API Routes                                               │  │
│  │  • Auth   • Bookings   • Payments   • Operators          │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │  Business Logic Services                                  │  │
│  │  • Booking Service  • Payment Service  • Notification     │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
            │                  │                  │
            ▼                  ▼                  ▼
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│   MongoDB      │  │   Redis Cache  │  │  External APIs │
│  (Database)    │  │   & Queue      │  │  • Travu       │
│                │  │                │  │  • NRC         │
│  • Users       │  │  • Sessions    │  │  • Paystack    │
│  • Bookings    │  │  • Cache       │  │  • Twilio      │
│  • Payments    │  │  • Celery      │  └────────────────┘
│  • Tickets     │  └────────────────┘
└────────────────┘
```

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Async Support**: asyncio, uvicorn
- **Database ODM**: Beanie (async MongoDB ODM)
- **Validation**: Pydantic v2
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt (passlib)

### Database & Caching
- **Primary Database**: MongoDB 7.0+
- **Cache**: Redis 7+
- **Task Queue**: Celery with Redis backend

### External Integrations
- **Payment Gateway**: Paystack
- **Flight/Bus API**: Travu
- **Train API**: NRC
- **SMS/WhatsApp**: Twilio
- **Email**: SMTP (configurable)

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Docker Compose / Kubernetes
- **Reverse Proxy**: Nginx
- **SSL/TLS**: Let's Encrypt / Certbot

## System Components

### 1. Core Layer (`app/core/`)

#### Configuration (`config.py`)
- Environment-based configuration using Pydantic Settings
- Centralized settings management
- Type-safe configuration access

#### Database (`database.py`)
- MongoDB connection management
- Beanie ODM initialization
- Connection pooling
- Graceful shutdown handling

#### Security (`security.py`)
- JWT token generation and validation
- Password hashing and verification
- Token expiration management
- Refresh token support

### 2. Data Layer (`app/models/`)

#### User Model
- User authentication and profile
- Role-based access control (Customer, Operator, Partner, Admin)
- Account verification and status tracking

#### Booking Models
- Base Booking model with common fields
- Specialized models for Flight, Bus, and Train bookings
- Passenger information management
- Booking status tracking

#### Payment Models
- Payment records with provider tracking
- Split payment configuration for operators
- Transaction ledger for financial tracking
- Refund support

#### Ticket Model
- E-ticket generation
- QR code data storage
- PDF ticket URLs
- Ticket validation and usage tracking

#### Operator Model
- Transport operator profiles
- Commission configuration
- Paystack subaccount integration
- Verification status

#### Partner Model
- API partner management
- API key and secret storage
- Webhook configuration
- Rate limiting per partner
- Usage tracking

### 3. API Schemas (`app/schemas/`)

Pydantic models for request/response validation:
- Authentication schemas (register, login, token)
- Booking schemas (search, create, response)
- Payment schemas (initialize, webhook, refund)

### 4. Route Layer (`app/routes/`)

#### Authentication Routes (`/api/v1/auth`)
- User registration
- User login
- Token refresh
- Current user info

#### Booking Routes (`/api/v1/bookings`)
- Unified search across all transport types
- Booking creation with passenger management
- User booking history
- Booking details
- Booking cancellation

#### Payment Routes (`/api/v1/payments`)
- Payment initialization
- Payment verification
- Webhook handling
- Refund processing

#### Operator Routes (`/api/v1/operators`)
- Dashboard analytics
- Booking management
- Sales reports
- Payout information

#### Partner Routes (`/api/v1`)
- Partner API search
- Partner booking creation
- Partner booking retrieval

### 5. Service Layer (`app/services/`)

#### Travu Client (`travu_client.py`)
- Flight search and booking
- Bus search and booking
- API authentication
- Error handling and retries

#### NRC Client (`nrc_client.py`)
- Train search and booking
- API authentication
- Schedule management

#### Payment Service (`payment_service.py`)
- Paystack integration
- Transaction initialization
- Split settlement configuration
- Subaccount management
- Refund processing
- Webhook signature verification

#### Notification Service (`notification_service.py`)
- Email notifications via SMTP
- SMS via Twilio
- WhatsApp via Twilio
- Booking confirmations
- Payment notifications
- E-ticket delivery

#### Ticket Service (`ticket_service.py`)
- QR code generation
- PDF ticket generation
- Ticket validation
- Ticket storage and retrieval

### 6. Middleware Layer (`app/middleware/`)

#### Authentication Middleware (`auth.py`)
- JWT token validation
- User authentication dependencies
- Role-based access control
- Partner API key validation

#### Rate Limiting (`rate_limit.py`)
- Per-IP rate limiting
- Per-partner rate limiting
- Configurable limits
- Rate limit headers

### 7. Utilities (`app/utils/`)

#### Helpers (`helpers.py`)
- Reference code generation
- API key generation
- Currency formatting
- Phone number parsing
- Commission calculation

## Data Flow

### Booking Flow

1. **Search Phase**
   ```
   Client → API Gateway → FastAPI
   FastAPI → Travu API (flights, buses)
   FastAPI → NRC API (trains)
   FastAPI → Aggregate Results → Client
   ```

2. **Booking Phase**
   ```
   Client → API Gateway → FastAPI
   FastAPI → Validate User & Auth
   FastAPI → Create Booking in MongoDB
   FastAPI → External Provider API
   FastAPI → Update Booking Status
   FastAPI → Notification Service
   ```

3. **Payment Phase**
   ```
   Client → API Gateway → FastAPI
   FastAPI → Create Payment Record
   FastAPI → Paystack Initialize
   Client → Paystack Checkout
   Paystack → Webhook → FastAPI
   FastAPI → Update Payment & Booking
   FastAPI → Generate Ticket
   FastAPI → Send Notifications
   ```

## Security Architecture

### Authentication & Authorization
- JWT-based stateless authentication
- Refresh token rotation
- Role-based access control (RBAC)
- API key authentication for partners

### Data Security
- Password hashing with bcrypt
- JWT tokens with expiration
- API key rotation support
- Webhook signature verification
- Input validation with Pydantic

### Network Security
- HTTPS/TLS encryption
- CORS configuration
- Rate limiting
- IP whitelisting (configurable)

### Compliance
- PCI-DSS: No card data storage, Paystack handles payments
- NDPA: Data encryption, access controls, audit logging

## Scalability

### Horizontal Scaling
- Stateless application design
- Multiple FastAPI instances behind load balancer
- Session management with Redis
- Database read replicas

### Vertical Scaling
- Connection pooling
- Async/await for non-blocking I/O
- Efficient database queries
- Caching strategy

### Caching Strategy
- Search results (short TTL)
- Static data (operators, routes)
- User sessions
- Rate limiting counters

## Monitoring & Observability

### Health Checks
- `/health` endpoint for basic health
- Database connectivity check
- External API availability

### Logging
- Structured JSON logging
- Request/response logging
- Error tracking
- Audit logging for sensitive operations

### Metrics
- Request latency
- Error rates
- Payment success rates
- Booking conversion rates
- External API response times

### Alerting
- Application errors
- Payment failures
- API downtime
- High latency
- Rate limit violations

## Disaster Recovery

### Backup Strategy
- Daily MongoDB backups
- Transaction log backups
- Configuration backups
- Encrypted backup storage

### Recovery Procedures
- Database restoration
- Application rollback
- Configuration restoration
- Incident response plan

## Performance Optimization

### Database Optimization
- Proper indexing on frequently queried fields
- MongoDB aggregation pipelines
- Connection pooling
- Query optimization

### API Optimization
- Async handlers for I/O operations
- Response compression
- Pagination for list endpoints
- Efficient serialization with Pydantic

### Caching
- Redis for frequent queries
- In-memory caching for static data
- Cache invalidation strategies

## Deployment Architecture

### Development
```
Docker Compose:
- FastAPI container
- MongoDB container
- Redis container
```

### Production
```
Kubernetes Cluster:
- Multiple FastAPI pods (3+)
- MongoDB StatefulSet with replication
- Redis cluster
- Nginx Ingress Controller
- Let's Encrypt for SSL
- Horizontal Pod Autoscaler
```

## Future Enhancements

1. **Real-time Features**
   - WebSocket support for live updates
   - Real-time seat availability
   - Live booking notifications

2. **Advanced Features**
   - Machine learning for price predictions
   - Recommendation engine
   - Fraud detection
   - Dynamic pricing

3. **Mobile Apps**
   - Native iOS app
   - Native Android app
   - Push notifications

4. **Analytics**
   - Advanced reporting dashboard
   - Business intelligence integration
   - Customer behavior analytics

5. **Integrations**
   - More transport providers
   - Hotel bookings
   - Car rentals
   - Travel insurance

## API Design Principles

1. **RESTful**: Standard HTTP methods and status codes
2. **Versioned**: `/api/v1` for version management
3. **Consistent**: Uniform response formats
4. **Documented**: OpenAPI/Swagger documentation
5. **Secure**: Authentication and authorization on all endpoints
6. **Paginated**: Large result sets use pagination
7. **Validated**: Pydantic for request/response validation

## Error Handling

### Error Response Format
```json
{
  "detail": "Human-readable error message",
  "type": "error_type",
  "field": "field_name"  // for validation errors
}
```

### HTTP Status Codes
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 429: Too Many Requests
- 500: Internal Server Error

## Conclusion

The Ovu Transport Aggregator is built with scalability, security, and reliability in mind. The modular architecture allows for easy maintenance and extension, while the use of modern technologies ensures high performance and developer productivity.
