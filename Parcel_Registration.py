"""
1. Parcel_Registration.py
Responsibilities
Register new parcels
Collect sender and receiver details
Generate unique tracking IDs
Validate user input
Store parcel records
DSA to Use
Array/List (store all parcel records)
Linked List (optional implementation for parcel insertion)

"""

class Parcel:
    def __init__(self, tracking_id, sender, receiver):
        self.tracking_id = tracking_id
        self.sender = sender
        self.receiver = receiver
        self.status = "Registered"  # Default status when first created

    def __str__(self):
        # This makes it print nicely later!
        return f"[{self.tracking_id}] From: {self.sender} To: {self.receiver} - Status: {self.status}"

# Our main Array/List to store all registered parcels
parcel_database = []