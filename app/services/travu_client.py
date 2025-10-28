"""
Travu API client for flights and buses
"""
import httpx
from typing import List, Optional
from datetime import datetime
from app.core.config import settings
from app.schemas.booking import SearchRequest, SearchResult
from app.models.booking import TransportType


class TravuAPIClient:
    """Client for Travu API integration"""
    
    def __init__(self):
        self.base_url = settings.TRAVU_API_URL
        self.api_key = settings.TRAVU_API_KEY
        self.api_secret = settings.TRAVU_API_SECRET
        
    async def search_flights(self, search_req: SearchRequest) -> List[SearchResult]:
        """Search for flights"""
        results = []
        
        # Mock implementation - replace with actual Travu API calls
        if not self.api_key:
            # Return mock data for demonstration
            results.append(SearchResult(
                transport_type=TransportType.FLIGHT,
                provider="travu",
                origin=search_req.origin,
                destination=search_req.destination,
                departure_date=search_req.departure_date,
                arrival_date=search_req.departure_date,
                price=45000.0,
                currency="NGN",
                available_seats=50,
                duration_minutes=90,
                provider_reference="TRV-FL-001",
                flight_number="AA101",
                airline="Air Peace"
            ))
            return results
        
        # Actual API call
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/flights/search",
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
                    for item in data.get("flights", []):
                        results.append(SearchResult(
                            transport_type=TransportType.FLIGHT,
                            provider="travu",
                            origin=item["origin"],
                            destination=item["destination"],
                            departure_date=datetime.fromisoformat(item["departure_time"]),
                            arrival_date=datetime.fromisoformat(item["arrival_time"]),
                            price=float(item["price"]),
                            currency=item.get("currency", "NGN"),
                            available_seats=item["available_seats"],
                            duration_minutes=item.get("duration"),
                            provider_reference=item["reference"],
                            flight_number=item["flight_number"],
                            airline=item["airline"]
                        ))
            except Exception as e:
                print(f"Error searching flights from Travu: {e}")
        
        return results
    
    async def search_buses(self, search_req: SearchRequest) -> List[SearchResult]:
        """Search for buses"""
        results = []
        
        # Mock implementation
        if not self.api_key:
            results.append(SearchResult(
                transport_type=TransportType.BUS,
                provider="travu",
                origin=search_req.origin,
                destination=search_req.destination,
                departure_date=search_req.departure_date,
                arrival_date=search_req.departure_date,
                price=8000.0,
                currency="NGN",
                available_seats=30,
                duration_minutes=420,
                provider_reference="TRV-BUS-001",
                bus_type="Luxury",
                bus_company="GUO Transport"
            ))
            return results
        
        # Actual API call
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/buses/search",
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
                    for item in data.get("buses", []):
                        results.append(SearchResult(
                            transport_type=TransportType.BUS,
                            provider="travu",
                            origin=item["origin"],
                            destination=item["destination"],
                            departure_date=datetime.fromisoformat(item["departure_time"]),
                            arrival_date=datetime.fromisoformat(item.get("arrival_time", item["departure_time"])),
                            price=float(item["price"]),
                            currency=item.get("currency", "NGN"),
                            available_seats=item["available_seats"],
                            duration_minutes=item.get("duration"),
                            provider_reference=item["reference"],
                            bus_type=item["bus_type"],
                            bus_company=item["company"]
                        ))
            except Exception as e:
                print(f"Error searching buses from Travu: {e}")
        
        return results
    
    async def book_flight(self, booking_data: dict) -> dict:
        """Book a flight"""
        # Mock implementation
        if not self.api_key:
            return {
                "booking_id": "TRV-FL-BOOK-001",
                "status": "confirmed",
                "pnr": "ABC123"
            }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/flights/book",
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
                print(f"Error booking flight: {e}")
                raise
        
        return {}
    
    async def book_bus(self, booking_data: dict) -> dict:
        """Book a bus"""
        # Mock implementation
        if not self.api_key:
            return {
                "booking_id": "TRV-BUS-BOOK-001",
                "status": "confirmed"
            }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/buses/book",
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
                print(f"Error booking bus: {e}")
                raise
        
        return {}
