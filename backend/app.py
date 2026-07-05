import os
import json
import uuid
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# Initialize Flask with the correct frontend static path directory
app = Flask(__name__, static_folder='../frontend', static_url_path='/')
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# Try to import existing data modules securely
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

# ==========================================
# FILE READ/WRITE UTILITY HELPERS
# ==========================================
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

# Fallback classes if custom data structural files are absent
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

Calc = CostCalculator() if CostCalculator else _DefaultCostCalculator()
Rpt = Reports() if Reports else _DefaultReports()

# Initial state data ingestion
parcels_store = _read_json(PARCELS_FILE, [])

# ==========================================
# ROUTE ENDPOINTS DEFINITIONS
# ==========================================
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# Unified API Registration Interface matching frontend app.js perfectly
@app.route('/api/register', methods=['POST'])
def register_parcel():
    data = request.json or {}
    
    # Simple explicit key presence validation match check
    if not data.get('sender') and not data.get('sender_name'):
        return jsonify({'success': False, 'error': 'Sender and receiver required'}), 400
        
    tracking = data.get('tracking_number') or f"KE-{uuid.uuid4().hex[:4].upper()}"
    
    parcel = {
        'trackingNumber': tracking,
        'senderName': data.get('sender_name') or data.get('sender'),
        'receiverName': data.get('receiver_name') or data.get('receiver'),
        'status': 'Registered',
        'weight': data.get('weight_kg') or data.get('weight', 0),
        'cost': 0, 
        'history': [
            {
                'status': 'Registered',
                'timestamp': datetime.utcnow().isoformat(),
                'location': data.get('pickup_location') or 'Origin Hub'
            }
        ]
    }
    
    parcels_store.append(parcel)
    _write_json(PARCELS_FILE, parcels_store)
    
    print(f"\n✓ Success! Registered: [{tracking}] From: {parcel['senderName']} To: {parcel['receiverName']}")
    return jsonify({'success': True, 'parcel': parcel}), 201

@app.route('/api/parcels', methods=['GET'])
def list_parcels():
    return jsonify(parcels_store)

@app.route('/api/parcels/<tracking>', methods=['GET'])
def get_parcel(tracking):
    for p in parcels_store:
        if p.get('trackingNumber') == tracking or p.get('tracking_number') == tracking:
            return jsonify(p)
    return jsonify({'error': 'not found'}), 404

@app.route('/api/calculate_cost', methods=['POST'])
def calculate_cost():
    body = request.json or {}
    try:
        weight = float(body.get('weight_kg', body.get('weight', 0)))
        distance = float(body.get('distance_km', 10))  # Default fallback distance fallback
    except Exception:
        return jsonify({'error': 'invalid numeric values'}), 400
    speed = body.get('speed', body.get('delivery_type', 'standard'))
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