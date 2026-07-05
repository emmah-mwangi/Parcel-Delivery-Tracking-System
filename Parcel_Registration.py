"""
Parcel Registration Module
Handles parcel registration, validation, and storage.
"""
import json
import os
import uuid
from datetime import datetime
from collections import deque


class ParcelRegistration:
    """Manages parcel registration with hash table for O(1) lookups."""
    
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.parcels_file = os.path.join(data_dir, 'parcels.json')
        os.makedirs(data_dir, exist_ok=True)
        self.parcel_index = {}  # Hash table for O(1) lookups
        self.registration_queue = deque()  # Queue for batch processing
        self._load_parcels()
    
    def _load_parcels(self):
        """Load parcels from JSON into hash table."""
        if os.path.exists(self.parcels_file):
            try:
                with open(self.parcels_file, 'r', encoding='utf-8') as f:
                    for parcel in json.load(f):
                        tracking = parcel.get('tracking_number')
                        if tracking:
                            self.parcel_index[tracking] = parcel
            except Exception as e:
                print(f"Error loading parcels: {e}")
    
    def _save_parcels(self):
        """Save parcels from hash table to JSON file."""
        with open(self.parcels_file, 'w', encoding='utf-8') as f:
            json.dump(list(self.parcel_index.values()), f, indent=2, 
                     ensure_ascii=False, default=str)
    
    def _validate_input(self, sender, receiver, destination, origin, weight):
        """Validate input fields. Returns (is_valid, error_message)."""
        if not all([sender, receiver, destination, origin]) or not all(isinstance(x, str) for x in [sender, receiver, destination, origin]):
            return False, "All fields must be non-empty strings"
        
        try:
            weight = float(weight)
            if weight <= 0 or weight > 1000:
                return False, "Weight must be 0-1000 kg"
        except (ValueError, TypeError):
            return False, "Invalid weight value"
        
        # Sanitize and check length
        sender, receiver = sender.strip(), receiver.strip()
        if not (2 <= len(sender) <= 100 and 2 <= len(receiver) <= 100):
            return False, "Names must be 2-100 characters"
        
        return True, None
    
    def _generate_tracking(self):
        """Generate unique tracking number using UUID."""
        return str(uuid.uuid4()).split('-')[0].upper()
    
    def register_parcel(self, sender_name, receiver_name, destination, origin, weight_kg, status='registered'):
        """Register a new parcel. Returns parcel dict or error dict."""
        # Validate input
        is_valid, error_msg = self._validate_input(
            sender_name, receiver_name, destination, origin, weight_kg
        )
        if not is_valid:
            return {'error': error_msg}
        
        # Generate unique tracking number
        tracking_number = self._generate_tracking()
        while tracking_number in self.parcel_index:
            tracking_number = self._generate_tracking()
        
        # Create parcel object
        now = datetime.utcnow().isoformat()
        parcel = {
            'tracking_number': tracking_number,
            'sender_name': sender_name.strip(),
            'receiver_name': receiver_name.strip(),
            'destination': destination.strip(),
            'origin': origin.strip(),
            'weight_kg': float(weight_kg),
            'status': status,
            'registered_at': now,
            'history': [{'status': status, 'timestamp': now, 'location': origin.strip()}]
        }
        
        # Store in hash table and queue
        self.parcel_index[tracking_number] = parcel
        self.registration_queue.append(parcel)
        self._save_parcels()
        
        return parcel
    
    def get_parcel(self, tracking_number):
        """Retrieve parcel by tracking number. O(1) lookup."""
        return self.parcel_index.get(tracking_number)
    
    def get_all_parcels(self):
        """Get all registered parcels."""
        return list(self.parcel_index.values())
    
    def update_status(self, tracking_number, new_status, location=''):
        """Update parcel status and add to history."""
        parcel = self.get_parcel(tracking_number)
        if not parcel:
            return {'error': 'Parcel not found'}
        
        parcel['status'] = new_status
        parcel.setdefault('history', []).append({
            'status': new_status, 'timestamp': datetime.utcnow().isoformat(), 'location': location
        })
        self._save_parcels()
        return parcel
    
    def delete_parcel(self, tracking_number):
        """Delete parcel. Returns True if deleted, False if not found."""
        if tracking_number in self.parcel_index:
            del self.parcel_index[tracking_number]
            self._save_parcels()
            return True
        return False
    
    def search_parcels(self, **criteria):
        """Search parcels by criteria. Returns matching parcels."""
        return [p for p in self.parcel_index.values() 
                if all(p.get(k) == v for k, v in criteria.items())]
    
    def get_statistics(self):
        """Get registration statistics."""
        parcels = list(self.parcel_index.values())
        total = len(parcels)
        status_counts = {}
        total_weight = sum(float(p.get('weight_kg', 0)) for p in parcels)
        
        for p in parcels:
            status_counts[p.get('status', 'unknown')] = status_counts.get(p.get('status', 'unknown'), 0) + 1
        
        return {
            'total_parcels': total,
            'status_distribution': status_counts,
            'total_weight_kg': round(total_weight, 2),
            'average_weight_kg': round(total_weight / total, 2) if total > 0 else 0
        }


# Interactive Menu
if __name__ == '__main__':
    print("=== PARCEL REGISTRATION SYSTEM ===")
    reg_system = ParcelRegistration()
    
    while True:
        print("\n1. Register Parcel")
        print("2. View All Parcels")
        print("3. Search Parcel")
        print("4. Update Status")
        print("5. Delete Parcel")
        print("6. Statistics")
        print("7. Exit")
        choice = input("Select (1-7): ").strip()
        
        if choice == "1":
            data = {
                'sender_name': input("Sender Name: "),
                'receiver_name': input("Receiver Name: "),
                'destination': input("Destination: "),
                'origin': input("Origin: "),
                'weight_kg': input("Weight (kg): ")
            }
            result = reg_system.register_parcel(**data)
            if 'error' in result:
                print(f"\n  Error: {result['error']}")
            else:
                print(f"\n  Registered! Tracking: {result['tracking_number']}")
        
        elif choice == "2":
            parcels = reg_system.get_all_parcels()
            print(f"\n--- Parcels ({len(parcels)}) ---")
            for p in parcels:
                print(f"[{p['tracking_number']}] {p['sender_name']} → {p['receiver_name']} | {p['status']}")
        
        elif choice == "3":
            tracking = input("Enter tracking number: ").strip()
            parcel = reg_system.get_parcel(tracking)
            if parcel:
                print(f"\nFound: {parcel['sender_name']} → {parcel['receiver_name']}")
                print(f"Status: {parcel['status']} | Weight: {parcel['weight_kg']}kg")
            else:
                print("\n  Parcel not found")
        
        elif choice == "4":
            tracking = input("Tracking number: ").strip()
            status = input("New status: ").strip()
            location = input("Location: ").strip()
            result = reg_system.update_status(tracking, status, location)
            print(f"\n{'  Updated' if 'error' not in result else '  Error'}: {result.get('error', result['status'])}")
        
        elif choice == "5":
            tracking = input("Tracking number: ").strip()
            if reg_system.delete_parcel(tracking):
                print("\n  Parcel deleted")
            else:
                print("\n  Parcel not found")
        
        elif choice == "6":
            stats = reg_system.get_statistics()
            print(f"\nTotal: {stats['total_parcels']} | Avg Weight: {stats['average_weight_kg']}kg")
            print(f"Status: {stats['status_distribution']}")
        
        elif choice == "7":
            print("Exiting. Goodbye!")
            break
        else:
            print("Invalid choice!")