"""
Parcel Live Tracking Module
Implements real-time parcel tracking with location updates and status monitoring.

Data Structures Used:
1. Binary Search Tree (BST) - O(log n) for efficient location-based searches
2. Doubly Linked List - O(1) for tracking history management

Algorithms Used:
1. Binary Search Tree Insertion/Search - O(log n) for location lookups
2. Status Transition Algorithm - O(1) for valid status changes
"""

import json
import os
from datetime import datetime
from collections import deque


class LocationNode:
    """
    Node for Binary Search Tree storing location-based parcel data.
    """
    
    def __init__(self, location, parcel):
        """
        Initialize location node.
        
        Args:
            location: Location name (used as BST key)
            parcel: Parcel data dictionary
        """
        self.location = location.lower()  # BST key (case-insensitive)
        self.parcels = [parcel]  # List of parcels at this location
        self.left = None
        self.right = None


class TrackingHistoryNode:
    """
    Node for Doubly Linked List storing tracking history.
    """
    
    def __init__(self, data):
        """
        Initialize history node.
        
        Args:
            data: Tracking event data dictionary
        """
        self.data = data
        self.timestamp = data.get('timestamp', datetime.utcnow().isoformat())
        self.prev = None
        self.next = None


class ParcelLiveTracking:
    """
    Manages real-time parcel tracking with efficient data structures.
    """
    
    # Valid status transitions
    VALID_TRANSITIONS = {
        'registered': ['picked_up', 'cancelled'],
        'picked_up': ['in_transit', 'cancelled'],
        'in_transit': ['out_for_delivery', 'returned'],
        'out_for_delivery': ['delivered', 'returned'],
        'delivered': [],
        'cancelled': [],
        'returned': ['registered']
    }
    
    def __init__(self, data_dir='data'):
        """
        Initialize the tracking system.
        
        Args:
            data_dir: Directory path for storing data
        """
        self.data_dir = data_dir
        self.parcels_file = os.path.join(data_dir, 'parcels.json')
        os.makedirs(data_dir, exist_ok=True)
        
        # Data Structure 1: Binary Search Tree for location-based searches
        self.location_bst = None
        
        # Data Structure 2: Doubly Linked List for tracking history
        self.history_head = None
        self.history_tail = None
        self.history_map = {}  # Maps tracking_number to history node
        
        # Load existing data
        self._load_data()
    
    def _load_data(self):
        """
        Load parcels and build BST index.
        Time Complexity: O(n log n) for BST construction
        """
        if os.path.exists(self.parcels_file):
            try:
                with open(self.parcels_file, 'r', encoding='utf-8') as f:
                    parcels = json.load(f)
                    
                    # Build BST from parcels
                    for parcel in parcels:
                        location = parcel.get('current_location', parcel.get('origin', 'unknown'))
                        self._bst_insert(location, parcel)
                        
                        # Build history linked list
                        tracking = parcel.get('tracking_number')
                        if tracking and parcel.get('history'):
                            for event in parcel['history']:
                                self._add_history_node(tracking, event)
            except Exception as e:
                print(f"Error loading tracking data: {e}")
    
    def _bst_insert(self, location, parcel):
        """
        Insert parcel into Binary Search Tree by location.
        
        Algorithm 1: BST Insertion
        Time Complexity: O(log n) average case, O(n) worst case
        Space Complexity: O(1)
        
        Args:
            location: Location string (BST key)
            parcel: Parcel data dictionary
        """
        location = location.lower()
        
        if self.location_bst is None:
            self.location_bst = LocationNode(location, parcel)
            return
        
        current = self.location_bst
        
        while True:
            if location < current.location:
                if current.left is None:
                    current.left = LocationNode(location, parcel)
                    return
                current = current.left
            elif location > current.location:
                if current.right is None:
                    current.right = LocationNode(location, parcel)
                    return
                current = current.right
            else:
                # Location exists, add parcel to node
                current.parcels.append(parcel)
                return
    
    def _bst_search(self, location):
        """
        Search BST for parcels at a specific location.
        
        Algorithm 1: BST Search
        Time Complexity: O(log n) average case, O(n) worst case
        Space Complexity: O(1)
        
        Args:
            location: Location to search for
            
        Returns:
            list: List of parcels at the location, or empty list if not found
        """
        location = location.lower()
        current = self.location_bst
        
        while current is not None:
            if location < current.location:
                current = current.left
            elif location > current.location:
                current = current.right
            else:
                return current.parcels
        
        return []
    
    def _bst_range_search(self, min_location, max_location):
        """
        Search BST for parcels within a location range.
        
        Algorithm 1: BST Range Search
        Time Complexity: O(log n + k) where k is number of results
        Space Complexity: O(k)
        
        Args:
            min_location: Minimum location (inclusive)
            max_location: Maximum location (inclusive)
            
        Returns:
            list: List of parcels in the range
        """
        results = []
        min_loc = min_location.lower()
        max_loc = max_location.lower()
        
        def _inorder_traversal(node):
            if node is None:
                return
            
            # Traverse left if current node is greater than min
            if node.location >= min_loc:
                _inorder_traversal(node.left)
            
            # Add current node if in range
            if min_loc <= node.location <= max_loc:
                results.extend(node.parcels)
            
            # Traverse right if current node is less than max
            if node.location <= max_loc:
                _inorder_traversal(node.right)
        
        _inorder_traversal(self.location_bst)
        return results
    
    def _add_history_node(self, tracking_number, event_data):
        """
        Add event to doubly linked list history.
        
        Algorithm 2: Doubly Linked List Insertion
        Time Complexity: O(1)
        Space Complexity: O(1)
        
        Args:
            tracking_number: Parcel tracking number
            event_data: Event data dictionary
        """
        new_node = TrackingHistoryNode(event_data)
        
        # Add to end of linked list
        if self.history_tail is None:
            self.history_head = new_node
            self.history_tail = new_node
        else:
            self.history_tail.next = new_node
            new_node.prev = self.history_tail
            self.history_tail = new_node
        
        # Map tracking number to this node
        if tracking_number not in self.history_map:
            self.history_map[tracking_number] = []
        self.history_map[tracking_number].append(new_node)
    
    def _validate_status_transition(self, current_status, new_status):
        """
        Algorithm 2: Status Transition Validation
        Validates if status change is allowed.
        
        Time Complexity: O(1)
        Space Complexity: O(1)
        
        Args:
            current_status: Current parcel status
            new_status: Desired new status
            
        Returns:
            tuple: (is_valid, error_message)
        """
        allowed = self.VALID_TRANSITIONS.get(current_status, [])
        
        if new_status in allowed:
            return True, None
        
        if new_status == current_status:
            return False, f"Parcel is already in '{new_status}' status"
        
        return False, f"Invalid transition from '{current_status}' to '{new_status}'"
    
    def update_parcel_location(self, tracking_number, new_location, status, notes=''):
        """
        Update parcel location and status.
        
        Args:
            tracking_number: Parcel tracking number
            new_location: New location
            status: New status
            notes: Optional notes about the update
            
        Returns:
            dict: Updated tracking information or error
        """
        # Load current parcels
        if not os.path.exists(self.parcels_file):
            return {'error': 'No parcels found'}
        
        try:
            with open(self.parcels_file, 'r', encoding='utf-8') as f:
                parcels = json.load(f)
        except Exception:
            return {'error': 'Failed to load parcels'}
        
        # Find and update parcel
        parcel_found = None
        for parcel in parcels:
            if parcel.get('tracking_number') == tracking_number:
                current_status = parcel.get('status', 'registered')
                
                # Validate status transition
                is_valid, error_msg = self._validate_status_transition(current_status, status)
                if not is_valid:
                    return {'error': error_msg}
                
                # Update parcel
                parcel['status'] = status
                parcel['current_location'] = new_location
                
                # Add to history
                history_entry = {
                    'status': status,
                    'location': new_location,
                    'timestamp': datetime.utcnow().isoformat(),
                    'notes': notes
                }
                parcel.setdefault('history', []).append(history_entry)
                
                parcel_found = parcel
                break
        
        if not parcel_found:
            return {'error': 'Parcel not found'}
        
        # Save updated data
        try:
            with open(self.parcels_file, 'w', encoding='utf-8') as f:
                json.dump(parcels, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            return {'error': f'Failed to save: {str(e)}'}
        
        # Update BST (remove from old location, add to new)
        # Note: For simplicity, we rebuild BST. In production, would do targeted update.
        self.location_bst = None
        for p in parcels:
            loc = p.get('current_location', p.get('origin', 'unknown'))
            self._bst_insert(loc, p)
        
        # Add to history linked list
        self._add_history_node(tracking_number, history_entry)
        
        return {
            'tracking_number': tracking_number,
            'status': status,
            'location': new_location,
            'timestamp': history_entry['timestamp'],
            'message': 'Tracking updated successfully'
        }
    
    def get_parcel_tracking(self, tracking_number):
        """
        Get complete tracking history for a parcel.
        
        Args:
            tracking_number: Parcel tracking number
            
        Returns:
            dict: Parcel data with full history or error
        """
        if not os.path.exists(self.parcels_file):
            return {'error': 'No parcels found'}
        
        try:
            with open(self.parcels_file, 'r', encoding='utf-8') as f:
                parcels = json.load(f)
        except Exception:
            return {'error': 'Failed to load parcels'}
        
        for parcel in parcels:
            if parcel.get('tracking_number') == tracking_number:
                return parcel
        
        return {'error': 'Parcel not found'}
    
    def get_parcels_by_location(self, location):
        """
        Get all parcels at a specific location using BST.
        
        Time Complexity: O(log n)
        
        Args:
            location: Location to search
            
        Returns:
            list: List of parcels at the location
        """
        return self._bst_search(location)
    
    def get_parcels_by_location_range(self, min_location, max_location):
        """
        Get all parcels within a location range using BST.
        
        Time Complexity: O(log n + k)
        
        Args:
            min_location: Minimum location
            max_location: Maximum location
            
        Returns:
            list: List of parcels in range
        """
        return self._bst_range_search(min_location, max_location)
    
    def get_parcels_by_status(self, status):
        """
        Get all parcels with a specific status.
        
        Time Complexity: O(n)
        
        Args:
            status: Status to filter by
            
        Returns:
            list: List of parcels with matching status
        """
        if not os.path.exists(self.parcels_file):
            return []
        
        try:
            with open(self.parcels_file, 'r', encoding='utf-8') as f:
                parcels = json.load(f)
        except Exception:
            return []
        
        return [p for p in parcels if p.get('status') == status]
    
    def get_tracking_history_linked_list(self, tracking_number):
        """
        Get tracking history using linked list traversal.
        
        Time Complexity: O(k) where k is history length
        
        Args:
            tracking_number: Parcel tracking number
            
        Returns:
            list: List of tracking events in chronological order
        """
        if tracking_number not in self.history_map:
            return []
        
        # Traverse linked list from the first node
        nodes = self.history_map[tracking_number]
        return [node.data for node in nodes]
    
    def get_recent_updates(self, limit=10):
        """
        Get most recent tracking updates across all parcels.
        
        Time Complexity: O(n) where n is total history events
        
        Args:
            limit: Maximum number of updates to return
            
        Returns:
            list: List of recent tracking events
        """
        # Collect all events
        all_events = []
        current = self.history_head
        
        while current is not None and len(all_events) < limit:
            all_events.append(current.data)
            current = current.next
        
        # Sort by timestamp (most recent first)
        all_events.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return all_events[:limit]
    
    def estimate_delivery_time(self, tracking_number):
        """
        Estimate delivery time based on current status and history.
        
        Args:
            tracking_number: Parcel tracking number
            
        Returns:
            dict: Delivery estimation or error
        """
        parcel = self.get_parcel_tracking(tracking_number)
        
        if 'error' in parcel:
            return parcel
        
        status = parcel.get('status', 'registered')
        history = parcel.get('history', [])
        
        # Calculate average time between status changes
        if len(history) >= 2:
            timestamps = [datetime.fromisoformat(h['timestamp']) for h in history if 'timestamp' in h]
            
            if len(timestamps) >= 2:
                total_time = sum(
                    (timestamps[i+1] - timestamps[i]).total_seconds() 
                    for i in range(len(timestamps)-1)
                )
                avg_time_per_stage = total_time / (len(timestamps) - 1)
                
                # Estimate remaining stages
                remaining_stages = 0
                if status == 'registered':
                    remaining_stages = 3  # picked_up, in_transit, delivered
                elif status == 'picked_up':
                    remaining_stages = 2  # in_transit, delivered
                elif status == 'in_transit':
                    remaining_stages = 1  # out_for_delivery, delivered (simplified)
                
                estimated_seconds = avg_time_per_stage * remaining_stages
                
                from datetime import timedelta
                estimated_delivery = datetime.utcnow() + timedelta(seconds=estimated_seconds)
                
                return {
                    'tracking_number': tracking_number,
                    'current_status': status,
                    'estimated_delivery': estimated_delivery.isoformat(),
                    'confidence': 'medium'  # Based on limited data
                }
        
        return {
            'tracking_number': tracking_number,
            'current_status': status,
            'estimated_delivery': None,
            'message': 'Insufficient data for estimation'
        }
    
    def get_statistics(self):
        """
        Get tracking statistics.
        
        Returns:
            dict: Tracking statistics
        """
        if not os.path.exists(self.parcels_file):
            return {'error': 'No data available'}
        
        try:
            with open(self.parcels_file, 'r', encoding='utf-8') as f:
                parcels = json.load(f)
        except Exception:
            return {'error': 'Failed to load data'}
        
        total = len(parcels)
        status_counts = {}
        location_counts = {}
        
        for parcel in parcels:
            status = parcel.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
            
            location = parcel.get('current_location', parcel.get('origin', 'unknown'))
            location_counts[location] = location_counts.get(location, 0) + 1
        
        return {
            'total_parcels': total,
            'status_distribution': status_counts,
            'location_distribution': location_counts,
            'total_tracking_events': len(self.history_map)
        }


# Example usage and testing
if __name__ == '__main__':
    # Initialize tracking system
    tracking_system = ParcelLiveTracking()
    
    print("Parcel Live Tracking System Test")
    print("=" * 50)
    
    # Test 1: Update parcel location
    print("\nTest 1: Update parcel location...")
    # First register a parcel
    from Parcel_Registration import ParcelRegistration
    reg_system = ParcelRegistration()
    parcel = reg_system.register_parcel(
        "Sender A", "Receiver B", "Nairobi", "Mombasa", 10.0
    )
    tracking_num = parcel['tracking_number']
    print(f"Registered parcel: {tracking_num}")
    
    # Update location
    result = tracking_system.update_parcel_location(
        tracking_num, "Nairobi", "picked_up", "Package picked up from Mombasa"
    )
    print(f"Updated: {result}")
    
    # Test 2: BST location search
    print("\nTest 2: Search parcels by location (BST)...")
    parcels_at_nairobi = tracking_system.get_parcels_by_location("Nairobi")
    print(f"Parcels in Nairobi: {len(parcels_at_nairobi)}")
    
    # Test 3: Get tracking history
    print("\nTest 3: Get tracking history (Linked List)...")
    history = tracking_system.get_tracking_history_linked_list(tracking_num)
    print(f"History events: {len(history)}")
    for event in history:
        print(f"  - {event.get('timestamp')}: {event.get('status')} at {event.get('location')}")
    
    # Test 4: Estimate delivery time
    print("\nTest 4: Estimate delivery time...")
    estimation = tracking_system.estimate_delivery_time(tracking_num)
    print(f"Estimation: {estimation}")
    
    # Test 5: Statistics
    print("\nTest 5: Tracking statistics...")
    stats = tracking_system.get_statistics()
    print(f"Statistics: {stats}")