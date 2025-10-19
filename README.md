# Ovu Transport Aggregator

A comprehensive FastAPI-based transport aggregator for Nigeria, integrating flights, buses, and trains.

## Features

- **Unified Search**: Search across multiple transport types (flights, buses, trains)
- **Booking Management**: Complete booking system with passenger and seat management
- **Payment Integration**: Paystack integration with split settlements for operators
- **E-Tickets**: Generate e-tickets with QR codes
- **Notifications**: Email, SMS, and WhatsApp notifications
- **Operator Dashboards**: Sales analytics and payout management for operators
- **Partner API**: RESTful API with JWT authentication for partners
- **Webhooks**: Event-based notifications for partners
- **Security**: PCI-DSS and NDPA compliance measures

## Technology Stack

- **Framework**: FastAPI
- **Database**: MongoDB (with Beanie ODM)
- **Payment**: Paystack
- **Notifications**: Twilio (SMS/WhatsApp), SMTP (Email)
- **Authentication**: JWT
- **Task Queue**: Celery + Redis
- **Containerization**: Docker

## Prerequisites

- Python 3.11+
- MongoDB 7.0+
- Redis 7+
- Docker (optional)

## Installation

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/Youngestdev/ovu.git
cd ovu
```

2. Create `.env` file from example:
```bash
cp .env.example .env
```

3. Update the `.env` file with your credentials

4. Start services:
```bash
docker-compose up -d
```

The API will be available at `http://localhost:8000`

### Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/Youngestdev/ovu.git
cd ovu
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
cp .env.example .env
```

5. Update the `.env` file with your credentials

6. Run MongoDB and Redis locally

7. Start the application:
```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --reload
```

## API Documentation

Once the application is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user info

### Bookings
- `POST /api/v1/bookings/search` - Search transport options
- `POST /api/v1/bookings` - Create booking
- `GET /api/v1/bookings` - Get user bookings
- `GET /api/v1/bookings/{id}` - Get specific booking
- `POST /api/v1/bookings/{id}/cancel` - Cancel booking

### Payments
- `POST /api/v1/payments/initialize` - Initialize payment
- `POST /api/v1/payments/webhook` - Payment webhook
- `GET /api/v1/payments/{id}` - Get payment details
- `POST /api/v1/payments/refund` - Request refund

### Operators
- `GET /api/v1/operators/dashboard` - Operator dashboard
- `GET /api/v1/operators/bookings` - Get operator bookings
- `GET /api/v1/operators/sales` - Sales analytics
- `GET /api/v1/operators/payouts` - Payout information

### Partner API
- `POST /api/v1/search` - Search transport (with API key)
- `POST /api/v1/bookings` - Create booking (with API key)
- `GET /api/v1/bookings/{ref}` - Get booking (with API key)

## Configuration

All configuration is done through environment variables. See `.env.example` for all available options.

### Key Configuration

- **MongoDB**: `MONGODB_URL`
- **Travu API**: `TRAVU_API_KEY`, `TRAVU_API_SECRET`
- **NRC API**: `NRC_API_KEY`, `NRC_API_SECRET`
- **Paystack**: `PAYSTACK_SECRET_KEY`, `PAYSTACK_PUBLIC_KEY`
- **Twilio**: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`
- **Email**: `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD`

## Security & Compliance

### PCI-DSS Compliance
- Payment data is handled through Paystack (PCI-DSS Level 1 certified)
- No credit card data is stored in the application
- All payment communications use HTTPS

### NDPA Compliance
- User data encryption at rest and in transit
- Access controls and authentication
- Audit logging for data access
- Data retention policies

### Security Features
- JWT-based authentication
- Rate limiting
- Input validation with Pydantic
- CORS configuration
- API key authentication for partners

## Architecture

```
app/
├── core/           # Core configurations
├── models/         # MongoDB models
├── schemas/        # Pydantic schemas
├── routes/         # API endpoints
├── services/       # Business logic & integrations
├── middleware/     # Custom middleware
└── utils/          # Utility functions
```

## Testing

```bash
pytest
```

With coverage:
```bash
pytest --cov=app --cov-report=html
```

## Monitoring

Health check endpoint: `GET /health`

Response:
```json
{
  "status": "healthy",
  "app": "Ovu Transport Aggregator",
  "version": "v1",
  "environment": "production"
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License

## Support

For support, email support@ovutransport.com or open an issue on GitHub.

## Roadmap

- [ ] Mobile app integration
- [ ] Real-time tracking
- [ ] Loyalty rewards system
- [ ] Multi-currency support
- [ ] Advanced analytics dashboard
- [ ] Machine learning for price predictions
- [ ] Integration with more transport providers

## Target Performance

- **Uptime**: 99.9% availability
- **Response Time**: < 200ms for search queries
- **Scalability**: Handle 10,000+ concurrent users
- **Security**: PCI-DSS and NDPA compliant