"""
PARCEL COST CALCULATOR MODULE
==============================

This module calculates delivery costs based on weight, destination, and type.

DATA STRUCTURES USED:
1. Stack (calculation_history)
   - Stores cost calculations in LIFO order
   - Most recent calculation on top
   - Used to show calculation history

2. Array/List (all_calculations)
   - Stores all calculations for reports
   - Keeps complete history

ALGORITHMS:
- Stack operations: O(1) - push/pop from top
"""

from datetime import datetime

# Delivery rates in KES (Kenyan Shillings)
DELIVERY_RATES = {
    "Standard": {"base": 500, "per_kg": 50},
    "Express": {"base": 1000, "per_kg": 100}
}

# Destination price multipliers
DESTINATION_MULTIPLIERS = {
    "Nairobi": 1.0,
    "Mombasa": 1.2,
    "Kisumu": 1.3,
    "Nakuru": 1.1,
    "Kigali": 1.5,
    "Uganda": 1.4,
    "Other": 1.6
}


# ========== STACK DATA STRUCTURE ==========

class Stack:
    """
    Stack (LIFO - Last In, First Out)
    
    Like a stack of plates - last one added is first to be removed.
    
    Operations:
    - push(item): Add to top - O(1)
    - pop(): Remove from top - O(1)
    - peek(): View top without removing - O(1)
    """
    def __init__(self):
        self.items = []
    
    def push(self, item):
        """Add item to top of stack"""
        self.items.append(item)
    
    def pop(self):
        """Remove and return top item"""
        if not self.is_empty():
            return self.items.pop()
        return None
    
    def peek(self):
        """View top item without removing"""
        if not self.is_empty():
            return self.items[-1]
        return None
    
    def is_empty(self):
        """Check if stack is empty"""
        return len(self.items) == 0
    
    def size(self):
        """Get number of items in stack"""
        return len(self.items)


# Global data structures
calculation_history = Stack()  # Stack - most recent on top
all_calculations = []  # Array - for reports


# ========== COST CALCULATION ==========

class CostCalculation:
    """Holds cost calculation details"""
    def __init__(self, weight, destination, delivery_type, tracking_id=None):
        self.weight = weight
        self.destination = destination
        self.delivery_type = delivery_type
        self.tracking_id = tracking_id
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.total_cost = 0
        self.breakdown = {}
    
    def calculate(self):
        """
        Calculate total delivery cost.
        
        Formula:
        base_cost + (weight × per_kg) = subtotal
        subtotal × destination_multiplier = with_destination
        with_destination + (with_destination × 0.16) = total (with 16% VAT)
        """
        try:
            # Get base rate
            if self.delivery_type not in DELIVERY_RATES:
                raise ValueError(f"Invalid delivery type: {self.delivery_type}")
            
            rates = DELIVERY_RATES[self.delivery_type]
            base_cost = rates["base"]
            weight_cost = rates["per_kg"] * self.weight
            
            # Get destination multiplier
            multiplier = DESTINATION_MULTIPLIERS.get(self.destination, DESTINATION_MULTIPLIERS["Other"])
            
            # Calculate total
            subtotal = base_cost + weight_cost
            total_with_destination = subtotal * multiplier
            tax = total_with_destination * 0.16  # 16% VAT
            self.total_cost = total_with_destination + tax
            
            # Store breakdown
            self.breakdown = {
                "base_cost": base_cost,
                "weight_cost": weight_cost,
                "subtotal": subtotal,
                "destination_multiplier": multiplier,
                "subtotal_with_destination": total_with_destination,
                "tax_16_percent": tax,
                "total": self.total_cost
            }
            
            return True
        except Exception as e:
            print(f"  Error calculating cost: {e}")
            return False
    
    def __str__(self):
        return f"[{self.tracking_id or 'NEW'}] {self.weight}kg to {self.destination} ({self.delivery_type}): KES {self.total_cost:.2f}"


def calculate_cost(weight, destination, delivery_type, tracking_id=None):
    """
    Calculate delivery cost and store in history.
    
    Steps:
    1. Create CostCalculation object
    2. Calculate total cost
    3. Push to stack (LIFO)
    4. Add to array for reports
    
    Returns:
        CostCalculation object if successful, None otherwise
    """
    calculation = CostCalculation(weight, destination, delivery_type, tracking_id)
    
    if calculation.calculate():
        # Push to stack (LIFO) - newest on top
        calculation_history.push(calculation)
        # Also add to array for reports
        all_calculations.append(calculation)
        return calculation
    return None


def display_cost_breakdown(calculation):
    """Display detailed cost breakdown"""
    print("\n" + "="*50)
    print(f"  COST CALCULATION BREAKDOWN")
    print("="*50)
    print(f"  Tracking ID    : {calculation.tracking_id or 'N/A'}")
    print(f"  Weight         : {calculation.weight} kg")
    print(f"  Destination    : {calculation.destination}")
    print(f"  Delivery Type  : {calculation.delivery_type}")
    print(f"  Timestamp      : {calculation.timestamp}")
    print("\n  --- Cost Breakdown ---")
    print(f"  Base Cost              : KES {calculation.breakdown['base_cost']:.2f}")
    print(f"  Weight Cost (per kg)   : KES {calculation.breakdown['weight_cost']:.2f}")
    print(f"  Subtotal               : KES {calculation.breakdown['subtotal']:.2f}")
    print(f"  Destination Multiplier : {calculation.breakdown['destination_multiplier']}x")
    print(f"  After Multiplier       : KES {calculation.breakdown['subtotal_with_destination']:.2f}")
    print(f"  Tax (16% VAT)          : KES {calculation.breakdown['tax_16_percent']:.2f}")
    print("-"*50)
    print(f"  TOTAL COST             : KES {calculation.breakdown['total']:.2f}")
    print("="*50)


def get_cost_data():
    """Get cost data for API/reports"""
    return {
        "calculations": len(all_calculations),
        "rates": DELIVERY_RATES,
        "destinations": list(DESTINATION_MULTIPLIERS.keys())
    }


# ========== TEST MENU ==========

if __name__ == "__main__":
    print("\n=== COST CALCULATOR ===")
    
    while True:
        print("\n1. Calculate Cost")
        print("2. View History (Stack - newest first)")
        print("3. View All Calculations")
        print("4. Exit")
        choice = input("Choose (1-4): ").strip()
        
        if choice == "1":
            try:
                weight = float(input("Weight (kg): "))
                print("Destinations:", ", ".join(DESTINATION_MULTIPLIERS.keys()))
                destination = input("Destination: ")
                print("Types: Standard, Express")
                delivery_type = input("Delivery Type: ")
                
                calc = calculate_cost(weight, destination, delivery_type)
                if calc:
                    display_cost_breakdown(calc)
            except ValueError:
                print("Invalid weight!")
        
        elif choice == "2":
            print("\n--- Recent Calculations (Stack - LIFO) ---")
            if calculation_history.is_empty():
                print("No calculations yet.")
            else:
                # Show from top of stack (most recent first)
                print(f"  Stack size: {calculation_history.size()}")
                temp_stack = Stack()
                while not calculation_history.is_empty():
                    item = calculation_history.pop()
                    print(f"  {item}")
                    temp_stack.push(item)
                # Restore stack
                while not temp_stack.is_empty():
                    calculation_history.push(temp_stack.pop())
        
        elif choice == "3":
            print(f"\n--- All Calculations ({len(all_calculations)}) ---")
            for calc in all_calculations:
                print(f"  {calc}")
        
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")