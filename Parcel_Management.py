"""
PARCEL MANAGEMENT MODULE
========================

This module handles parcel delivery processing and status updates.

DATA STRUCTURES USED:
1. Queue (delivery_queue) - FIFO processing
   - Parcels processed in arrival order
   - First parcel added is first to be delivered
   - Uses deque for efficient O(1) operations

2. Array/List (parcel_database) - storage
   - All parcels stored here
   - Used for searching and updates

KEY ALGORITHMS:
- Linear Search: O(n) - find parcel by tracking ID
- Queue operations: O(1) - add/remove from queue
"""

from datetime import datetime
from parcel_core import Parcel, parcel_database, delivery_queue, DELIVERY_STAGES, ensure_parcel, enqueue_parcel


# ========== SEARCHING ==========

def find_parcel(tracking_id):
    """
    Find a parcel by tracking ID using LINEAR SEARCH.
    
    Algorithm: Linear Search
    - Check each parcel one by one
    - Stop when found
    - Time: O(n) - may check all parcels
    - Space: O(1) - no extra storage
    
    Args:
        tracking_id: The ID to search for (e.g., "KE-1234")
    
    Returns:
        Parcel object if found, None otherwise
    """
    for parcel in parcel_database:
        if parcel.tracking_id == tracking_id.upper():
            return parcel
    return None


# ========== QUEUE OPERATIONS ==========

def add_to_queue(tracking_id):
    """
    Add a parcel to the delivery queue.
    
    Queue behavior: FIFO (First In, First Out)
    - First parcel added will be processed first
    - Like a real queue at a store
    """
    parcel = find_parcel(tracking_id)

    if parcel is None:
        print(f"\n  Error: No parcel found with ID '{tracking_id.upper()}'.")
        return

    if parcel in delivery_queue:
        print(f"\n  '{parcel.tracking_id}' is already in queue.")
        return

    enqueue_parcel(parcel)
    print(f"\n  Added to queue: {parcel}")
    print(f"  Queue size: {len(delivery_queue)} parcel(s)")


def process_next():
    """
    Process the next parcel in the delivery queue.
    
    Steps:
    1. Take first parcel from queue (popleft)
    2. Move to next delivery stage
    3. If not delivered, add back to queue
    4. If delivered, remove from queue completely
    """
    if not delivery_queue:
        print("\n  Queue is empty. No parcels to process.")
        return

    # Get first parcel (FIFO - first in, first out)
    parcel = delivery_queue.popleft()
    
    # Find current stage index
    current_index = DELIVERY_STAGES.index(parcel.status)

    # Check if already delivered
    if current_index >= len(DELIVERY_STAGES) - 1:
        print(f"\n  '{parcel.tracking_id}' is already Delivered.")
        return

    # Move to next stage
    next_stage = DELIVERY_STAGES[current_index + 1]
    parcel.status = next_stage
    
    # Add to history (Stack-like - newest on top)
    parcel.history.append((next_stage, datetime.now().strftime("%Y-%m-%d %H:%M")))

    print(f"\n  Processed: {parcel.tracking_id}")
    print(f"  New Status: {parcel.status}")

    # If not delivered, add back to queue for next stage
    if parcel.status != "Delivered":
        enqueue_parcel(parcel)
        print("  Re-queued for next stage.")
    else:
        print(f"  Delivered to {parcel.receiver}. Removed from queue.")


def update_status(tracking_id, new_status):
    """
    Manually update parcel status.
    
    Args:
        tracking_id: Parcel ID to update
        new_status: New status from DELIVERY_STAGES list
    """
    if new_status not in DELIVERY_STAGES:
        print(f"\n  Invalid status. Choose from: {', '.join(DELIVERY_STAGES)}")
        return

    parcel = find_parcel(tracking_id)

    if parcel is None:
        print(f"\n  No parcel found with ID '{tracking_id.upper()}'.")
        return

    # Update status
    parcel.status = new_status
    
    # Add to history
    parcel.history.append((new_status, datetime.now().strftime("%Y-%m-%d %H:%M")))

    # If delivered, remove from queue
    if new_status == "Delivered" and parcel in delivery_queue:
        delivery_queue.remove(parcel)
        print(f"\n  Status updated to '{new_status}'. Removed from queue.")
    else:
        print(f"\n  Status updated to '{new_status}'.")


def mark_delivered(tracking_id):
    """Quick way to mark a parcel as delivered"""
    update_status(tracking_id, "Delivered")


# ========== VIEW FUNCTIONS ==========

def view_queue():
    """Show current delivery queue (FIFO order)"""
    print("\n--- Delivery Queue (FIFO Order) ---")

    if not delivery_queue:
        print("  Queue is empty.")
        return

    print(f"  {len(delivery_queue)} parcel(s) in queue:\n")
    for position, parcel in enumerate(delivery_queue, start=1):
        label = "  <- NEXT" if position == 1 else ""
        print(f"  #{position}{label}")
        print(f"    Tracking: {parcel.tracking_id}")
        print(f"    From: {parcel.sender} → {parcel.receiver}")
        print(f"    Status: {parcel.status}")
        print()


def view_all_parcels():
    """Show all parcels in database with their history"""
    print("\n--- All Parcels ---")

    if not parcel_database:
        print("  No parcels registered yet.")
        return

    for parcel in parcel_database:
        print(f"\n  {parcel}")
        print(f"  History:")
        for status, timestamp in parcel.history:
            print(f"    {timestamp} → {status}")

    # Summary
    total = len(parcel_database)
    in_queue = len(delivery_queue)
    delivered = sum(1 for p in parcel_database if p.status == 'Delivered')
    
    print(f"\n  Total: {total} | In Queue: {in_queue} | Delivered: {delivered}")


# ========== TEST MENU ==========

if __name__ == "__main__":
    # Add some sample data
    from Parcel_Registration import register_parcel

    sample = [
        ("Alice Kamau", "Brian Odhiambo"),
        ("Carol Wanjiku", "David Mwangi"),
        ("Eve Adhiambo", "Frank Kipchoge"),
    ]
    for sender, receiver in sample:
        p = register_parcel(sender, receiver)
        if p:
            add_to_queue(p.tracking_id)

    print("\n=== PARCEL MANAGEMENT ===")

    while True:
        print("\n1. Add to Queue")
        print("2. Process Next Delivery")
        print("3. Update Status")
        print("4. Mark Delivered")
        print("5. View Queue")
        print("6. View All Parcels")
        print("7. Exit")
        choice = input("Choose (1-7): ").strip()

        if choice == "1":
            tid = input("Tracking ID: ").strip()
            add_to_queue(tid)

        elif choice == "2":
            process_next()

        elif choice == "3":
            tid = input("Tracking ID: ").strip()
            print(f"  Stages: {', '.join(DELIVERY_STAGES)}")
            status = input("New Status: ").strip()
            update_status(tid, status)

        elif choice == "4":
            tid = input("Tracking ID: ").strip()
            mark_delivered(tid)

        elif choice == "5":
            view_queue()

        elif choice == "6":
            view_all_parcels()

        elif choice == "7":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")