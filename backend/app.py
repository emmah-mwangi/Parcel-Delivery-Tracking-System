from flask import Flask, jsonify, request, send_from_directory
import os
import json
import uuid
from datetime import datetime

# Try to import existing modules; if not present, use internal implementations
try:
    from Parcel_CostCalculator import CostCalculator
except Exception:
    CostCalculator = None

try:
    from Parcel_Reports import Reports
except Exception:
    Reports = None

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
PARCELS_FILE = os.path.join(DATA_DIR, 'parcels.json')
COST_HISTORY_FILE = os.path.join(DATA_DIR, 'cost_history.json')

os.makedirs(DATA_DIR, exist_ok=True)

app = Flask(__name__, static_folder='../frontend', static_url_path='/')

# Helpers to read/write JSON

def _read_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except Exception:
            return default


def _write_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)

# Basic in-repo cost calculator fallback
class _DefaultCostCalculator:
    def __init__(self):
        self.history = _read_json(COST_HISTORY_FILE, [])

    def calculate_cost(self, weight_kg, distance_km, speed='standard'):
        base = 50
        weight_factor = max(1, weight_kg / 5)
        distance_factor = 1 + (distance_km / 100)
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
        self.history.append(entry)
        _write_json(COST_HISTORY_FILE, self.history)
        return cost

# Default reports fallback
class _DefaultReports:
    def summary(self, parcels):
        total = len(parcels)
        statuses = {}
        weights = []
        for p in parcels:
            st = p.get('status', 'unknown')
            statuses[st] = statuses.get(st, 0) + 1
            try:
                weights.append(float(p.get('weight_kg', 0)))
            except Exception:
                pass
        avg_weight = round(sum(weights) / len(weights), 2) if weights else 0
        return {
            'total_parcels': total,
            'by_status': statuses,
            'average_weight_kg': avg_weight
        }

# Choose implementations (prefer imported ones)
Calc = CostCalculator() if CostCalculator else _DefaultCostCalculator()
Rpt = Reports() if Reports else _DefaultReports()

# Load parcels on startup
parcels_store = _read_json(PARCELS_FILE, [])

# Serve frontend
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/parcels', methods=['GET'])
def list_parcels():
    return jsonify(parcels_store)

@app.route('/api/parcels', methods=['POST'])
def create_parcel():
    data = request.json or {}
    tracking = data.get('tracking_number') or str(uuid.uuid4()).split('-')[0].upper()
    parcel = {
        'tracking_number': tracking,
        'sender_name': data.get('sender_name', ''),
        'receiver_name': data.get('receiver_name', ''),
        'destination': data.get('destination', ''),
        'origin': data.get('origin', ''),
        'weight_kg': data.get('weight_kg', 0),
        'status': data.get('status', 'registered'),
        'history': [
            {
                'status': data.get('status', 'registered'),
                'timestamp': datetime.utcnow().isoformat(),
                'location': data.get('origin', '')
            }
        ]
    }
    parcels_store.append(parcel)
    _write_json(PARCELS_FILE, parcels_store)
    return jsonify(parcel), 201

@app.route('/api/parcels/<tracking>', methods=['GET'])
def get_parcel(tracking):
    for p in parcels_store:
        if p.get('tracking_number') == tracking:
            return jsonify(p)
    return jsonify({'error': 'not found'}), 404

@app.route('/api/parcels/<tracking>/status', methods=['PUT'])
def update_status(tracking):
    body = request.json or {}
    new_status = body.get('status')
    location = body.get('location', '')
    if not new_status:
        return jsonify({'error': 'status required'}), 400
    for p in parcels_store:
        if p.get('tracking_number') == tracking:
            p['status'] = new_status
            entry = {'status': new_status, 'timestamp': datetime.utcnow().isoformat(), 'location': location}
            p.setdefault('history', []).append(entry)
            _write_json(PARCELS_FILE, parcels_store)
            return jsonify(p)
    return jsonify({'error': 'not found'}), 404

@app.route('/api/calculate_cost', methods=['POST'])
def calculate_cost():
    body = request.json or {}
    try:
        weight = float(body.get('weight_kg', 0))
        distance = float(body.get('distance_km', 0))
    except Exception:
        return jsonify({'error': 'invalid numeric values'}), 400
    speed = body.get('speed', 'standard')
    cost = None
    try:
        cost = Calc.calculate_cost(weight, distance, speed)
    except Exception:
        cost = _DefaultCostCalculator().calculate_cost(weight, distance, speed)
    return jsonify({'cost': cost})

@app.route('/api/reports', methods=['GET'])
def reports():
    try:
        summary = Rpt.summary(parcels_store)
    except Exception:
        summary = _DefaultReports().summary(parcels_store)
    return jsonify(summary)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
