""" 
4. Parcel_Management.py
Responsibilities
Update parcel status
Move parcels through delivery stages
Process deliveries in order
Mark parcels as delivered
Remove completed deliveries from queue
DSA to Use
Queue (FIFO delivery process)
Array/List 

"""

"""
Parcel_Management.py
DSA Used:
  - Queue (deque) : FIFO delivery pipeline: processes parcels in arrival order
  - Array/List    : parcel_database stores all parcel objects (to be shared with other modules)
"""


from collections import deque
from datetime import datetime


class Parcel:
    def __init__(self, tracking_id, sender, receiver):
        self.tracking_id = tracking_id
        self.sender      = sender
        self.receiver    = receiver
        self.status      = "Registered"
        self.history     = [("Registered", datetime.now().strftime("%Y-%m-%d %H:%M"))]

    def __str__(self):
        return f"[{self.tracking_id}] From: {self.sender}  To: {self.receiver}  -  Status: {self.status}"



# DATA STRUCTURES

parcel_database = []     # Array/List- master record of all parcels

delivery_queue  = deque()  # Queue (deque)- FIFO delivery pipeline

# Delivery stages every parcel passes through in order
DELIVERY_STAGES = [
    "Registered",
    "Picked Up",
    "In Transit",
    "Out for Delivery",
    "Delivered"
]

# HELPER: find a parcel by tracking ID (Linear Search O(n))

def find_parcel(tracking_id):
    """
    Linear Search through parcel_database.
    Time Complexity  : O(n)
    Space Complexity : O(1)
    """
    for parcel in parcel_database:
        if parcel.tracking_id == tracking_id.upper():
            return parcel
    return None

# 1: Add parcel to the delivery queue

def add_to_queue(tracking_id):
   
    parcel = find_parcel(tracking_id)

    if parcel is None:
        print(f"\n  Error: No parcel found with ID '{tracking_id.upper()}'.")
        return

    # Check it isn't already in the queue
    if parcel in delivery_queue:
        print(f"\n  '{parcel.tracking_id}' is already in the delivery queue.")
        return

    delivery_queue.append(parcel)    # ENQUEUE: add to back of queue O(1)
    print(f"\n  Added to queue: {parcel}")
    print(f"  Queue size    : {len(delivery_queue)} parcel(s)")

# 2: Process the next parcel in queue

def process_next():
    
    if not delivery_queue:
        print("\n  Queue is empty. No parcels to process.")
        return

    parcel = delivery_queue.popleft()    

    current_index = DELIVERY_STAGES.index(parcel.status)

    # Already at final stage
    if current_index >= len(DELIVERY_STAGES) - 1:
        print(f"\n  '{parcel.tracking_id}' is already Delivered.")
        return

    # Advance one stage
    next_stage     = DELIVERY_STAGES[current_index + 1]
    parcel.status  = next_stage
    parcel.history.append((next_stage, datetime.now().strftime("%Y-%m-%d %H:%M")))

    print(f"\n  Processed : {parcel.tracking_id}")
    print(f"  New Status: {parcel.status}")

    # If not yet delivered, re-enqueue for the next stage
    if parcel.status != "Delivered":
        delivery_queue.append(parcel)    
        print(f"  Re-queued for next stage.")
    else:
        print(f"  Parcel delivered to {parcel.receiver}. Removed from queue.")


# 3: Update parcel status manually

def update_status(tracking_id, new_status):
   
    if new_status not in DELIVERY_STAGES:
        print(f"\n  Invalid status. Choose from: {', '.join(DELIVERY_STAGES)}")
        return

    parcel = find_parcel(tracking_id)

    if parcel is None:
        print(f"\n  No parcel found with ID '{tracking_id.upper()}'.")
        return

    parcel.status = new_status
    parcel.history.append((new_status, datetime.now().strftime("%Y-%m-%d %H:%M")))

    # If manually marked Delivered, remove from active queue
    if new_status == "Delivered" and parcel in delivery_queue:
        delivery_queue.remove(parcel)
        print(f"\n  Status updated to '{new_status}'. Removed from queue.")
    else:
        print(f"\n  Status updated to '{new_status}'.")


# 4: Mark parcel as delivered directly

def mark_delivered(tracking_id):
   update_status(tracking_id, "Delivered")



# 5: View current delivery queue


def view_queue():
    
    print("\n--- Current Delivery Queue (FIFO Order) ---")

    if not delivery_queue:
        print("  Queue is empty.")
        return

    print(f"  {len(delivery_queue)} parcel(s) in queue:\n")
    for position, parcel in enumerate(delivery_queue, start=1):
        label = "  <- NEXT" if position == 1 else ""
        print(f"  #{position}{label}")
        print(f"    Tracking : {parcel.tracking_id}")
        print(f"    From     : {parcel.sender}  ->  {parcel.receiver}")
        print(f"    Status   : {parcel.status}")
        print()


# 6: View all parcels in the database


def view_all_parcels():
   
    print("\n--- All Parcels in System ---")

    if not parcel_database:
        print("  No parcels registered yet.")
        return

    for parcel in parcel_database:
        print(f"\n  {parcel}")
        print(f"  History:")
        for status, timestamp in parcel.history:
            print(f"    {timestamp}  ->  {status}")

    print(f"\n  Total: {len(parcel_database)} parcel(s) | "
          f"In queue: {len(delivery_queue)} | "
          f"Delivered: {sum(1 for p in parcel_database if p.status == 'Delivered')}")


# INTERACTIVE MENU(Sample)

if __name__ == "__main__":

    # Sample data so the menu has something to work with
    from Parcel_Registration import register_parcel, parcel_database as reg_db

    sample = [
        ("Alice Kamau",    "Brian Odhiambo"),
        ("Carol Wanjiku",  "David Mwangi"),
        ("Eve Adhiambo",   "Frank Kipchoge"),
    ]
    for sender, receiver in sample:
        p = register_parcel(sender, receiver)
        if p:
            parcel_database.append(p)
            delivery_queue.append(p)

    print("\n=== PARCEL MANAGEMENT SYSTEM ===")

    while True:
        print("\n1. Add Parcel to Queue")
        print("2. Process Next Delivery")
        print("3. Update Parcel Status")
        print("4. Mark Parcel as Delivered")
        print("5. View Delivery Queue")
        print("6. View All Parcels")
        print("7. Exit")
        choice = input("Select an option (1-7): ").strip()

        if choice == "1":
            tid = input("Enter Tracking ID to queue: ").strip()
            add_to_queue(tid)

        elif choice == "2":
            process_next()

        elif choice == "3":
            tid = input("Enter Tracking ID    : ").strip()
            print(f"  Stages: {', '.join(DELIVERY_STAGES)}")
            new_status = input("Enter New Status     : ").strip()
            update_status(tid, new_status)

        elif choice == "4":
            tid = input("Enter Tracking ID: ").strip()
            mark_delivered(tid)

        elif choice == "5":
            view_queue()

        elif choice == "6":
            view_all_parcels()

        elif choice == "7":
            print("Exiting Management System. Goodbye!")
            break

        else:
            print("Invalid choice! Please select 1-7.")
