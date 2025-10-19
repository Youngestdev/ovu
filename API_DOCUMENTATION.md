# API Documentation

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication

All authenticated endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <your_access_token>
```

Partner API endpoints require an API key:
```
X-API-Key: <your_api_key>
```

## Endpoints

### Authentication

#### Register User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+2348012345678"
}
```

Response (201):
```json
{
  "id": "64a1b2c3d4e5f6g7h8i9j0k1",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "customer",
  "is_active": true,
  "is_verified": false
}
```

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

Response (200):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Get Current User
```http
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

Response (200):
```json
{
  "id": "64a1b2c3d4e5f6g7h8i9j0k1",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "customer",
  "is_active": true,
  "is_verified": false
}
```

### Bookings

#### Search Transport
```http
POST /api/v1/bookings/search
Content-Type: application/json

{
  "origin": "Lagos",
  "destination": "Abuja",
  "departure_date": "2024-12-25T08:00:00",
  "passengers": 2,
  "transport_types": ["flight", "bus", "train"]
}
```

Response (200):
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
    "duration_minutes": 90,
    "provider_reference": "TRV-FL-001",
    "flight_number": "AA101",
    "airline": "Air Peace"
  },
  {
    "transport_type": "bus",
    "provider": "travu",
    "origin": "Lagos",
    "destination": "Abuja",
    "departure_date": "2024-12-25T08:00:00",
    "price": 15000.0,
    "currency": "NGN",
    "available_seats": 30,
    "duration_minutes": 720,
    "provider_reference": "TRV-BUS-001",
    "bus_type": "Luxury",
    "bus_company": "GUO Transport"
  }
]
```

#### Create Booking
```http
POST /api/v1/bookings
Authorization: Bearer <access_token>
Content-Type: application/json

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
      "gender": "male",
      "id_type": "passport",
      "id_number": "A12345678"
    }
  ]
}
```

Response (201):
```json
{
  "id": "64a1b2c3d4e5f6g7h8i9j0k1",
  "booking_reference": "BKG-20241225120000-ABC123",
  "user_id": "64a1b2c3d4e5f6g7h8i9j0k1",
  "transport_type": "flight",
  "status": "pending",
  "origin": "Lagos",
  "destination": "Abuja",
  "departure_date": "2024-12-25T08:00:00",
  "total_passengers": 1,
  "total_price": 47000.0,
  "currency": "NGN",
  "created_at": "2024-12-20T12:00:00"
}
```

#### Get User Bookings
```http
GET /api/v1/bookings?skip=0&limit=10
Authorization: Bearer <access_token>
```

Response (200):
```json
[
  {
    "id": "64a1b2c3d4e5f6g7h8i9j0k1",
    "booking_reference": "BKG-20241225120000-ABC123",
    "user_id": "64a1b2c3d4e5f6g7h8i9j0k1",
    "transport_type": "flight",
    "status": "paid",
    "origin": "Lagos",
    "destination": "Abuja",
    "departure_date": "2024-12-25T08:00:00",
    "total_passengers": 1,
    "total_price": 47000.0,
    "currency": "NGN",
    "created_at": "2024-12-20T12:00:00"
  }
]
```

#### Get Specific Booking
```http
GET /api/v1/bookings/{booking_id}
Authorization: Bearer <access_token>
```

#### Cancel Booking
```http
POST /api/v1/bookings/{booking_id}/cancel
Authorization: Bearer <access_token>
```

Response (200):
```json
{
  "message": "Booking cancelled successfully"
}
```

### Payments

#### Initialize Payment
```http
POST /api/v1/payments/initialize
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "booking_id": "64a1b2c3d4e5f6g7h8i9j0k1",
  "payment_method": "card",
  "callback_url": "https://yourapp.com/payment/callback"
}
```

Response (201):
```json
{
  "payment_reference": "PAY-20241220120000-XYZ789",
  "booking_id": "64a1b2c3d4e5f6g7h8i9j0k1",
  "amount": 47000.0,
  "currency": "NGN",
  "status": "pending",
  "authorization_url": "https://checkout.paystack.com/abc123"
}
```

#### Get Payment Details
```http
GET /api/v1/payments/{payment_id}
Authorization: Bearer <access_token>
```

#### Request Refund
```http
POST /api/v1/payments/refund
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "booking_id": "64a1b2c3d4e5f6g7h8i9j0k1",
  "reason": "Changed travel plans",
  "amount": null
}
```

Response (202):
```json
{
  "message": "Refund initiated successfully"
}
```

### Operator Dashboard

#### Get Dashboard
```http
GET /api/v1/operators/dashboard
Authorization: Bearer <operator_token>
```

Response (200):
```json
{
  "operator": {
    "name": "Air Peace",
    "operator_code": "AIRP001",
    "type": "airline",
    "status": "active"
  },
  "stats": {
    "total_bookings": 1250,
    "today_bookings": 45,
    "total_revenue": 58750000.0,
    "today_revenue": 2115000.0
  }
}
```

#### Get Operator Bookings
```http
GET /api/v1/operators/bookings?skip=0&limit=20
Authorization: Bearer <operator_token>
```

#### Get Sales Analytics
```http
GET /api/v1/operators/sales?days=30
Authorization: Bearer <operator_token>
```

Response (200):
```json
{
  "period_days": 30,
  "daily_sales": [
    {
      "date": "2024-12-01",
      "bookings": 42,
      "revenue": 1974000.0
    }
  ],
  "total_bookings": 1250,
  "total_revenue": 58750000.0
}
```

#### Get Payouts
```http
GET /api/v1/operators/payouts
Authorization: Bearer <operator_token>
```

### Partner API

#### Search Transport (Partner)
```http
POST /api/v1/search
X-API-Key: <partner_api_key>
Content-Type: application/json

{
  "origin": "Lagos",
  "destination": "Abuja",
  "departure_date": "2024-12-25T08:00:00",
  "passengers": 2,
  "transport_types": ["flight", "bus"]
}
```

#### Get Booking (Partner)
```http
GET /api/v1/bookings/{booking_reference}
X-API-Key: <partner_api_key>
```

## Webhooks

### Payment Webhook
Paystack will send POST requests to your configured webhook URL:

```http
POST /api/v1/payments/webhook
X-Paystack-Signature: <signature>
Content-Type: application/json

{
  "event": "charge.success",
  "data": {
    "reference": "PAY-20241220120000-XYZ789",
    "amount": 4700000,
    "status": "success"
  }
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid input data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Not authorized to access this resource"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error",
  "type": "server_error"
}
```

## Rate Limits

- Default: 60 requests per minute per IP
- Partners: Configurable per partner (default 60/min, 10,000/day)

## Pagination

List endpoints support pagination:
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records to return (default: 10, max: 100)

Example:
```
GET /api/v1/bookings?skip=20&limit=10
```
