"""
NRC API client for train bookings
"""
import httpx
from typing import List
from datetime import datetime
from app.core.config import settings
from app.schemas.booking import SearchRequest, SearchResult
from app.models.booking import TransportType


class NRCAPIClient:
    """Client for NRC (Nigerian Railway Corporation) API integration"""
    
    def __init__(self):
        self.base_url = settings.NRC_API_URL
        self.api_key = settings.NRC_API_KEY
        self.api_secret = settings.NRC_API_SECRET
        
    async def search_trains(self, search_req: SearchRequest) -> List[SearchResult]:
        """Search for trains"""
        results = []
        
        # Mock implementation - replace with actual NRC API calls
        if not self.api_key:
            # Return mock data for demonstration
            results.append(SearchResult(
                transport_type=TransportType.TRAIN,
                provider="nrc",
                origin=search_req.origin,
                destination=search_req.destination,
                departure_date=search_req.departure_date,
                arrival_date=search_req.departure_date,
                price=3500.0,
                currency="NGN",
                available_seats=100,
                duration_minutes=180,
                provider_reference="NRC-TRN-001",
                train_number="NRC-001",
                train_service="Lagos-Ibadan Express"
            ))
            return results
        
        # Actual API call
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/trains/search",
                    json={
                        "origin": search_req.origin,
                        "destination": search_req.destination,
                        "departure_date": search_req.departure_date.isoformat(),
                        "passengers": search_req.passengers,
                    },
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "X-API-Secret": self.api_secret,
                    },
                    timeout=30.0,
                )
                
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get("trains", []):
                        results.append(SearchResult(
                            transport_type=TransportType.TRAIN,
                            provider="nrc",
                            origin=item["origin"],
                            destination=item["destination"],
                            departure_date=datetime.fromisoformat(item["departure_time"]),
                            arrival_date=datetime.fromisoformat(item.get("arrival_time", item["departure_time"])),
                            price=float(item["price"]),
                            currency=item.get("currency", "NGN"),
                            available_seats=item["available_seats"],
                            duration_minutes=item.get("duration"),
                            provider_reference=item["reference"],
                            train_number=item["train_number"],
                            train_service=item["service_name"]
                        ))
            except Exception as e:
                print(f"Error searching trains from NRC: {e}")
        
        return results
    
    async def book_train(self, booking_data: dict) -> dict:
        """Book a train"""
        # Mock implementation
        if not self.api_key:
            return {
                "booking_id": "NRC-TRN-BOOK-001",
                "status": "confirmed",
                "ticket_number": "NRC-TKT-001"
            }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/trains/book",
                    json=booking_data,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "X-API-Secret": self.api_secret,
                    },
                    timeout=30.0,
                )
                
                if response.status_code == 200:
                    return response.json()
            except Exception as e:
                print(f"Error booking train: {e}")
                raise
        
        return {}
