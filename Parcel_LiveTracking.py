"""
Parcel_LiveTracking.py
DSA Used:
  - Array/List    : parcel_database list stores all parcels
  - Linear Search : search by sender or receiver name
  - Binary Search : search by tracking ID (list sorted first)
"""

import random
from datetime import datetime


 
# PARCEL CLASS  (same as Registration.py)
 
class Parcel:
    def __init__(self, tracking_id, sender, receiver):
        self.tracking_id = tracking_id
        self.sender      = sender
        self.receiver    = receiver
        self.status      = "Registered"
        self.history     = [("Registered", datetime.now().strftime("%Y-%m-%d %H:%M"))]

    def __str__(self):
        return f"[{self.tracking_id}] From: {self.sender}  To: {self.receiver}  -  Status: {self.status}"


 
# Array / List  (DSA Requirement)
 
parcel_database = []

VALID_STATUSES = [
    "Registered", "Picked Up", "In Transit",
    "Out for Delivery", "Delivered", "Returned"
]


 
# GENERATE TRACKING ID  (same as Registration.py)
 
def generate_tracking_id():
    return f"KE-{random.randint(1000, 9999)}"


 
# REGISTER PARCEL  (same as Registration.py)
 
def register_parcel(sender, receiver):
    if not sender.strip() or not receiver.strip():
        print("\n  Error: Sender and receiver names cannot be empty!")
        return None

    tracking_id = generate_tracking_id()
    new_parcel  = Parcel(tracking_id, sender, receiver)
    parcel_database.append(new_parcel)
    print(f"\n  Registered: {new_parcel}")
    return new_parcel


 
# SORT the list by tracking ID
# (required before Binary Search can work)
 
def sort_by_id():
    parcel_database.sort(key=lambda p: p.tracking_id)


 
# BINARY SEARCH – by Tracking ID   O(log n)
 
def binary_search(tracking_id):
    sort_by_id()                      # list must be sorted first
    target = tracking_id.upper()
    low    = 0
    high   = len(parcel_database) - 1

    while low <= high:
        mid    = (low + high) // 2
        mid_id = parcel_database[mid].tracking_id

        if mid_id == target:
            return parcel_database[mid]   # found
        elif mid_id < target:
            low = mid + 1                 # search right half
        else:
            high = mid - 1               # search left half

    return None   # not found


 
# LINEAR SEARCH – by sender name   O(n)
 
def search_by_sender(name):
    results = []
    for parcel in parcel_database:             # check every parcel
        if name.lower() in parcel.sender.lower():
            results.append(parcel)
    return results


 
# LINEAR SEARCH – by receiver name   O(n)
 
def search_by_receiver(name):
    results = []
    for parcel in parcel_database:             # check every parcel
        if name.lower() in parcel.receiver.lower():
            results.append(parcel)
    return results


 
# TRACK – show full details for one parcel
 
def track_parcel(tracking_id):
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
        print(f"    {timestamp}  →  {status}")
    print("="*48)


 
# UPDATE STATUS
 
def update_status(tracking_id, new_status):
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


 
# INTERACTIVE MENU
 
if __name__ == "__main__":

    # sample data so the menu has something to work with
    for sender, receiver in [
        ("Alice Kamau",    "Brian Odhiambo"),
        ("Carol Wanjiku",  "David Mwangi"),
        ("Eve Adhiambo",   "Frank Kipchoge"),
        ("Grace Nyambura", "Henry Otieno"),
    ]:
        register_parcel(sender, receiver)
    update_status(parcel_database[1].tracking_id, "In Transit")
    update_status(parcel_database[2].tracking_id, "Delivered")

    print("\n=== PARCEL LIVE TRACKING SYSTEM ===")

    while True:
        print("\n1. Register a New Parcel")
        print("2. Track Parcel by ID")
        print("3. Search by Sender Name")
        print("4. Search by Receiver Name")
        print("5. Update Parcel Status")
        print("6. View All Parcels")
        print("7. Exit")
        choice = input("Select an option (1-7): ").strip()

        if choice == "1":
            sender_input   = input("Enter Sender Name   : ")
            receiver_input = input("Enter Receiver Name : ")
            register_parcel(sender_input, receiver_input)

        elif choice == "2":
            tid = input("Enter Tracking ID : ")
            track_parcel(tid)

        elif choice == "3":
            name    = input("Enter Sender Name : ")
            results = search_by_sender(name)
            print(f"\n  Found {len(results)} result(s).")
            for p in results:
                track_parcel(p.tracking_id)

        elif choice == "4":
            name    = input("Enter Receiver Name : ")
            results = search_by_receiver(name)
            print(f"\n  Found {len(results)} result(s).")
            for p in results:
                track_parcel(p.tracking_id)

        elif choice == "5":
            tid = input("Enter Tracking ID : ")
            print(f"  Statuses: {', '.join(VALID_STATUSES)}")
            new_status = input("New Status        : ")
            update_status(tid, new_status)

        elif choice == "6":
            print("\n--- Current Parcel Database ---")
            if not parcel_database:
                print("No parcels registered yet.")
            else:
                for parcel in parcel_database:
                    print(parcel)

        elif choice == "7":
            print("Exiting Tracking System. Goodbye!")
            break

        else:
            print("Invalid choice! Please select 1-7.")
