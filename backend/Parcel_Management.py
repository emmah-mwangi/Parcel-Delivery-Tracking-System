"""Parcel Management Module - Queue-based delivery processing"""
from typing import List

class DeliveryQueue:
    """Queue data structure for FIFO delivery processing
    
    Time Complexity:
    - enqueue: O(1)
    - dequeue: O(1)
    - peek: O(1)
    - is_empty: O(1)
    
    Space Complexity: O(n)
    """
    
    def __init__(self):
        self.queue = []  # Queue (FIFO)
    
    def enqueue(self, parcel) -> None:
        """Add parcel to queue - O(1)"""
        self.queue.append(parcel)
    
    def dequeue(self):
        """Remove and return first parcel - O(1) with list"""
        if not self.is_empty():
            return self.queue.pop(0)
        return None
    
    def peek(self):
        """View first parcel - O(1)"""
        if not self.is_empty():
            return self.queue[0]
        return None
    
    def is_empty(self) -> bool:
        """Check if queue is empty - O(1)"""
        return len(self.queue) == 0
    
    def size(self) -> int:
        """Get queue size - O(1)"""
        return len(self.queue)

class ParcelManagement:
    """Manages parcel delivery using Queue
    
    Time Complexity:
    - add_to_queue: O(1)
    - process_delivery: O(1)
    - update_status: O(n)
    - get_queue_info: O(n)
    
    Space Complexity: O(n)
    """
    
    def __init__(self, registration_module):
        """Initialize management with registration module"""
        self.registration = registration_module
        self.delivery_queue = DeliveryQueue()
        self.delivered_parcels = []  # Array/List for completed deliveries
    
    def add_to_queue(self, tracking_id: str) -> Tuple[bool, str]:
        """Add parcel to delivery queue - O(n)"""
        parcel = self.registration.search_by_tracking_id(tracking_id)
        if not parcel:
            return False, "Parcel not found"
        
        if parcel.status != "Registered":
            return False, f"Parcel status is {parcel.status}"
        
        self.delivery_queue.enqueue(parcel)
        parcel.status = "Dispatched"
        
        return True, "Parcel added to delivery queue"
    
    def process_delivery(self) -> Tuple[bool, str, dict]:
        """Process next parcel in queue - O(1)"""
        parcel = self.delivery_queue.dequeue()
        if not parcel:
            return False, "No parcels in queue", {}
        
        parcel.status = "Delivered"
        self.delivered_parcels.append(parcel)
        
        delivery_info = {
            'tracking_id': parcel.tracking_id,
            'receiver': parcel.receiver,
            'destination': parcel.destination,
            'status': 'Delivered'
        }
        
        return True, "Delivery processed", delivery_info
    
    def update_parcel_status(self, tracking_id: str, new_status: str) -> Tuple[bool, str]:
        """Update parcel status - O(n)"""
        parcel = self.registration.search_by_tracking_id(tracking_id)
        if not parcel:
            return False, "Parcel not found"
        
        valid_statuses = ["Registered", "Dispatched", "In Transit", "Out For Delivery", "Delivered", "Cancelled"]
        if new_status not in valid_statuses:
            return False, f"Invalid status. Must be one of: {valid_statuses}"
        
        parcel.status = new_status
        return True, f"Status updated to {new_status}"
    
    def get_queue_info(self) -> dict:
        """Get delivery queue information - O(n)"""
        next_parcel = self.delivery_queue.peek()
        next_info = None
        
        if next_parcel:
            next_info = {
                'tracking_id': next_parcel.tracking_id,
                'receiver': next_parcel.receiver,
                'destination': next_parcel.destination
            }
        
        return {
            'queue_size': self.delivery_queue.size(),
            'next_parcel': next_info,
            'delivered_count': len(self.delivered_parcels)
        }
    
    def get_queue_list(self) -> List:
        """Get list of parcels in queue - O(n)"""
        return [{
            'tracking_id': p.tracking_id,
            'receiver': p.receiver,
            'destination': p.destination,
            'weight': p.weight
        } for p in self.delivery_queue.queue]
    
    def get_delivered_parcels(self) -> List:
        """Get all delivered parcels - O(n)"""
        return [{
            'tracking_id': p.tracking_id,
            'receiver': p.receiver,
            'destination': p.destination,
            'status': p.status
        } for p in self.delivered_parcels]
    
    def get_delivered_count(self) -> int:
        """Get count of delivered parcels - O(1)"""
        return len(self.delivered_parcels)

from typing import Tuple
