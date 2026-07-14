"""Parcel Cost Calculator Module - Calculates delivery costs"""
from typing import List, Tuple

class CostCalculation:
    """Represents a single cost calculation"""
    def __init__(self, tracking_id: str, weight: float, destination: str, cost: float):
        self.tracking_id = tracking_id
        self.weight = weight
        self.destination = destination
        self.cost = cost

class ParcelCostCalculator:
    """Manages cost calculations using Stack and Array/List
    
    Time Complexity:
    - calculate_cost: O(1)
    - get_calculation_history: O(n)
    - push_to_stack: O(1)
    - pop_from_stack: O(1)
    
    Space Complexity: O(n)
    """
    
    # Rate constants (Ksh per kg)
    BASE_RATE = 50  # Base rate per kg
    EXPRESS_MULTIPLIER = 1.5  # 50% premium for express
    
    # Destination surcharge (percentage)
    DESTINATION_SURCHARGE = {
        'Nakuru': 10,
        'Mombasa': 15,
        'Kisii': 12,
        'Nairobi': 0,  # No surcharge
        'Westlands': 5,
        'Kilimani': 5
    }
    
    def __init__(self):
        self.calculation_history: List[CostCalculation] = []  # Array/List
        self.calculation_stack = []  # Stack (LIFO)
    
    def push_to_stack(self, calculation: CostCalculation) -> None:
        """Push calculation to stack - O(1)"""
        self.calculation_stack.append(calculation)
    
    def pop_from_stack(self) -> CostCalculation or None:
        """Pop calculation from stack - O(1)"""
        if self.calculation_stack:
            return self.calculation_stack.pop()
        return None
    
    def peek_stack(self) -> CostCalculation or None:
        """Peek top of stack - O(1)"""
        if self.calculation_stack:
            return self.calculation_stack[-1]
        return None
    
    def calculate_cost(self, tracking_id: str, weight: float, 
                       destination: str, delivery_type: str = "normal") -> Tuple[float, dict]:
        """Calculate delivery cost - O(1)
        
        Args:
            tracking_id: Parcel tracking ID
            weight: Parcel weight in kg
            destination: Destination location
            delivery_type: 'normal' or 'express'
        
        Returns:
            Tuple of (total_cost, cost_breakdown)
        """
        # Base cost
        base_cost = weight * self.BASE_RATE
        
        # Apply delivery type multiplier
        if delivery_type.lower() == "express":
            base_cost *= self.EXPRESS_MULTIPLIER
        
        # Apply destination surcharge
        surcharge_percent = self.DESTINATION_SURCHARGE.get(destination, 20)
        surcharge = base_cost * (surcharge_percent / 100)
        
        # Total cost
        total_cost = base_cost + surcharge
        
        # Create calculation record
        calculation = CostCalculation(tracking_id, weight, destination, total_cost)
        
        # Store in history
        self.calculation_history.append(calculation)
        
        # Push to stack
        self.push_to_stack(calculation)
        
        # Return breakdown
        cost_breakdown = {
            'tracking_id': tracking_id,
            'weight': weight,
            'destination': destination,
            'delivery_type': delivery_type,
            'base_rate': self.BASE_RATE,
            'base_cost': round(base_cost, 2),
            'surcharge_percent': surcharge_percent,
            'surcharge': round(surcharge, 2),
            'total_cost': round(total_cost, 2)
        }
        
        return round(total_cost, 2), cost_breakdown
    
    def get_calculation_history(self) -> List[dict]:
        """Get calculation history - O(n)"""
        return [{
            'tracking_id': calc.tracking_id,
            'weight': calc.weight,
            'destination': calc.destination,
            'cost': calc.cost
        } for calc in self.calculation_history]
    
    def get_history_size(self) -> int:
        """Get history size - O(1)"""
        return len(self.calculation_history)
    
    def get_stack_size(self) -> int:
        """Get stack size - O(1)"""
        return len(self.calculation_stack)
    
    def get_average_cost(self) -> float:
        """Get average cost from history - O(n)"""
        if not self.calculation_history:
            return 0.0
        total = sum(calc.cost for calc in self.calculation_history)
        return round(total / len(self.calculation_history), 2)
    
    def get_total_cost(self) -> float:
        """Get total cost - O(n)"""
        return round(sum(calc.cost for calc in self.calculation_history), 2)
