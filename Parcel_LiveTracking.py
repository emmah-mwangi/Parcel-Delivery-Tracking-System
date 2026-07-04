"""
PARCEL TRACKING MODULE
======================

This module handles searching and tracking parcels.

SEARCHING ALGORITHMS USED:
1. Binary Search - O(log n)
   - Fast search by tracking ID
   - Requires sorted list
   - Cuts search space in half each time

2. Linear Search - O(n)
   - Search by sender or receiver name
   - Checks each parcel one by one
   - Simple and reliable

DATA STRUCTURES:
- Array/List (parcel_database): Stores all parcels for searching
"""

from datetime import datetime
from parcel_core import Parcel, parcel_database, generate_tracking_id, ensure_parcel

VALID_STATUSES = [
    "Registered", "Picked Up", "In Transit",
    "Out for Delivery", "Delivered", "Returned"
]


def register_parcel(sender, receiver):
    """Register a new parcel (helper function)"""
    if not sender or not sender.strip() or not receiver or not receiver.strip():
        print("\n  Error: Sender and receiver names cannot be empty!")
        return None

    tracking_id = generate_tracking_id()
    new_parcel = Parcel(tracking_id, sender, receiver)
    ensure_parcel(new_parcel)
    print(f"\n  Registered: {new_parcel}")
    return new_parcel


def sort_by_id():
    """
    Sort parcels by tracking ID.
    Needed for Binary Search to work.
    Time: O(n log n)
    """
    parcel_database.sort(key=lambda p: p.tracking_id)


# ========== BINARY SEARCH ==========

def binary_search(tracking_id):
    """
    Find parcel by tracking ID using BINARY SEARCH.
    
    Algorithm: Binary Search
    - List must be sorted first
    - Compare middle element with target
    - If match: found!
    - If target < middle: search left half
    - If target > middle: search right half
    - Repeat until found or exhausted
    
    Time Complexity: O(log n) - very fast!
    Space Complexity: O(1)
    
    Example:
        List: [KE-1000, KE-2000, KE-3000, KE-4000, KE-5000]
        Search: KE-3000
        1. Check middle (KE-3000) - found!
        
        Search: KE-4000
        1. Check middle (KE-3000) - too low, search right
        2. Check middle of right half (KE-4000) - found!
    """
    sort_by_id()  # Binary search requires sorted list
    target = tracking_id.upper()
    low = 0
    high = len(parcel_database) - 1

    while low <= high:
        mid = (low + high) // 2
        mid_id = parcel_database[mid].tracking_id

        if mid_id == target:
            return parcel_database[mid]  # Found it!
        elif mid_id < target:
            low = mid + 1  # Search right half
        else:
            high = mid - 1  # Search left half

    return None  # Not found


# ========== LINEAR SEARCH ==========

def search_by_sender(name):
    """
    Find all parcels by sender name using LINEAR SEARCH.
    
    Algorithm: Linear Search
    - Check each parcel one by one
    - Compare sender name (case-insensitive)
    - Add matches to results
    
    Time Complexity: O(n) - checks all parcels
    Space Complexity: O(k) - k = number of matches
    
    Args:
        name: Sender name to search for
    
    Returns:
        List of matching parcels
    """
    results = []
    for parcel in parcel_database:  # Check every parcel
        if name.lower() in parcel.sender.lower():
            results.append(parcel)
    return results


def search_by_receiver(name):
    """
    Find all parcels by receiver name using LINEAR SEARCH.
    
    Algorithm: Linear Search
    - Same as search_by_sender but for receiver
    
    Time Complexity: O(n)
    Space Complexity: O(k)
    """
    results = []
    for parcel in parcel_database:  # Check every parcel
        if name.lower() in parcel.receiver.lower():
            results.append(parcel)
    return results


# ========== TRACKING ==========

def track_parcel(tracking_id):
    """
    Show full details of a parcel.
    
    Uses Binary Search to find parcel quickly.
    """
    parcel = binary_search(tracking_id)
    if parcel is None:
        print(f"\n  No parcel found with ID '{tracking_id.upper()}'.")
        return

    print("\n" + "="*48)
    print(f"  Tracking ID : {parcel.tracking_id}")
    print(f"  Sender      : {parcel.sender}")
    print(f"  Receiver    : {parcel.receiver}")
    print(f"  Status      : {parcel.status}")
    print("  --- History ---")
    for status, timestamp in parcel.history:
        print(f"    {timestamp} → {status}")
    print("="*48)


def update_status(tracking_id, new_status):
    """Update parcel status"""
    if new_status not in VALID_STATUSES:
        print(f"\n  Invalid status. Choose from: {', '.join(VALID_STATUSES)}")
        return

    parcel = binary_search(tracking_id)
    if parcel is None:
        print(f"\n  Parcel '{tracking_id.upper()}' not found.")
        return

    parcel.status = new_status
    parcel.history.append((new_status, datetime.now().strftime("%Y-%m-%d %H:%M")))
    print(f"\n  Status updated to '{new_status}'.")


# ========== TEST MENU ==========

if __name__ == "__main__":
    # Sample data
    for sender, receiver in [
        ("Alice Kamau", "Brian Odhiambo"),
        ("Carol Wanjiku", "David Mwangi"),
        ("Eve Adhiambo", "Frank Kipchoge"),
        ("Grace Nyambura", "Henry Otieno"),
    ]:
        register_parcel(sender, receiver)
    
    # Update some statuses
    update_status(parcel_database[1].tracking_id, "In Transit")
    update_status(parcel_database[2].tracking_id, "Delivered")

    print("\n=== PARCEL TRACKING ===")

    while True:
        print("\n1. Register Parcel")
        print("2. Track by ID")
        print("3. Search by Sender")
        print("4. Search by Receiver")
        print("5. Update Status")
        print("6. View All")
        print("7. Exit")
        choice = input("Choose (1-7): ").strip()

        if choice == "1":
            sender = input("Sender: ")
            receiver = input("Receiver: ")
            register_parcel(sender, receiver)

        elif choice == "2":
            tid = input("Tracking ID: ")
            track_parcel(tid)

        elif choice == "3":
            name = input("Sender Name: ")
            results = search_by_sender(name)
            print(f"\n  Found {len(results)} result(s).")
            for p in results:
                track_parcel(p.tracking_id)

        elif choice == "4":
            name = input("Receiver Name: ")
            results = search_by_receiver(name)
            print(f"\n  Found {len(results)} result(s).")
            for p in results:
                track_parcel(p.tracking_id)

        elif choice == "5":
            tid = input("Tracking ID: ")
            print(f"  Statuses: {', '.join(VALID_STATUSES)}")
            status = input("New Status: ")
            update_status(tid, status)

        elif choice == "6":
            print("\n--- All Parcels ---")
            if not parcel_database:
                print("No parcels.")
            else:
                for parcel in parcel_database:
                    print(parcel)

        elif choice == "7":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")