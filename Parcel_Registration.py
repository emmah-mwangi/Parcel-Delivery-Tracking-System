"""
Parcel Registration Module
Handles parcel registration, validation, and storage management.

Data Structures Used:
1. Hash Table (Dictionary) - O(1) average case for tracking number lookups
2. Queue - O(1) for registration processing and batch operations

Algorithms Used:
1. Validation Algorithm - O(n) for input validation and sanitization
2. Duplicate Detection Algorithm - O(1) using hash-based lookup
"""

import json
import os
import uuid
from datetime import datetime
from collections import deque


class ParcelRegistration:
    """
    Manages parcel registration with efficient data structures and algorithms.
    """
    
    def __init__(self, data_dir='data'):
        """
        Initialize the registration system.
        
        Args:
            data_dir: Directory path for storing parcel data
        """
        self.data_dir = data_dir
        self.parcels_file = os.path.join(data_dir, 'parcels.json')
        os.makedirs(data_dir, exist_ok=True)
        
        # Data Structure 1: Hash Table (Dictionary) for O(1) tracking number lookups
        self.parcel_index = {}
        
        # Data Structure 2: Queue for batch registration processing
        self.registration_queue = deque()
        
        # Load existing parcels into hash table
        self._load_parcels()
    
    def _load_parcels(self):
        """
        Load parcels from JSON file into hash table index.
        Time Complexity: O(n) where n is number of parcels
        """
        if os.path.exists(self.parcels_file):
            try:
                with open(self.parcels_file, 'r', encoding='utf-8') as f:
                    parcels = json.load(f)
                    # Build hash table index for O(1) lookups
                    for parcel in parcels:
                        tracking = parcel.get('tracking_number')
                        if tracking:
                            self.parcel_index[tracking] = parcel
            except Exception as e:
                print(f"Error loading parcels: {e}")
    
    def _save_parcels(self):
        """
        Save all parcels from hash table to JSON file.
        Time Complexity: O(n)
        """
        parcels = list(self.parcel_index.values())
        with open(self.parcels_file, 'w', encoding='utf-8') as f:
            json.dump(parcels, f, indent=2, ensure_ascii=False, default=str)
    
    def _validate_input(self, sender_name, receiver_name, destination, origin, weight_kg):
        """
        Algorithm 1: Input Validation Algorithm
        Validates all input fields for correctness and safety.
        
        Time Complexity: O(n) where n is length of longest string
        Space Complexity: O(1)
        
        Args:
            sender_name: Sender's name
            receiver_name: Receiver's name
            destination: Delivery destination
            origin: Pickup location
            weight_kg: Package weight in kilograms
            
        Returns:
            tuple: (is_valid, error_message)
        """
        # Check for None or empty values
        if not sender_name or not isinstance(sender_name, str):
            return False, "Invalid sender name"
        
        if not receiver_name or not isinstance(receiver_name, str):
            return False, "Invalid receiver name"
        
        if not destination or not isinstance(destination, str):
            return False, "Invalid destination"
        
        if not origin or not isinstance(origin, str):
            return False, "Invalid origin"
        
        # Validate weight
        try:
            weight = float(weight_kg)
            if weight <= 0 or weight > 1000:
                return False, "Weight must be between 0 and 1000 kg"
        except (ValueError, TypeError):
            return False, "Invalid weight value"
        
        # Sanitize strings (remove leading/trailing whitespace)
        sender_name = sender_name.strip()
        receiver_name = receiver_name.strip()
        destination = destination.strip()
        origin = origin.strip()
        
        if len(sender_name) < 2 or len(sender_name) > 100:
            return False, "Sender name must be 2-100 characters"
        
        if len(receiver_name) < 2 or len(receiver_name) > 100:
            return False, "Receiver name must be 2-100 characters"
        
        return True, None
    
    def _generate_tracking_number(self):
        """
        Generate unique tracking number using UUID.
        Time Complexity: O(1)
        
        Returns:
            str: Unique tracking number
        """
        return str(uuid.uuid4()).split('-')[0].upper()
    
    def _check_duplicate(self, tracking_number):
        """
        Algorithm 2: Duplicate Detection Algorithm
        Uses hash table for O(1) duplicate checking.
        
        Time Complexity: O(1) average case
        Space Complexity: O(1)
        
        Args:
            tracking_number: Tracking number to check
            
        Returns:
            bool: True if duplicate exists, False otherwise
        """
        return tracking_number in self.parcel_index
    
    def register_parcel(self, sender_name, receiver_name, destination, origin, weight_kg, status='registered'):
        """
        Register a new parcel in the system.
        
        Args:
            sender_name: Sender's full name
            receiver_name: Receiver's full name
            destination: Delivery destination address
            origin: Pickup location
            weight_kg: Package weight in kilograms
            status: Initial status (default: 'registered')
            
        Returns:
            dict: Registered parcel object or error message
        """
        # Step 1: Validate input using validation algorithm
        is_valid, error_msg = self._validate_input(
            sender_name, receiver_name, destination, origin, weight_kg
        )
        
        if not is_valid:
            return {'error': error_msg}
        
        # Step 2: Generate unique tracking number
        tracking_number = self._generate_tracking_number()
        
        # Step 3: Check for duplicates (should not happen with UUID, but safety check)
        while self._check_duplicate(tracking_number):
            tracking_number = self._generate_tracking_number()
        
        # Step 4: Create parcel object
        parcel = {
            'tracking_number': tracking_number,
            'sender_name': sender_name.strip(),
            'receiver_name': receiver_name.strip(),
            'destination': destination.strip(),
            'origin': origin.strip(),
            'weight_kg': float(weight_kg),
            'status': status,
            'registered_at': datetime.utcnow().isoformat(),
            'history': [
                {
                    'status': status,
                    'timestamp': datetime.utcnow().isoformat(),
                    'location': origin.strip()
                }
            ]
        }
        
        # Step 5: Add to hash table (O(1) operation)
        self.parcel_index[tracking_number] = parcel
        
        # Step 6: Add to registration queue for batch processing
        self.registration_queue.append(parcel)
        
        # Step 7: Persist to file
        self._save_parcels()
        
        return parcel
    
    def batch_register(self, parcels_data):
        """
        Register multiple parcels using queue-based batch processing.
        
        Args:
            parcels_data: List of parcel data dictionaries
            
        Returns:
            dict: Summary of batch registration results
        """
        successful = []
        failed = []
        
        for data in parcels_data:
            result = self.register_parcel(
                data.get('sender_name', ''),
                data.get('receiver_name', ''),
                data.get('destination', ''),
                data.get('origin', ''),
                data.get('weight_kg', 0),
                data.get('status', 'registered')
            )
            
            if 'error' in result:
                failed.append(result)
            else:
                successful.append(result)
        
        return {
            'successful_count': len(successful),
            'failed_count': len(failed),
            'successful': successful,
            'failed': failed
        }
    
    def get_parcel(self, tracking_number):
        """
        Retrieve parcel by tracking number using hash table lookup.
        
        Time Complexity: O(1) average case
        
        Args:
            tracking_number: Unique tracking number
            
        Returns:
            dict: Parcel object or None if not found
        """
        return self.parcel_index.get(tracking_number)
    
    def get_all_parcels(self):
        """
        Retrieve all registered parcels.
        
        Time Complexity: O(n)
        
        Returns:
            list: List of all parcel objects
        """
        return list(self.parcel_index.values())
    
    def update_parcel_status(self, tracking_number, new_status, location=''):
        """
        Update parcel status and add to history.
        
        Args:
            tracking_number: Tracking number
            new_status: New status value
            location: Current location
            
        Returns:
            dict: Updated parcel or error message
        """
        parcel = self.get_parcel(tracking_number)
        
        if not parcel:
            return {'error': 'Parcel not found'}
        
        # Update status
        parcel['status'] = new_status
        
        # Add to history
        history_entry = {
            'status': new_status,
            'timestamp': datetime.utcnow().isoformat(),
            'location': location
        }
        parcel.setdefault('history', []).append(history_entry)
        
        # Save changes
        self._save_parcels()
        
        return parcel
    
    def delete_parcel(self, tracking_number):
        """
        Delete a parcel from the system.
        
        Args:
            tracking_number: Tracking number
            
        Returns:
            bool: True if deleted, False if not found
        """
        if tracking_number in self.parcel_index:
            del self.parcel_index[tracking_number]
            self._save_parcels()
            return True
        return False
    
    def search_parcels(self, **criteria):
        """
        Search parcels by various criteria.
        
        Args:
            criteria: Key-value pairs to search (e.g., status='in_transit', destination='Nairobi')
            
        Returns:
            list: Matching parcels
        """
        results = []
        
        for parcel in self.parcel_index.values():
            match = True
            for key, value in criteria.items():
                if parcel.get(key) != value:
                    match = False
                    break
            
            if match:
                results.append(parcel)
        
        return results
    
    def get_statistics(self):
        """
        Get registration statistics.
        
        Returns:
            dict: Statistics about registered parcels
        """
        parcels = list(self.parcel_index.values())
        
        total = len(parcels)
        status_counts = {}
        total_weight = 0
        
        for parcel in parcels:
            status = parcel.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
            
            try:
                total_weight += float(parcel.get('weight_kg', 0))
            except Exception:
                pass
        
        return {
            'total_parcels': total,
            'status_distribution': status_counts,
            'total_weight_kg': round(total_weight, 2),
            'average_weight_kg': round(total_weight / total, 2) if total > 0 else 0
        }


# Example usage and testing
if __name__ == '__main__':
    # Initialize registration system
    reg_system = ParcelRegistration()
    
    # Test 1: Register a single parcel
    print("Test 1: Registering a parcel...")
    parcel1 = reg_system.register_parcel(
        sender_name="John Doe",
        receiver_name="Jane Smith",
        destination="Nairobi, Kenya",
        origin="Mombasa, Kenya",
        weight_kg=5.5
    )
    print(f"Registered: {parcel1['tracking_number']}")
    
    # Test 2: Retrieve parcel
    print("\nTest 2: Retrieving parcel...")
    retrieved = reg_system.get_parcel(parcel1['tracking_number'])
    print(f"Found: {retrieved['sender_name']} -> {retrieved['receiver_name']}")
    
    # Test 3: Batch registration
    print("\nTest 3: Batch registration...")
    batch_data = [
        {'sender_name': 'Alice', 'receiver_name': 'Bob', 'destination': 'Kisumu', 'origin': 'Nairobi', 'weight_kg': 2.0},
        {'sender_name': 'Charlie', 'receiver_name': 'Diana', 'destination': 'Eldoret', 'origin': 'Nakuru', 'weight_kg': 3.5}
    ]
    result = reg_system.batch_register(batch_data)
    print(f"Batch result: {result['successful_count']} successful, {result['failed_count']} failed")
    
    # Test 4: Statistics
    print("\nTest 4: Statistics...")
    stats = reg_system.get_statistics()
    print(f"Total parcels: {stats['total_parcels']}")
    print(f"Status distribution: {stats['status_distribution']}")
    
    # Test 5: Search
    print("\nTest 5: Search parcels...")
    found = reg_system.search_parcels(status='registered')
    print(f"Found {len(found)} registered parcels")