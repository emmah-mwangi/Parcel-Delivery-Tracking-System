# Parcel Cost Calculator
# Implements a simple cost calculator and keeps history using a stack and array semantics.
import os
import json
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
COST_HISTORY_FILE = os.path.join(DATA_DIR, 'cost_history.json')

os.makedirs(DATA_DIR, exist_ok=True)

class CostCalculator:
    def __init__(self):
        # history as array
        self.history = self._load_history()
        # stack implemented as list for LIFO operations
        self.stack = list(self.history)

    def _load_history(self):
        if not os.path.exists(COST_HISTORY_FILE):
            return []
        try:
            with open(COST_HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    def _save_history(self):
        with open(COST_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2)

    def calculate_cost(self, weight_kg, distance_km, speed='standard'):
        base = 50
        weight_factor = max(1, float(weight_kg) / 5)
        distance_factor = 1 + (float(distance_km) / 100)
        speed_multiplier = 1.0
        if speed == 'express':
            speed_multiplier = 1.5
        elif speed == 'overnight':
            speed_multiplier = 2.0
        cost = round(base * weight_factor * distance_factor * speed_multiplier, 2)
        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'weight_kg': weight_kg,
            'distance_km': distance_km,
            'speed': speed,
            'cost': cost
        }
        # array semantics: append to end
        self.history.append(entry)
        # stack semantics: push onto top
        self.stack.append(entry)
        self._save_history()
        return cost

    def pop_latest(self):
        # remove last entry (stack pop)
        if not self.stack:
            return None
        entry = self.stack.pop()
        # also remove from history if it matches last
        if self.history and self.history[-1] == entry:
            self.history.pop()
            self._save_history()
        return entry

    def get_history(self):
        return list(self.history)

if __name__ == '__main__':
    c = CostCalculator()
    print('Test cost:', c.calculate_cost(10, 120, 'express'))
