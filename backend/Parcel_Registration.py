"""Parcel Registration Module - Handles parcel creation and validation"""
import uuid
from datetime import datetime
from typing import List, Tuple

class Parcel:
    """Represents a single parcel"""
    def __init__(self, tracking_id: str, sender: str, receiver: str, 
                 origin: str, destination: str, weight: float):
        self.tracking_id = tracking_id
        self.sender = sender
        self.receiver = receiver
        self.origin = origin
        self.destination = destination
        self.weight = weight
        self.status = "Registered"
        self.created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cost = 0.0

class ParcelRegistration:
    """Manages parcel registration using Array/List
    
    Time Complexity:
    - add_parcel: O(1) append
    - validate_input: O(1)
    - search_by_tracking: O(n)
    - get_all_parcels: O(n)
    
    Space Complexity: O(n)
    """
    
    def __init__(self):
        self.parcels: List[Parcel] = []  # Array/List DSA
        self.tracking_ids_set = set()  # For O(1) duplicate checking
    
    def generate_tracking_id(self) -> str:
        """Generate unique tracking ID - O(1)"""
        tracking_id = f"PKL{str(uuid.uuid4().hex[:8]).upper()}"
        while tracking_id in self.tracking_ids_set:
            tracking_id = f"PKL{str(uuid.uuid4().hex[:8]).upper()}"
        self.tracking_ids_set.add(tracking_id)
        return tracking_id
    
    def validate_input(self, sender: str, receiver: str, origin: str, 
                      destination: str, weight: float) -> Tuple[bool, str]:
        """Validate parcel input - O(1)"""
        if not sender or not sender.strip():
            return False, "Sender name required"
        if not receiver or not receiver.strip():
            return False, "Receiver name required"
        if not origin or not origin.strip():
            return False, "Origin location required"
        if not destination or not destination.strip():
            return False, "Destination location required"
        if weight <= 0:
            return False, "Weight must be > 0"
        if weight > 500:
            return False, "Weight exceeds 500kg limit"
        return True, "Valid input"
    
    def add_parcel(self, sender: str, receiver: str, origin: str, 
                   destination: str, weight: float) -> Tuple[bool, str, str]:
        """Register new parcel - O(1) append"""
        is_valid, message = self.validate_input(sender, receiver, origin, destination, weight)
        if not is_valid:
            return False, message, ""
        
        tracking_id = self.generate_tracking_id()
        parcel = Parcel(tracking_id, sender, receiver, origin, destination, weight)
        self.parcels.append(parcel)
        
        return True, "Registered successfully", tracking_id
    
    def search_by_tracking_id(self, tracking_id: str):
        """Search parcel - O(n) linear search"""
        for parcel in self.parcels:
            if parcel.tracking_id == tracking_id:
                return parcel
        return None
    
    def get_all_parcels(self) -> List[Parcel]:
        """Get all parcels - O(n)"""
        return self.parcels
    
    def get_parcel_count(self) -> int:
        """Get total count - O(1)"""
        return len(self.parcels)
    
    def get_parcel_details(self, tracking_id: str):
        """Get parcel details - O(n)"""
        parcel = self.search_by_tracking_id(tracking_id)
        if not parcel:
            return None
        return {
            'tracking_id': parcel.tracking_id,
            'sender': parcel.sender,
            'receiver': parcel.receiver,
            'origin': parcel.origin,
            'destination': parcel.destination,
            'weight': parcel.weight,
            'status': parcel.status,
            'created_date': parcel.created_date,
            'cost': parcel.cost
        }
