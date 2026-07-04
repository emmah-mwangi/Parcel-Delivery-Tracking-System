"""
PARCEL REGISTRATION MODULE
==========================

This module handles creating new parcel records.

PROCESS:
1. Get sender and receiver names from user
2. Generate unique tracking ID
3. Create Parcel object
4. Store in parcel_database (Array/List data structure)

DATA STRUCTURE:
- Array/List (parcel_database): Stores all parcels in order
  - Adding new parcel: O(1) - just append to end
  - Access by index: O(1)
"""

from parcel_core import Parcel, parcel_database, generate_tracking_id, ensure_parcel


def register_parcel(sender, receiver, destination="", weight=0, description=""):
    """
    Register a new parcel in the system.
    
    Steps:
    1. Validate input (names can't be empty)
    2. Generate tracking ID
    3. Create Parcel object with all details
    4. Add to database
    
    Args:
        sender: Sender name
        receiver: Receiver name
        destination: Delivery destination
        weight: Parcel weight in kg
        description: Parcel contents/details
    
    Returns:
        Parcel object if successful, None if failed
    """
    # Check that both names are provided
    if not sender or not sender.strip() or not receiver or not receiver.strip():
        print("\n❌ Error: Sender and receiver names cannot be empty!")
        return None

    # Generate unique tracking ID
    tracking_id = generate_tracking_id()
    
    # Create new parcel with all details
    new_parcel = Parcel(tracking_id, sender, receiver, destination, weight, description)
    
    # Save to database (Array/List)
    ensure_parcel(new_parcel)

    print(f"\n  Success! Registered: {new_parcel}")
    print(f"   Tracking ID: {tracking_id}")
    print(f"   Destination: {destination}")
    if weight:
        print(f"   Weight: {weight} kg")
    return new_parcel


# Simple menu for testing
if __name__ == "__main__":
    print("=== PARCEL REGISTRATION ===")
    
    while True:
        print("\n1. Register New Parcel")
        print("2. View All Parcels")
        print("3. Exit")
        choice = input("Choose (1-3): ").strip()
        
        if choice == "1":
            sender = input("Sender Name: ")
            receiver = input("Receiver Name: ")
            register_parcel(sender, receiver)
            
        elif choice == "2":
            print("\n--- All Parcels ---")
            if not parcel_database:
                print("No parcels yet.")
            else:
                for parcel in parcel_database:
                    print(parcel)
                    
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")