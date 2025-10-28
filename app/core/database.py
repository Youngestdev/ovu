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


class Database:
    client: AsyncIOMotorClient = None
    
    
db = Database()


async def connect_to_mongo():
    """Connect to MongoDB"""
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)
    
    await init_beanie(
        database=db.client[settings.MONGODB_DB_NAME],
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


async def close_mongo_connection():
    """Close MongoDB connection"""
    if db.client:
        db.client.close()
