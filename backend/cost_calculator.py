"""
COST CALCULATOR MODULE
========================
Turns weight, road distance (from Dijkstra), delivery speed, and
fragility into a KSh price, and keeps a history of every quote.

Pricing formula
----------------
    cost = BASE_FEE
         + weight_kg   x WEIGHT_RATE_PER_KG
         + distance_km x DISTANCE_RATE_PER_KM
         + speed_surcharge (0 / EXPRESS / OVERNIGHT)
         + (FRAGILE_SURCHARGE if is_fragile else 0)

History is kept two ways on purpose, to demonstrate both structures:
  - self.history (array)  -> chronological order, used for reports
  - self.stack   (Stack)  -> LIFO, so the last quote can be undone
"""

from datetime import datetime
from backend.data_structures import StatusStack

BASE_FEE = 250
WEIGHT_RATE_PER_KG = 40
DISTANCE_RATE_PER_KM = 5
EXPRESS_SURCHARGE = 300
OVERNIGHT_SURCHARGE = 600
FRAGILE_SURCHARGE = 150


class CostCalculator:
    def __init__(self):
        self.history = []            # array - chronological log
        self.stack = StatusStack()   # LIFO - supports undo_last()

    def calculate_cost(self, weight_kg, distance_km, delivery_type='standard', is_fragile=False):
        weight_kg = float(weight_kg)
        distance_km = float(distance_km)

        speed_surcharge = 0
        if delivery_type == 'express':
            speed_surcharge = EXPRESS_SURCHARGE
        elif delivery_type == 'overnight':
            speed_surcharge = OVERNIGHT_SURCHARGE

        fragile_surcharge = FRAGILE_SURCHARGE if is_fragile else 0

        weight_charge = round(weight_kg * WEIGHT_RATE_PER_KG, 2)
        distance_charge = round(distance_km * DISTANCE_RATE_PER_KM, 2)

        total = round(BASE_FEE + weight_charge + distance_charge + speed_surcharge + fragile_surcharge, 2)

        breakdown = {
            'base_fee': BASE_FEE,
            'weight_charge': weight_charge,
            'distance_charge': distance_charge,
            'speed_surcharge': speed_surcharge,
            'fragile_surcharge': fragile_surcharge,
            'total': total
        }

        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'weight_kg': weight_kg,
            'distance_km': distance_km,
            'delivery_type': delivery_type,
            'is_fragile': is_fragile,
            'cost': total
        }
        self.history.append(entry)   # array semantics: append to end
        self.stack.push(entry)       # stack semantics: push onto top

        return breakdown

    def undo_last(self):
        """Pop the most recent quote off the stack (does not touch history)."""
        return self.stack.pop()

    def get_history(self):
        return list(self.history)
