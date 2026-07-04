"""
PARCEL DELIVERY TRACKING SYSTEM - Flask API Server
===================================================

This is the main web server that connects the frontend to the backend.

ENDPOINTS:
- POST /api/register - Register new parcel
- GET /api/track/<id> - Track parcel by ID
- GET /api/search/sender/<name> - Search by sender
- GET /api/search/receiver/<name> - Search by receiver
- GET /api/management/queue - View delivery queue
- POST /api/management/add-queue - Add to queue
- POST /api/management/process - Process next delivery
- POST /api/management/update-status - Update status
- POST /api/cost/calculate - Calculate delivery cost
- GET /api/cost/rates - Get cost rates
- GET /api/reports/parcels - Get all parcels
- GET /api/reports/statistics - Get statistics
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import json

from Parcel_Registration import register_parcel, parcel_database as reg_database
from Parcel_Management import (
    parcel_database, delivery_queue, find_parcel, add_to_queue,
    process_next, update_status, mark_delivered, view_queue,
    DELIVERY_STAGES, enqueue_parcel
)
from Parcel_LiveTracking import binary_search, search_by_sender, search_by_receiver
from Parcel_CostCalculator import calculate_cost, DELIVERY_RATES, DESTINATION_MULTIPLIERS
from Parcel_Reports import ReportGenerator

app = Flask(__name__)
CORS(app)


# ========== FRONTEND ROUTES ==========

@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('frontend', 'index.html')


@app.route('/assets/<path:filename>')
def serve_frontend_assets(filename):
    """Serve frontend files (CSS, JS, images)"""
    return send_from_directory('frontend/assets', filename)


# ========== HELPER FUNCTIONS ==========

def sync_database():
    """
    Sync registration database with management database.
    Ensures all parcels are in the main database and queue.
    """
    for parcel in reg_database:
        if parcel not in parcel_database:
            parcel_database.append(parcel)
        enqueue_parcel(parcel)


# ========== DASHBOARD ROUTES ==========

@app.route('/api/dashboard')
def get_dashboard():
    """Get dashboard statistics"""
    sync_database()
    stats = ReportGenerator.get_statistics()
    return jsonify(stats or {})


@app.route('/api/stats')
def get_stats():
    """Get detailed statistics"""
    sync_database()
    if not parcel_database:
        return jsonify({"error": "No data"}), 404
    
    stats = ReportGenerator.get_statistics()
    return jsonify(stats)


# ========== REGISTRATION ROUTES ==========

@app.route('/api/register', methods=['POST'])
def register_new_parcel():
    """
    Register a new parcel.
    
    Expected JSON:
    {
        "sender": "John Doe",
        "receiver": "Jane Smith",
        "destination": "Mombasa",
        "weight": 2.5,
        "description": "Electronics"
    }
    """
    data = request.get_json()
    sender = data.get('sender', '').strip()
    receiver = data.get('receiver', '').strip()
    destination = data.get('destination', '').strip()
    weight = float(data.get('weight', 0))
    description = data.get('description', '').strip()
    
    if not sender or not receiver:
        return jsonify({"error": "Sender and receiver required"}), 400
    
    parcel = register_parcel(sender, receiver, destination, weight, description)
    if parcel:
        sync_database()
        enqueue_parcel(parcel)

        return jsonify({
            "success": True,
            "tracking_id": parcel.tracking_id,
            "sender": parcel.sender,
            "receiver": parcel.receiver,
            "destination": parcel.destination,
            "weight": parcel.weight,
            "description": parcel.description,
            "status": parcel.status,
            "message": f"Parcel registered: {parcel.tracking_id}"
        }), 201
    
    return jsonify({"error": "Registration failed"}), 400


# ========== TRACKING ROUTES ==========

@app.route('/api/track/<tracking_id>')
def track_parcel(tracking_id):
    """
    Track a parcel by ID.
    Uses Binary Search algorithm - O(log n)
    """
    sync_database()
    parcel = binary_search(tracking_id)
    
    if not parcel:
        return jsonify({"error": "Parcel not found"}), 404
    
    return jsonify({
        "tracking_id": parcel.tracking_id,
        "sender": parcel.sender,
        "receiver": parcel.receiver,
        "status": parcel.status,
        "history": [{
            "status": h[0],
            "timestamp": h[1]
        } for h in parcel.history]
    })


@app.route('/api/search/sender/<name>')
def search_sender(name):
    """
    Search parcels by sender name.
    Uses Linear Search algorithm - O(n)
    """
    sync_database()
    results = search_by_sender(name)
    
    return jsonify({
        "count": len(results),
        "parcels": [{
            "tracking_id": p.tracking_id,
            "sender": p.sender,
            "receiver": p.receiver,
            "status": p.status
        } for p in results]
    })


@app.route('/api/search/receiver/<name>')
def search_receiver(name):
    """
    Search parcels by receiver name.
    Uses Linear Search algorithm - O(n)
    """
    sync_database()
    results = search_by_receiver(name)
    
    return jsonify({
        "count": len(results),
        "parcels": [{
            "tracking_id": p.tracking_id,
            "sender": p.sender,
            "receiver": p.receiver,
            "status": p.status
        } for p in results]
    })


# ========== MANAGEMENT ROUTES ==========

@app.route('/api/management/queue', methods=['GET'])
def get_queue():
    """Get current delivery queue (FIFO order)"""
    sync_database()
    return jsonify({
        "queue_size": len(delivery_queue),
        "parcels": [{
            "position": idx + 1,
            "tracking_id": p.tracking_id,
            "from": p.sender,
            "to": p.receiver,
            "status": p.status
        } for idx, p in enumerate(delivery_queue)]
    })


@app.route('/api/management/add-queue', methods=['POST'])
def add_parcel_to_queue():
    """Add parcel to delivery queue"""
    data = request.get_json()
    tracking_id = data.get('tracking_id', '').strip()
    
    parcel = find_parcel(tracking_id)
    if not parcel:
        return jsonify({"error": "Parcel not found"}), 404
    
    if parcel in delivery_queue:
        return jsonify({"error": "Parcel already in queue"}), 400
    
    delivery_queue.append(parcel)
    return jsonify({"success": True, "message": f"Added {tracking_id} to queue"})


@app.route('/api/management/process', methods=['POST'])
def process_delivery():
    """
    Process next delivery in queue.
    Uses Queue data structure (FIFO) - O(1)
    """
    if not delivery_queue:
        return jsonify({"error": "Queue is empty"}), 400
    
    parcel = delivery_queue.popleft()
    current_index = DELIVERY_STAGES.index(parcel.status)
    
    if current_index >= len(DELIVERY_STAGES) - 1:
        return jsonify({"message": "Parcel already delivered"})
    
    next_stage = DELIVERY_STAGES[current_index + 1]
    parcel.status = next_stage
    parcel.history.append((next_stage, datetime.now().strftime("%Y-%m-%d %H:%M")))
    
    if parcel.status != "Delivered":
        delivery_queue.append(parcel)
    
    return jsonify({
        "success": True,
        "tracking_id": parcel.tracking_id,
        "new_status": parcel.status,
        "message": f"Updated {parcel.tracking_id} to {parcel.status}"
    })


@app.route('/api/management/update-status', methods=['POST'])
def update_parcel_status():
    """Manually update parcel status"""
    data = request.get_json()
    tracking_id = data.get('tracking_id', '').strip()
    new_status = data.get('status', '').strip()
    
    if new_status not in DELIVERY_STAGES:
        return jsonify({"error": f"Invalid status. Must be: {', '.join(DELIVERY_STAGES)}"}), 400
    
    parcel = find_parcel(tracking_id)
    if not parcel:
        return jsonify({"error": "Parcel not found"}), 404
    
    parcel.status = new_status
    parcel.history.append((new_status, datetime.now().strftime("%Y-%m-%d %H:%M")))
    
    if new_status == "Delivered" and parcel in delivery_queue:
        delivery_queue.remove(parcel)
    
    return jsonify({
        "success": True,
        "tracking_id": parcel.tracking_id,
        "new_status": parcel.status,
        "message": f"Status updated to {new_status}"
    })


# ========== COST CALCULATOR ROUTES ==========

@app.route('/api/cost/calculate', methods=['POST'])
def calculate_delivery_cost():
    """
    Calculate delivery cost.
    Uses Stack data structure for history - O(1)
    """
    data = request.get_json()
    
    try:
        weight = float(data.get('weight', 0))
        destination = data.get('destination', 'Other').strip()
        delivery_type = data.get('delivery_type', 'Standard').strip()
        tracking_id = data.get('tracking_id', '').strip() or None
    except ValueError:
        return jsonify({"error": "Invalid weight"}), 400
    
    if weight <= 0:
        return jsonify({"error": "Weight must be greater than 0"}), 400
    
    if delivery_type not in DELIVERY_RATES:
        return jsonify({"error": f"Invalid delivery type: {delivery_type}"}), 400
    
    calc = calculate_cost(weight, destination, delivery_type, tracking_id)
    if calc:
        return jsonify({
            "success": True,
            "weight": calc.weight,
            "destination": calc.destination,
            "delivery_type": calc.delivery_type,
            "breakdown": calc.breakdown,
            "total_cost": calc.total_cost
        })
    
    return jsonify({"error": "Calculation failed"}), 400


@app.route('/api/cost/rates')
def get_cost_rates():
    """Get delivery rates and destinations"""
    return jsonify({
        "rates": DELIVERY_RATES,
        "destinations": list(DESTINATION_MULTIPLIERS.keys())
    })


# ========== REPORTS ROUTES ==========

@app.route('/api/reports/parcels')
def get_all_parcels():
    """Get all parcels data"""
    sync_database()
    parcels_data = ReportGenerator.get_all_parcels_data()
    return jsonify({"parcels": parcels_data, "total": len(parcels_data)})


@app.route('/api/reports/statistics')
def get_reports_statistics():
    """Get reporting statistics"""
    sync_database()
    stats = ReportGenerator.get_statistics()
    return jsonify(stats or {})


# ========== ERROR HANDLERS ==========

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500


# ========== START SERVER ==========

if __name__ == '__main__':
    # Initialize sample data
    sync_database()
    print("\n" + "="*60)
    print("  PARCEL DELIVERY TRACKING SYSTEM")
    print("="*60)
    print("  Server: http://localhost:5000")
    print("  Frontend: http://localhost:5000/")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)