"""
Test configuration and fixtures
"""
import pytest
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.user import User
from app.models.booking import Booking, FlightBooking, BusBooking, TrainBooking
from app.models.payment import Payment, Transaction
from app.models.ticket import Ticket
from app.models.operator import Operator
from app.models.partner import Partner


@pytest.fixture
async def test_db():
    """Test database fixture"""
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    
    await init_beanie(
        database=client["ovu_transport_test"],
        document_models=[
            User,
            Booking,
            FlightBooking,
            BusBooking,
            TrainBooking,
            Payment,
            Transaction,
            Ticket,
            Operator,
            Partner,
        ]
    )
    
    yield client
    
    # Cleanup
    await client.drop_database("ovu_transport_test")
    client.close()


@pytest.fixture
def client():
    """Test client fixture"""
    from main import app
    return TestClient(app)
