"""
2. Parcel_CostCalculator.py
Responsibilities
Calculate delivery cost based on weight
Calculate charges based on destination
Apply express/normal delivery rates
Maintain calculation history
Display cost breakdown
DSA to Use
Stack (store cost calculation history)
Array/List (store previous calculations)
"""

from datetime import datetime

# COST RATES (in KES - Kenyan Shillings)
DELIVERY_RATES = {
    "Standard": {"base": 500, "per_kg": 50},
    "Express": {"base": 1000, "per_kg": 100}
}

DESTINATION_MULTIPLIERS = {
    "Nairobi": 1.0,
    "Mombasa": 1.2,
    "Kisumu": 1.3,
    "Nakuru": 1.1,
    "Kigali": 1.5,
    "Uganda": 1.4,
    "Other": 1.6
}

# Stack (LIFO) - store cost calculation history
class Stack:
    def __init__(self):
        self.items = []
    
    def push(self, item):
        """Add item to top of stack O(1)"""
        self.items.append(item)
    
    def pop(self):
        """Remove and return item from top O(1)"""
        if not self.is_empty():
            return self.items.pop()
        return None
    
    def peek(self):
        """View top item without removing"""
        if not self.is_empty():
            return self.items[-1]
        return None
    
    def is_empty(self):
        return len(self.items) == 0
    
    def size(self):
        return len(self.items)

# Global structures
calculation_history = Stack()  # LIFO - most recent calculations on top
all_calculations = []  # Array/List - for reports

class CostCalculation:
    def __init__(self, weight, destination, delivery_type, tracking_id=None):
        self.weight = weight
        self.destination = destination
        self.delivery_type = delivery_type
        self.tracking_id = tracking_id
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.total_cost = 0
        self.breakdown = {}
    
    def calculate(self):
        """Calculate total delivery cost with breakdown"""
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
    Calculate delivery cost and store in history
    Time Complexity: O(1)
    Space Complexity: O(1)
    """
    calculation = CostCalculation(weight, destination, delivery_type, tracking_id)
    
    if calculation.calculate():
        # Push to stack (LIFO)
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
    """Get cost data for API"""
    return {
        "calculations": len(all_calculations),
        "rates": DELIVERY_RATES,
        "destinations": list(DESTINATION_MULTIPLIERS.keys())
    }
