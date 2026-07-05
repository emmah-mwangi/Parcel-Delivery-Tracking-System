"""
Parcel Live Tracking System
DSA: BST (O(log n)), Doubly Linked List (O(1) insert), Hash Map (O(1) lookup)
"""

import json
import os
from datetime import datetime
from typing import Optional


# BST Node
class LocationNode:
    def __init__(self, location):
        self.location = location.lower()
        self.parcels = []
        self.left: Optional['LocationNode'] = None
        self.right: Optional['LocationNode'] = None


# Linked List Node
class HistoryNode:
    def __init__(self, data):
        self.data = data
        self.prev: Optional['HistoryNode'] = None
        self.next: Optional['HistoryNode'] = None


class ParcelLiveTracking:
    """Live tracking with BST and Linked List."""
    
    # Valid status transitions (Algorithm 2)
    VALID_TRANSITIONS = {
        'registered': ['picked_up', 'cancelled'],
        'picked_up': ['in_transit', 'cancelled'],
        'in_transit': ['out_for_delivery', 'returned'],
        'out_for_delivery': ['delivered', 'returned'],
        'delivered': [],
        'cancelled': [],
        'returned': ['registered']
    }
    
    def __init__(self, data_file='data/parcels.json'):
        self.data_file = data_file
        self.location_bst = None  # BST root
        self.history_head = None  # Linked list head
        self.history_tail = None  # Linked list tail
        self.history_map = {}     # Hash map for O(1) lookups
        self._load_and_index()
    
    # BST Insertion - O(log n)
    def _bst_insert(self, location, parcel):
        location = location.lower()
        if not self.location_bst:
            self.location_bst = LocationNode(location)
            self.location_bst.parcels.append(parcel)
            return
        
        current = self.location_bst
        while True:
            if location < current.location:
                if not current.left:
                    current.left = LocationNode(location)
                    current.left.parcels.append(parcel)
                    return
                current = current.left
            elif location > current.location:
                if not current.right:
                    current.right = LocationNode(location)
                    current.right.parcels.append(parcel)
                    return
                current = current.right
            else:
                current.parcels.append(parcel)
                return
    
    # BST Search - O(log n)
    def _bst_search(self, location):
        location = location.lower()
        current = self.location_bst
        while current:
            if location < current.location:
                current = current.left
            elif location > current.location:
                current = current.right
            else:
                return current.parcels
        return []
    
    # Linked List Insertion - O(1)
    def _add_history(self, tracking_num, event):
        node = HistoryNode(event)
        if not self.history_head:
            self.history_head = self.history_tail = node
        else:
            # Type assertion for Pylance
            tail = self.history_tail
            assert tail is not None
            tail.next = node
            node.prev = tail
            self.history_tail = node
        
        if tracking_num not in self.history_map:
            self.history_map[tracking_num] = []
        self.history_map[tracking_num].append(node)
    
    # Status Validation - O(1)
    def _validate_status(self, current, new):
        if new == current:
            return False, f"Already in '{new}' status"
        if new in self.VALID_TRANSITIONS.get(current, []):
            return True, None
        return False, f"Invalid: {current} → {new}"
    
    def _load_and_index(self):
        """Load and index - O(n log n)."""
        if not os.path.exists(self.data_file):
            return
        
        with open(self.data_file, 'r') as f:
            parcels = json.load(f)
        
        for parcel in parcels:
            loc = parcel.get('current_location', parcel.get('origin', 'unknown'))
            self._bst_insert(loc, parcel)
            
            tracking = parcel.get('tracking_number')
            if tracking and parcel.get('history'):
                for event in parcel['history']:
                    self._add_history(tracking, event)
    
    def update_location(self, tracking_num, location, status, notes=''):
        """Update location and status."""
        with open(self.data_file, 'r') as f:
            parcels = json.load(f)
        
        event = None
        for parcel in parcels:
            if parcel['tracking_number'] == tracking_num:
                current_status = parcel.get('status', 'registered')
                valid, msg = self._validate_status(current_status, status)
                if not valid:
                    return {'error': msg}
                
                parcel['status'] = status
                parcel['current_location'] = location
                
                event = {
                    'status': status,
                    'location': location,
                    'timestamp': datetime.now().isoformat(),
                    'notes': notes
                }
                parcel.setdefault('history', []).append(event)
                break
        
        if not event:
            return {'error': 'Parcel not found'}
        
        with open(self.data_file, 'w') as f:
            json.dump(parcels, f, indent=2, default=str)
        
        # Rebuild BST
        self.location_bst = None
        for p in parcels:
            loc = p.get('current_location', p.get('origin', 'unknown'))
            self._bst_insert(loc, p)
        
        self._add_history(tracking_num, event)
        return {'success': True, 'status': status, 'location': location}
    
    def track_parcel(self, tracking_num):
        """Get tracking info - O(n)."""
        with open(self.data_file, 'r') as f:
            parcels = json.load(f)
        
        for parcel in parcels:
            if parcel['tracking_number'] == tracking_num:
                return parcel
        return {'error': 'Not found'}
    
    def get_by_location(self, location):
        """Search by location - O(log n)."""
        return self._bst_search(location)
    
    def get_history(self, tracking_num):
        """Get history - O(k)."""
        if tracking_num not in self.history_map:
            return []
        return [node.data for node in self.history_map[tracking_num]]
    
    def get_statistics(self):
        """Get stats."""
        with open(self.data_file, 'r') as f:
            parcels = json.load(f)
        
        stats = {'total': len(parcels), 'by_status': {}, 'by_location': {}}
        for p in parcels:
            s = p.get('status', 'unknown')
            stats['by_status'][s] = stats['by_status'].get(s, 0) + 1
            
            loc = p.get('current_location', p.get('origin', 'unknown'))
            stats['by_location'][loc] = stats['by_location'].get(loc, 0) + 1
        
        return stats


# Demo
if __name__ == '__main__':
    tracker = ParcelLiveTracking()
    print("=== PARCEL LIVE TRACKING ===\n")
    
    from Parcel_Registration import ParcelRegistration
    reg = ParcelRegistration()
    parcel = reg.register_parcel("Alice", "Bob", "Nairobi", "Mombasa", 500)
    tracking_num = parcel['tracking_number']
    
    print("1. Update:", tracker.update_location(tracking_num, "Nairobi", "picked_up"))
    print("2. Track:", tracker.track_parcel(tracking_num)['status'])
    print("3. BST Search:", len(tracker.get_by_location("Nairobi")), "parcel(s)")
    print("4. History:", len(tracker.get_history(tracking_num)), "events")
    print("5. Stats:", tracker.get_statistics())
