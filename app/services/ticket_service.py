"""
Ticket generation service with QR codes
"""
import qrcode
import io
import base64
from datetime import datetime
from typing import Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from app.models.ticket import Ticket
from app.models.booking import Booking


class TicketService:
    """E-ticket generation with QR codes"""
    
    def generate_qr_code(self, data: str) -> str:
        """Generate QR code and return as base64 string"""
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        
        img_base64 = base64.b64encode(buffer.read()).decode()
        
        return img_base64
    
    def generate_ticket_pdf(
        self,
        ticket: Ticket,
        booking: Booking,
        qr_code_base64: str,
    ) -> bytes:
        """Generate PDF ticket"""
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a73e8'),
            spaceAfter=30,
            alignment=1,  # Center
        )
        
        # Title
        title = Paragraph("OVU TRANSPORT E-TICKET", title_style)
        story.append(title)
        story.append(Spacer(1, 0.3 * inch))
        
        # Ticket details
        ticket_data = [
            ['Ticket Number:', ticket.ticket_number],
            ['Passenger Name:', ticket.passenger_name],
            ['Transport Type:', ticket.transport_type.upper()],
            ['Route:', f"{ticket.origin} → {ticket.destination}"],
            ['Departure Date:', ticket.departure_date.strftime('%Y-%m-%d %H:%M')],
            ['Seat Number:', ticket.seat_number or 'N/A'],
            ['Status:', ticket.status.upper()],
        ]
        
        table = Table(ticket_data, colWidths=[2.5 * inch, 4 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.5 * inch))
        
        # QR Code
        qr_image_data = base64.b64decode(qr_code_base64)
        qr_buffer = io.BytesIO(qr_image_data)
        qr_img = Image(qr_buffer, width=2 * inch, height=2 * inch)
        
        story.append(Paragraph("Scan QR Code at Terminal", styles['Heading3']))
        story.append(Spacer(1, 0.2 * inch))
        story.append(qr_img)
        story.append(Spacer(1, 0.3 * inch))
        
        # Footer
        footer_text = """
        <para align=center>
        <b>Important Instructions:</b><br/>
        Please arrive at the terminal 30 minutes before departure.<br/>
        Present this ticket and a valid ID at the check-in counter.<br/>
        For assistance, contact support@ovutransport.com
        </para>
        """
        footer = Paragraph(footer_text, styles['Normal'])
        story.append(footer)
        
        # Build PDF
        doc.build(story)
        
        buffer.seek(0)
        return buffer.read()
    
    async def create_ticket(
        self,
        booking: Booking,
        passenger_name: str,
        seat_number: Optional[str] = None,
    ) -> Ticket:
        """Create an e-ticket for a booking"""
        
        # Generate ticket number
        ticket_number = f"TKT-{booking.transport_type[:3].upper()}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        # Generate QR code data
        qr_data = f"{ticket_number}|{booking.booking_reference}|{passenger_name}"
        qr_code_base64 = self.generate_qr_code(qr_data)
        
        # Create ticket
        ticket = Ticket(
            ticket_number=ticket_number,
            booking_id=str(booking.id),
            user_id=booking.user_id,
            passenger_name=passenger_name,
            qr_code_data=qr_data,
            transport_type=booking.transport_type,
            origin=booking.origin,
            destination=booking.destination,
            departure_date=booking.departure_date,
            seat_number=seat_number,
        )
        
        await ticket.save()
        
        # Generate PDF
        pdf_bytes = self.generate_ticket_pdf(ticket, booking, qr_code_base64)
        
        # In production, upload to cloud storage and set ticket.pdf_url
        # For now, we'll store it locally
        pdf_filename = f"/tmp/{ticket_number}.pdf"
        with open(pdf_filename, "wb") as f:
            f.write(pdf_bytes)
        
        ticket.pdf_url = f"file://{pdf_filename}"
        await ticket.save()
        
        return ticket
