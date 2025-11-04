"""
Database connection and initialization
"""
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings
from app.models.user import User
from app.models.booking import Booking, FlightBooking, BusBooking, TrainBooking
from app.models.payment import Payment, Transaction
from app.models.ticket import Ticket
from app.models.operator import Operator
from app.models.partner import Partner
from app.models.waitlist import WaitlistSubscription


class Database:
    client: AsyncIOMotorClient = None  # type: ignore
    
    
db = Database()


async def connect_to_mongo():
    """Connect to MongoDB"""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db.client = client  # type: ignore

    await init_beanie(
        database=client[settings.MONGODB_DB_NAME],
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
            WaitlistSubscription,
        ]
    )


async def close_mongo_connection():
    """Close MongoDB connection"""
    if db.client:
        db.client.close()
