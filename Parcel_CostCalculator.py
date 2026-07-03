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


def view_calculation_history():
    """View all calculations using Stack (LIFO order)"""
    print("\n--- Cost Calculation History (Most Recent First) ---")
    
    if calculation_history.is_empty():
        print("  No calculations yet.")
        return
    
    temp_stack = Stack()
    count = 1
    
    # Display and restore stack
    while not calculation_history.is_empty():
        calc = calculation_history.pop()
        print(f"\n  {count}. {calc}")
        display_cost_breakdown(calc)
        temp_stack.push(calc)
        count += 1
    
    # Restore original stack
    while not temp_stack.is_empty():
        calculation_history.push(temp_stack.pop())


def get_average_cost():
    """Calculate average delivery cost from all calculations"""
    if not all_calculations:
        return 0
    
    total = sum(calc.total_cost for calc in all_calculations)
    return total / len(all_calculations)


def get_cost_statistics():
    """Get detailed statistics about calculations"""
    if not all_calculations:
        print("\n  No calculations to analyze.")
        return
    
    costs = [calc.total_cost for calc in all_calculations]
    destinations = [calc.destination for calc in all_calculations]
    
    print("\n--- Cost Statistics ---")
    print(f"  Total Calculations  : {len(all_calculations)}")
    print(f"  Minimum Cost        : KES {min(costs):.2f}")
    print(f"  Maximum Cost        : KES {max(costs):.2f}")
    print(f"  Average Cost        : KES {get_average_cost():.2f}")
    print(f"  Total Revenue       : KES {sum(costs):.2f}")
    
    # Destination frequency
    print(f"\n  --- Destinations ---")
    for dest in set(destinations):
        count = destinations.count(dest)
        avg = sum(c.total_cost for c in all_calculations if c.destination == dest) / count
        print(f"    {dest}: {count} deliveries, Avg: KES {avg:.2f}")


# INTERACTIVE MENU
if __name__ == "__main__":
    
    print("\n=== PARCEL COST CALCULATOR SYSTEM ===")
    
    while True:
        print("\n1. Calculate Delivery Cost")
        print("2. View Calculation History (Stack - LIFO)")
        print("3. View Cost Statistics")
        print("4. Get Latest Calculation (Peek)")
        print("5. Exit")
        choice = input("Select an option (1-5): ").strip()
        
        if choice == "1":
            try:
                weight = float(input("  Enter parcel weight (kg)    : "))
                tracking_id = input("  Enter tracking ID (optional): ").strip()
                
                print(f"\n  Available destinations: {', '.join(DESTINATION_MULTIPLIERS.keys())}")
                destination = input("  Enter destination          : ").strip()
                
                if destination not in DESTINATION_MULTIPLIERS:
                    destination = "Other"
                    print(f"  Destination not found. Using 'Other' with 1.6x multiplier.")
                
                print(f"\n  Available types: {', '.join(DELIVERY_RATES.keys())}")
                delivery_type = input("  Enter delivery type         : ").strip()
                
                if delivery_type not in DELIVERY_RATES:
                    print("  Invalid delivery type!")
                    continue
                
                calc = calculate_cost(weight, destination, delivery_type, tracking_id or None)
                if calc:
                    display_cost_breakdown(calc)
            except ValueError:
                print("  Error: Please enter valid numbers for weight.")
        
        elif choice == "2":
            view_calculation_history()
        
        elif choice == "3":
            get_cost_statistics()
        
        elif choice == "4":
            latest = calculation_history.peek()
            if latest:
                print(f"\n  Latest Calculation: {latest}")
                display_cost_breakdown(latest)
            else:
                print("\n  No calculations in history.")
        
        elif choice == "5":
            print("Exiting Cost Calculator. Goodbye!")
            break
        
        else:
            print("Invalid choice! Please select 1-5.")
