# Email Service Documentation

## Overview

The Ovu Transport application uses [Resend](https://resend.com) as the primary email service provider. This service provides professional HTML email templates for all transactional emails.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Resend API Key

Add your Resend API key to the `.env` file:

```env
RESEND_API_KEY=re_your_api_key_here
RESEND_FROM_EMAIL=Ovu Transport <noreply@ovutransport.com>
```

### 3. Verify Domain

Before sending emails, you need to verify your domain in Resend:

1. Log in to [Resend Dashboard](https://resend.com/domains)
2. Add your domain (e.g., `ovutransport.com`)
3. Add the DNS records provided by Resend to your domain
4. Wait for verification (usually takes a few minutes)

## Email Templates

The service includes the following professional HTML email templates:

### 1. Welcome Email (`welcome.html`)
Sent when a new user registers on the platform.

**Variables:**
- `first_name`: User's first name
- `dashboard_url`: Link to the user dashboard

**Usage:**
```python
from app.services.notification_service import NotificationService

notification_service = NotificationService()
await notification_service.email_service.send_welcome_email(
    to_email="user@example.com",
    first_name="John",
)
```

### 2. Booking Confirmation (`booking_confirmation.html`)
Sent when a booking is successfully created.

**Variables:**
- `customer_name`: Full name of the customer
- `booking_reference`: Unique booking reference
- `transport_type`: Type of transport (Flight, Bus, Train)
- `origin`: Departure location
- `destination`: Arrival location
- `departure_date`: Date and time of departure
- `total_passengers`: Number of passengers
- `total_price`: Total booking price
- `booking_url`: Link to view booking details

**Usage:**
```python
await notification_service.send_booking_confirmation(
    email="user@example.com",
    phone="+2348012345678",
    booking_reference="BKG123456",
    booking_details={
        "customer_name": "John Doe",
        "transport_type": "flight",
        "origin": "Lagos",
        "destination": "Abuja",
        "departure_date": "2024-01-15 10:00",
        "total_passengers": 2,
        "total_price": 50000.0,
    }
)
```

### 3. E-Ticket (`ticket.html`)
Sent when payment is confirmed and e-ticket is generated.

**Variables:**
- `customer_name`: Full name of the customer
- `ticket_number`: Unique ticket number
- `booking_reference`: Associated booking reference
- `origin`: Departure location
- `destination`: Arrival location
- `departure_date`: Date and time of departure
- `ticket_url`: Link to download the e-ticket

**Usage:**
```python
await notification_service.send_ticket(
    email="user@example.com",
    phone="+2348012345678",
    ticket_number="TKT123456",
    ticket_url="https://ovutransport.com/tickets/123",
    booking_details={
        "customer_name": "John Doe",
        "booking_reference": "BKG123456",
        "origin": "Lagos",
        "destination": "Abuja",
        "departure_date": "2024-01-15 10:00",
    }
)
```

### 4. Payment Success (`payment_success.html`)
Sent when payment is successfully processed.

**Variables:**
- `customer_name`: Full name of the customer
- `payment_reference`: Unique payment reference
- `booking_reference`: Associated booking reference
- `amount`: Payment amount
- `payment_date`: Date and time of payment
- `payment_method`: Payment method used (e.g., Card)
- `booking_url`: Link to view booking details

**Usage:**
```python
await notification_service.send_payment_notification(
    email="user@example.com",
    payment_reference="PAY123456",
    amount=50000.0,
    status="success",
    booking_reference="BKG123456",
    customer_name="John Doe",
)
```

### 5. Payment Failed (`payment_failed.html`)
Sent when payment processing fails.

**Variables:**
- `customer_name`: Full name of the customer
- `payment_reference`: Unique payment reference
- `booking_reference`: Associated booking reference
- `amount`: Payment amount
- `reason`: Reason for payment failure (optional)
- `retry_payment_url`: Link to retry payment

**Usage:**
```python
await notification_service.send_payment_notification(
    email="user@example.com",
    payment_reference="PAY123456",
    amount=50000.0,
    status="failed",
    booking_reference="BKG123456",
    customer_name="John Doe",
)
```

### 6. Booking Cancelled (`booking_cancelled.html`)
Sent when a booking is cancelled.

**Variables:**
- `customer_name`: Full name of the customer
- `booking_reference`: Cancelled booking reference
- `origin`: Departure location
- `destination`: Arrival location
- `departure_date`: Original departure date
- `cancellation_date`: Date of cancellation
- `refund_amount`: Refund amount (optional)
- `search_url`: Link to search for new journeys

**Usage:**
```python
await email_service.send_booking_cancelled(
    to_email="user@example.com",
    customer_name="John Doe",
    booking_reference="BKG123456",
    origin="Lagos",
    destination="Abuja",
    departure_date="2024-01-15 10:00",
    cancellation_date="2024-01-10 12:00",
    refund_amount=45000.0,
)
```

## Template Customization

All email templates are located in `app/templates/emails/` and use [Jinja2](https://jinja.palletsprojects.com/) templating engine.

### Template Structure

Each template follows this structure:
- **Header**: Company branding with gradient background
- **Content**: Main email content with clear formatting
- **Footer**: Copyright, company info, and unsubscribe links

### Common Variables

All templates automatically include:
- `year`: Current year
- `company_name`: "Ovu Transport"

### Styling

Templates use inline CSS for maximum email client compatibility. The color scheme uses:
- Primary gradient: `#667eea` to `#764ba2`
- Success: `#28a745`
- Error: `#dc3545`
- Warning: `#ffc107`

## Testing

### Unit Tests

Run the email service tests:

```bash
pytest tests/test_email_service.py -v
```

### Template Testing

Test that all templates load and render correctly:

```bash
python /tmp/test_templates.py
```

### Manual Testing

To test email sending in development, you can use Resend's test mode by using a test API key (starts with `re_test_`).

## Production Considerations

### 1. Rate Limits

Resend has the following rate limits:
- Free tier: 100 emails/day
- Pro tier: 50,000 emails/month
- Enterprise: Custom limits

Monitor your usage in the [Resend Dashboard](https://resend.com/overview).

### 2. Email Deliverability

To ensure high deliverability:
- Verify your domain with SPF, DKIM, and DMARC records
- Use a professional "from" email address
- Avoid spammy content and excessive links
- Monitor bounce and complaint rates

### 3. Error Handling

The email service includes error handling and logging:
- Failed sends are logged with error details
- The service returns `False` on failure
- Errors don't crash the application

### 4. Monitoring

Monitor email delivery in the Resend Dashboard:
- Delivery status
- Open rates
- Bounce rates
- Complaint rates

## Troubleshooting

### Emails Not Sending

1. **Check API Key**: Ensure `RESEND_API_KEY` is set correctly in `.env`
2. **Verify Domain**: Ensure your domain is verified in Resend
3. **Check Logs**: Review application logs for error messages
4. **Rate Limits**: Check if you've exceeded your rate limit

### Template Not Found

1. **Check Path**: Ensure templates are in `app/templates/emails/`
2. **File Name**: Template files must match exactly (e.g., `welcome.html`)
3. **Permissions**: Ensure template files have read permissions

### Template Rendering Errors

1. **Check Variables**: Ensure all required variables are passed
2. **Syntax**: Check Jinja2 syntax in templates
3. **Escaping**: Use `{{ variable }}` for auto-escaping

## Migration from SMTP

The old SMTP-based email service is still available as a fallback. To switch back:

1. Remove Resend initialization in `NotificationService`
2. Restore the old SMTP email sending logic
3. Update environment variables to use SMTP settings

## Support

For Resend-specific issues:
- [Resend Documentation](https://resend.com/docs)
- [Resend Support](https://resend.com/support)

For application-specific issues:
- Contact the development team
- Check application logs
