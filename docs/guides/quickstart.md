# Quick Start Guide

Get started with Ovu Transport Aggregator in 5 minutes!

## Prerequisites

- Python 3.11 or higher
- MongoDB (or MongoDB Atlas account)
- Redis (optional, for Celery tasks)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/Youngestdev/ovu.git
cd ovu
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and set minimum required variables:

```bash
# Minimum required for local development
SECRET_KEY=your-secret-key-change-this
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=ovu_transport
PAYSTACK_SECRET_KEY=sk_test_your_key
PAYSTACK_PUBLIC_KEY=pk_test_your_key
PAYSTACK_WEBHOOK_SECRET=your_webhook_secret
SMTP_FROM_EMAIL=noreply@example.com
DATA_ENCRYPTION_KEY=your-encryption-key
```

### 5. Start MongoDB (if running locally)

```bash
# Using Docker
docker run -d -p 27017:27017 --name mongodb mongo:7.0

# Or install MongoDB locally
# See: https://www.mongodb.com/docs/manual/installation/
```

### 6. Run the Application

```bash
python main.py
```

Or with uvicorn:

```bash
uvicorn main:app --reload
```

The API will be available at: `http://localhost:8000`

### 7. Access API Documentation

Open your browser and navigate to:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Using Docker (Easier!)

### 1. Clone the Repository

```bash
git clone https://github.com/Youngestdev/ovu.git
cd ovu
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

### 3. Start Services

```bash
docker-compose up -d
```

That's it! The application will be available at `http://localhost:8000`

To view logs:
```bash
docker-compose logs -f app
```

To stop services:
```bash
docker-compose down
```

## First API Calls

### 1. Register a User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+2348012345678"
  }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

Save the `access_token` from the response.

### 3. Search Transport

```bash
curl -X POST "http://localhost:8000/api/v1/bookings/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "origin": "Lagos",
    "destination": "Abuja",
    "departure_date": "2024-12-25T08:00:00",
    "passengers": 1,
    "transport_types": ["flight", "bus", "train"]
  }'
```

### 4. Check Health

```bash
curl http://localhost:8000/health
```

## Testing

Run tests:

```bash
pytest
```

With coverage:

```bash
pytest --cov=app --cov-report=html
```

## Common Issues

### Issue: MongoDB Connection Error

**Solution**: Make sure MongoDB is running and the connection string in `.env` is correct.

```bash
# Check if MongoDB is running
docker ps  # If using Docker

# Or check local MongoDB
mongosh
```

### Issue: Module Import Errors

**Solution**: Make sure you're in the virtual environment and all dependencies are installed.

```bash
# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Port Already in Use

**Solution**: Change the port in `.env` or stop the process using port 8000.

```bash
# Find process using port 8000
lsof -i :8000  # On Mac/Linux
netstat -ano | findstr :8000  # On Windows

# Change port in .env
PORT=8001
```

## Next Steps

1. **Read the API Documentation**: Check `API_DOCUMENTATION.md` for all available endpoints
2. **Configure External Services**: Set up Travu API, NRC API, Twilio, etc.
3. **Deploy to Production**: See `DEPLOYMENT.md` for deployment guides
4. **Customize**: Modify the code to fit your specific needs

## Getting Help

- **Documentation**: See `README.md` for detailed information
- **API Reference**: Check `API_DOCUMENTATION.md`
- **Deployment**: Read `DEPLOYMENT.md`
- **Issues**: Open an issue on GitHub

## Development Tips

### Hot Reload

Use `--reload` flag for automatic reloading during development:

```bash
uvicorn main:app --reload
```

### Debug Mode

Enable debug mode in `.env`:

```bash
DEBUG=True
```

### Database Inspection

Use MongoDB Compass or mongosh to inspect your database:

```bash
mongosh mongodb://localhost:27017/ovu_transport
```

### API Testing

Use tools like:
- **Postman**: Import the OpenAPI spec from `/docs`
- **HTTPie**: `http POST localhost:8000/api/v1/auth/login email=user@example.com password=pass123`
- **cURL**: See examples above

## Project Structure Overview

```
ovu/
├── app/
│   ├── core/           # Configuration, database, security
│   ├── models/         # MongoDB models
│   ├── schemas/        # Pydantic schemas
│   ├── routes/         # API endpoints
│   ├── services/       # Business logic
│   ├── middleware/     # Custom middleware
│   └── utils/          # Helper functions
├── tests/              # Test files
├── main.py            # Application entry point
├── requirements.txt   # Python dependencies
├── Dockerfile         # Docker configuration
└── docker-compose.yml # Multi-container setup
```

## Environment Variables Reference

See `.env.example` for all available configuration options.

**Critical Variables:**
- `SECRET_KEY`: Used for JWT token signing (must be strong and secret)
- `MONGODB_URL`: Database connection string
- `PAYSTACK_SECRET_KEY`: Payment processing
- `SMTP_*`: Email notifications
- `TWILIO_*`: SMS/WhatsApp notifications

## Monitoring

Check application health:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "app": "Ovu Transport Aggregator",
  "version": "v1",
  "environment": "development"
}
```

## Security Notes

⚠️ **Important Security Reminders:**

1. Never commit `.env` file to version control
2. Use strong, random values for `SECRET_KEY`
3. Keep API keys secret
4. Use HTTPS in production
5. Regularly update dependencies
6. Enable rate limiting in production
7. Monitor for suspicious activity

## License

MIT License - See LICENSE file for details

## Support

For support and questions:
- Email: support@ovutransport.com
- GitHub Issues: https://github.com/Youngestdev/ovu/issues

---

Happy coding! 🚀
