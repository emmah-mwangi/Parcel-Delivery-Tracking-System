"""Parcel Live Tracking Module - Search and track parcels"""
from typing import List, Tuple

class ParcelLiveTracking:
    """Manages parcel tracking using Linear and Binary Search
    
    Time Complexity:
    - linear_search_by_tracking: O(n)
    - linear_search_by_sender: O(n)
    - linear_search_by_receiver: O(n)
    - binary_search: O(log n) - requires sorted data
    
    Space Complexity: O(1) - no extra space
    """
    
    def __init__(self, registration_module):
        """Initialize with reference to registration module"""
        self.registration = registration_module
    
    def linear_search_by_tracking(self, tracking_id: str):
        """Linear search by tracking ID - O(n)"""
        parcels = self.registration.get_all_parcels()
        for parcel in parcels:
            if parcel.tracking_id == tracking_id:
                return parcel
        return None
    
    def linear_search_by_sender(self, sender_name: str) -> List:
        """Linear search by sender name - O(n)"""
        parcels = self.registration.get_all_parcels()
        results = []
        for parcel in parcels:
            if sender_name.lower() in parcel.sender.lower():
                results.append(parcel)
        return results
    
    def linear_search_by_receiver(self, receiver_name: str) -> List:
        """Linear search by receiver name - O(n)"""
        parcels = self.registration.get_all_parcels()
        results = []
        for parcel in parcels:
            if receiver_name.lower() in parcel.receiver.lower():
                results.append(parcel)
        return results
    
    def binary_search_by_tracking(self, tracking_id: str) -> Tuple[bool, int]:
        """Binary search on sorted tracking IDs - O(log n)"""
        parcels = self.registration.get_all_parcels()
        sorted_parcels = sorted(parcels, key=lambda p: p.tracking_id)
        
        left, right = 0, len(sorted_parcels) - 1
        
        while left <= right:
            mid = (left + right) // 2
            mid_tracking = sorted_parcels[mid].tracking_id
            
            if mid_tracking == tracking_id:
                return True, mid
            elif mid_tracking < tracking_id:
                left = mid + 1
            else:
                right = mid - 1
        
        return False, -1
    
    def get_parcel_tracking_info(self, tracking_id: str) -> dict or None:
        """Get parcel tracking information - O(n)"""
        parcel = self.linear_search_by_tracking(tracking_id)
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
    
    def search_all_parcels(self, search_term: str) -> List:
        """Search across all fields - O(n)"""
        parcels = self.registration.get_all_parcels()
        results = []
        search_lower = search_term.lower()
        
        for parcel in parcels:
            if (search_lower in parcel.tracking_id.lower() or
                search_lower in parcel.sender.lower() or
                search_lower in parcel.receiver.lower() or
                search_lower in parcel.origin.lower() or
                search_lower in parcel.destination.lower()):
                results.append(parcel)
        
        return results
    
    def get_total_parcels(self) -> int:
        """Get total parcels in system - O(1)"""
        return self.registration.get_parcel_count()
