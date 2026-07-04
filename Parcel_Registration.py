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
import random

class Parcel:
    def __init__(self, tracking_id, sender, receiver):
        self.tracking_id = tracking_id
        self.sender = sender
        self.receiver = receiver
        self.status = "Registered"  # Default status when first created

    def __str__(self):
        return f"[{self.tracking_id}] From: {self.sender} To: {self.receiver} - Status: {self.status}"

# Our main Array/List to store all registered parcels (DSA Requirement!)
parcel_database = []

def generate_tracking_id():
    """Generates a random 4-digit ID with a prefix, e.g., KE-4928"""
    random_number = random.randint(1000, 9999)
    return f"KE-{random_number}"

def register_parcel(sender, receiver):
    """Validates input, creates a parcel, and saves it to the database list."""
    # Input Validation
    if not sender.strip() or not receiver.strip():
        print("\n❌ Error: Sender and receiver names cannot be empty!")
        return None
    
    tracking_id = generate_tracking_id()
    new_parcel = Parcel(tracking_id, sender, receiver)
    
    # Store in our list data structure
    parcel_database.append(new_parcel)
    
    print(f"\n✅ Success! Registered: {new_parcel}")
    return new_parcel

# --- Interactive Menu ---
if __name__ == "__main__":
    print("=== WELCOME TO THE PARCEL REGISTRATION SYSTEM ===")
    
    while True:
        print("\n1. Register a New Parcel")
        print("2. View All Registered Parcels")
        print("3. Exit")
        choice = input("Select an option (1-3): ").strip()
        
        if choice == "1":
            sender_input = input("Enter Sender Name: ")
            receiver_input = input("Enter Receiver Name: ")
            register_parcel(sender_input, receiver_input)
            
        elif choice == "2":
            print("\n--- Current Parcel Database ---")
            if not parcel_database:
                print("No parcels registered yet.")
            else:
                for parcel in parcel_database:
                    print(parcel)
                    
        elif choice == "3":
            print("Exiting Registration System. Goodbye!")
            break
        else:
            print("Invalid choice! Please select 1, 2, or 3.")