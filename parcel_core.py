"""
PARCEL DELIVERY TRACKING SYSTEM - Core Module
==============================================

This module contains the main data structures used throughout the system.

DATA STRUCTURES USED:
1. Array (List) - parcel_database
   - Stores all parcel records in memory
   - Allows fast access by index O(1)
   - Used for searching and displaying parcels

2. Queue (deque) - delivery_queue
   - Follows FIFO (First In, First Out) principle
   - Processes parcels in the order they arrive
   - Ensures fair delivery processing
"""

from collections import deque
from datetime import datetime
import random


# Simple class to hold parcel information
class Parcel:
    def __init__(self, tracking_id, sender, receiver, destination="", weight=0.0, description=""):
        self.tracking_id = tracking_id      # Unique ID like KE-1234
        self.sender = sender.strip()        # Who sent it
        self.receiver = receiver.strip()    # Who receives it
        self.destination = destination      # Where it's going
        self.weight = float(weight)         # Weight in kg
        self.description = description      # Parcel contents/details
        self.status = "Registered"          # Current delivery status
        # History tracks all status changes (Stack-like behavior - newest on top)
        self.history = [("Registered", datetime.now().strftime("%Y-%m-%d %H:%M"))]

    def __str__(self):
        # Simple string representation for printing
        return f"[{self.tracking_id}] {self.sender} → {self.receiver} ({self.status})"


# ========== DATA STRUCTURES ==========

# Array/List: Stores all parcels - main database
parcel_database = []

# Queue: FIFO structure for processing deliveries in order
delivery_queue = deque()

# Delivery stages a parcel goes through
DELIVERY_STAGES = [
    "Registered",      # Just created
    "Picked Up",       # Collected from sender
    "In Transit",      # On the way
    "Out for Delivery", # Final delivery attempt
    "Delivered"        # Completed
]


# ========== HELPER FUNCTIONS ==========

def generate_tracking_id():
    """
    Generate a unique tracking ID.
    Format: KE-XXXX where X is a random 4-digit number
    Example: KE-1234, KE-5678
    """
    return f"KE-{random.randint(1000, 9999)}"


def ensure_parcel(parcel):
    """
    Add parcel to database if not already there.
    Prevents duplicate entries.
    """
    if parcel is None:
        return None
    if parcel not in parcel_database:
        parcel_database.append(parcel)
    return parcel


def enqueue_parcel(parcel):
    """
    Add parcel to delivery queue if not already queued.
    Uses Queue data structure (FIFO).
    """
    parcel = ensure_parcel(parcel)
    if parcel is not None and parcel not in delivery_queue:
        delivery_queue.append(parcel)
    return parcel


def clear_state():
    """Clear all data - useful for testing"""
    parcel_database.clear()
    delivery_queue.clear()