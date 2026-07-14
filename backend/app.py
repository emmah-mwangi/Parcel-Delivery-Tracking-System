"""
PARCEL DELIVERY TRACKING SYSTEM - BACKEND
============================================
Flask REST API. This is the single source of truth for the system -
the frontend (frontend/app.js) only talks to the endpoints below; it
holds no business logic and no local copy of the data structures.

Persistence: parcels are saved to data/parcels.json on every write, and
the in-memory structures (hash table, priority queue) are rebuilt from
that file on startup, so a server restart doesn't lose data.
"""

import os
import json
import uuid
from datetime import datetime

from flask import Flask, jsonify, request, send_from_directory

from data_structures import HashTable, ParcelQueue, StatusStack, PriorityQueue, Graph
import algorithms
from cost_calculator import CostCalculator
from reports import Reports

# ------------------------------------------------------------------
# Paths & persistence helpers
# ------------------------------------------------------------------
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
PARCELS_FILE = os.path.join(DATA_DIR, 'parcels.json')
COUNTER_FILE = os.path.join(DATA_DIR, 'counter.json')

os.makedirs(DATA_DIR, exist_ok=True)


def read_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except (json.JSONDecodeError, ValueError):
            return default


def write_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)


def save_parcels():
    write_json(PARCELS_FILE, parcels_array)


def next_tracking_number():
    counter = read_json(COUNTER_FILE, {'value': 1})
    tracking = 'PK' + str(counter['value']).zfill(4)
    counter['value'] += 1
    write_json(COUNTER_FILE, counter)
    return tracking


# ------------------------------------------------------------------
# App + in-memory structures
# ------------------------------------------------------------------
app = Flask(__name__, static_folder=os.path.join(BASE_DIR, '..', 'frontend'), static_url_path='/')

# Manual CORS headers (no flask-cors package needed)
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

@app.route('/api/parcels', methods=['OPTIONS'])
@app.route('/api/parcels/<path:tracking>', methods=['OPTIONS'])
def handle_options(tracking=None):
    return '', 204

parcels_array = read_json(PARCELS_FILE, [])          # 1. ARRAY - primary store
lookup_table = HashTable()                            # 2. HASH TABLE - O(1) by tracking_number
dispatch_queue = PriorityQueue()                       # 3. PRIORITY QUEUE - dispatch order
status_log = StatusStack()                             # 4. STACK - LIFO status change log
processed_queue = ParcelQueue()                        # 5. QUEUE - FIFO of dispatched parcels
route_network = Graph()                                 # 6. GRAPH - town-to-town road network

cost_calculator = CostCalculator()
reports = Reports()


def rebuild_indexes():
    """Rebuild the hash table & priority queue from the array on startup."""
    lookup_table.rebuild(parcels_array, key_fn=lambda p: p['tracking_number'])
    for p in parcels_array:
        if p.get('status') == 'Registered':
            dispatch_queue.push(p, p.get('delivery_type', 'standard'))


def seed_route_network():
    """Kenyan town-to-town network used by the cost calculator (Dijkstra)."""
    edges = [
        ('Nairobi', 'Thika', 45),
        ('Nairobi', 'Machakos', 63),
        ('Nairobi', 'Naivasha', 90),
        ('Nairobi', 'Nyeri', 150),
        ('Nairobi', 'Mombasa', 480),
        ('Thika', 'Nyeri', 110),
        ('Naivasha', 'Nakuru', 75),
        ('Nyeri', 'Nakuru', 160),
        ('Nakuru', 'Eldoret', 155),
        ('Nakuru', 'Kericho', 95),
        ('Kericho', 'Kisumu', 90),
        ('Eldoret', 'Kakamega', 65),
        ('Eldoret', 'Kitale', 70),
        ('Kakamega', 'Kisumu', 55),
        ('Mombasa', 'Malindi', 120),
        ('Machakos', 'Kitui', 135),
    ]
    for a, b, dist in edges:
        route_network.add_edge(a, b, dist)


rebuild_indexes()
seed_route_network()


# ------------------------------------------------------------------
# Static frontend
# ------------------------------------------------------------------
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


# ------------------------------------------------------------------
# PARCEL CRUD  (Array + Hash Table)
# ------------------------------------------------------------------
@app.route('/api/parcels', methods=['GET'])
def list_parcels():
    return jsonify(parcels_array)


@app.route('/api/parcels/<tracking>', methods=['GET'])
def get_parcel(tracking):
    parcel = lookup_table.get(tracking)  # O(1) hash table lookup
    if not parcel:
        return jsonify({'error': 'Parcel not found'}), 404
    return jsonify(parcel)


@app.route('/api/parcels', methods=['POST'])
def create_parcel():
    body = request.json or {}
    required = ['sender_name', 'receiver_name', 'weight_kg']
    missing = [f for f in required if not body.get(f)]
    if missing:
        return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400

    delivery_type = body.get('delivery_type', 'standard')
    is_fragile = bool(body.get('is_fragile', False))

    path, distance_km = algorithms.dijkstra(route_network, 'Nairobi', 'Mombasa')
    if path is None:
        return jsonify({'error': 'No known route between default towns'}), 400

    breakdown = cost_calculator.calculate_cost(body['weight_kg'], distance_km, delivery_type, is_fragile)

    tracking = next_tracking_number()
    now = datetime.utcnow().isoformat()
    parcel = {
        'tracking_number': tracking,
        'sender_name': body['sender_name'],
        'sender_phone': body.get('sender_phone', ''),
        'sender_email': body.get('sender_email', ''),
        'pickup_location': body.get('pickup_location', ''),
        'receiver_name': body['receiver_name'],
        'receiver_phone': body.get('receiver_phone', ''),
        'receiver_email': body.get('receiver_email', ''),
        'delivery_location': body.get('delivery_location', ''),
        'route_path': path,
        'distance_km': distance_km,
        'parcel_description': body.get('parcel_description', ''),
        'weight_kg': float(body['weight_kg']),
        'delivery_type': delivery_type,
        'is_fragile': is_fragile,
        'cost': breakdown['total'],
        'cost_breakdown': breakdown,
        'status': 'Registered',
        'registration_date': now,
        'status_history': [{'status': 'Registered', 'timestamp': now, 'location': 'Warehouse'}]
    }

    parcels_array.append(parcel)                 # array insert
    lookup_table.set(tracking, parcel)            # hash table insert
    dispatch_queue.push(parcel, delivery_type)     # priority queue insert
    status_log.push({'tracking_number': tracking, 'from': None, 'to': 'Registered', 'timestamp': now})
    save_parcels()

    return jsonify(parcel), 201


@app.route('/api/parcels/<tracking>/status', methods=['PUT'])
def update_status(tracking):
    parcel = lookup_table.get(tracking)
    if not parcel:
        return jsonify({'error': 'Parcel not found'}), 404

    body = request.json or {}
    new_status = body.get('status')
    location = body.get('location', '')
    if not new_status:
        return jsonify({'error': 'status is required'}), 400

    old_status = parcel['status']
    now = datetime.utcnow().isoformat()
    parcel['status'] = new_status
    parcel.setdefault('status_history', []).append({'status': new_status, 'timestamp': now, 'location': location})

    status_log.push({'tracking_number': tracking, 'from': old_status, 'to': new_status, 'timestamp': now})
    save_parcels()
    return jsonify(parcel)


@app.route('/api/parcels/<tracking>', methods=['DELETE'])
def delete_parcel(tracking):
    global parcels_array
    if not lookup_table.contains(tracking):
        return jsonify({'error': 'Parcel not found'}), 404

    parcels_array = [p for p in parcels_array if p['tracking_number'] != tracking]
    lookup_table.delete(tracking)
    save_parcels()
    return jsonify({'success': True})


# ------------------------------------------------------------------
# UNDO  (Stack)
# ------------------------------------------------------------------
@app.route('/api/undo-last-status', methods=['POST'])
def undo_last_status():
    entry = status_log.pop()
    if not entry:
        return jsonify({'error': 'Nothing to undo'}), 400

    parcel = lookup_table.get(entry['tracking_number'])
    if parcel:
        parcel['status'] = entry['from'] or 'Registered'
        if parcel.get('status_history'):
            parcel['status_history'].pop()
        save_parcels()

    return jsonify({'reverted': entry, 'parcel': parcel})


@app.route('/api/status-log', methods=['GET'])
def get_status_log():
    return jsonify(status_log.to_list())  # newest-first (LIFO view)


# ------------------------------------------------------------------
# DISPATCH QUEUE  (Priority Queue + FIFO Queue)
# ------------------------------------------------------------------
@app.route('/api/queue', methods=['GET'])
def view_queue():
    ordered = dispatch_queue.to_ordered_list()
    return jsonify([{
        'tracking_number': p['tracking_number'],
        'delivery_type': p['delivery_type']
    } for p in ordered])


@app.route('/api/queue/process-next', methods=['POST'])
def process_next():
    parcel = dispatch_queue.pop()
    if not parcel:
        return jsonify({'error': 'Queue is empty'}), 400

    now = datetime.utcnow().isoformat()
    parcel['status'] = 'Dispatched'
    parcel.setdefault('status_history', []).append({'status': 'Dispatched', 'timestamp': now, 'location': 'Warehouse'})
    status_log.push({'tracking_number': parcel['tracking_number'], 'from': 'Registered', 'to': 'Dispatched', 'timestamp': now})
    processed_queue.enqueue(parcel['tracking_number'])  # FIFO record of dispatch order
    save_parcels()
    return jsonify(parcel)


# ------------------------------------------------------------------
# SEARCH  (Linear Search / Binary Search)
# ------------------------------------------------------------------
@app.route('/api/search', methods=['GET'])
def search_parcels():
    field = request.args.get('field', 'tracking_number')
    value = request.args.get('value', '')
    algorithm = request.args.get('algorithm', 'linear')

    if algorithm == 'binary':
        sorted_parcels = algorithms.merge_sort(parcels_array, field)
        result = algorithms.binary_search(sorted_parcels, field, value)
    else:
        result = algorithms.linear_search(parcels_array, field, value)

    if not result:
        return jsonify({'error': 'No match found', 'algorithm': algorithm}), 404
    return jsonify({'result': result, 'algorithm': algorithm})


# ------------------------------------------------------------------
# SORT  (Bubble / Selection / Merge)
# ------------------------------------------------------------------
@app.route('/api/sort', methods=['GET'])
def sort_parcels():
    field = request.args.get('field', 'tracking_number')
    algorithm = request.args.get('algorithm', 'merge')
    reverse = request.args.get('order', 'asc') == 'desc'

    if algorithm == 'bubble':
        sorted_parcels = algorithms.bubble_sort(parcels_array, field, reverse)
    elif algorithm == 'selection':
        sorted_parcels = algorithms.selection_sort(parcels_array, field, reverse)
    else:
        sorted_parcels = algorithms.merge_sort(parcels_array, field, reverse)

    return jsonify({'result': sorted_parcels, 'algorithm': algorithm, 'field': field})


# ------------------------------------------------------------------
# ROUTE NETWORK  (Graph + Dijkstra)
# ------------------------------------------------------------------
@app.route('/api/routes/cities', methods=['GET'])
def list_cities():
    return jsonify(route_network.towns())


@app.route('/api/routes/shortest', methods=['GET'])
def shortest_route():
    origin = request.args.get('from')
    destination = request.args.get('to')
    path, distance = algorithms.dijkstra(route_network, origin, destination)
    if path is None:
        return jsonify({'error': 'No route found'}), 404
    return jsonify({'path': path, 'distance_km': distance})


# ------------------------------------------------------------------
# COST CALCULATOR
# ------------------------------------------------------------------
@app.route('/api/calculate-cost', methods=['POST'])
def calculate_cost():
    body = request.json or {}
    try:
        weight = float(body.get('weight_kg', 0))
    except (TypeError, ValueError):
        return jsonify({'error': 'weight_kg must be numeric'}), 400

    origin = 'Nairobi'
    destination = 'Mombasa'
    delivery_type = body.get('delivery_type', 'standard')
    is_fragile = bool(body.get('is_fragile', False))

    path, distance_km = algorithms.dijkstra(route_network, origin, destination)
    if path is None:
        return jsonify({'error': 'No known route between those towns'}), 400

    breakdown = cost_calculator.calculate_cost(weight, distance_km, delivery_type, is_fragile)
    return jsonify({'path': path, 'distance_km': distance_km, 'breakdown': breakdown})


# ------------------------------------------------------------------
# REPORTS
# ------------------------------------------------------------------
@app.route('/api/reports', methods=['GET'])
def get_reports():
    return jsonify({
        'summary': reports.summary(parcels_array),
        'top_destinations': reports.top_destinations(parcels_array),
        'weight_distribution': reports.weight_distribution(parcels_array),
        'queue_status': reports.queue_status(dispatch_queue)
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
