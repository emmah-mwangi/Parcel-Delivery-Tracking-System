"""Main Flask Application - Integrated Parcel Delivery System"""
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os

from Parcel_Registration import ParcelRegistration
from Parcel_CostCalculator import ParcelCostCalculator
from Parcel_LiveTracking import ParcelLiveTracking
from Parcel_Management import ParcelManagement
from Parcel_Reports import ParcelReports

app = Flask(__name__)
CORS(app)

# Initialize modules
registration = ParcelRegistration()
cost_calculator = ParcelCostCalculator()
live_tracking = ParcelLiveTracking(registration)
management = ParcelManagement(registration)
reports = ParcelReports(registration, management)

# ============ REGISTRATION ENDPOINTS ============

@app.route('/api/register', methods=['POST'])
def register_parcel():
    """Register a new parcel"""
    data = request.json
    
    success, message, tracking_id = registration.add_parcel(
        sender=data.get('sender'),
        receiver=data.get('receiver'),
        origin=data.get('origin'),
        destination=data.get('destination'),
        weight=float(data.get('weight', 0))
    )
    
    if not success:
        return jsonify({'success': False, 'message': message}), 400
    
    # Calculate cost
    cost, breakdown = cost_calculator.calculate_cost(
        tracking_id, 
        float(data.get('weight')), 
        data.get('destination'),
        data.get('delivery_type', 'normal')
    )
    
    # Update parcel cost
    parcel = registration.search_by_tracking_id(tracking_id)
    if parcel:
        parcel.cost = cost
    
    return jsonify({
        'success': True,
        'message': message,
        'tracking_id': tracking_id,
        'cost': cost,
        'breakdown': breakdown
    }), 201

@app.route('/api/parcels/count', methods=['GET'])
def get_parcel_count():
    """Get total registered parcels"""
    return jsonify({
        'total_parcels': registration.get_parcel_count()
    })

# ============ COST CALCULATOR ENDPOINTS ============

@app.route('/api/calculate-cost', methods=['POST'])
def calculate_cost():
    """Calculate delivery cost"""
    data = request.json
    
    cost, breakdown = cost_calculator.calculate_cost(
        tracking_id=data.get('tracking_id'),
        weight=float(data.get('weight')),
        destination=data.get('destination'),
        delivery_type=data.get('delivery_type', 'normal')
    )
    
    return jsonify({
        'success': True,
        'cost': cost,
        'breakdown': breakdown
    })

@app.route('/api/cost-history', methods=['GET'])
def get_cost_history():
    """Get calculation history"""
    history = cost_calculator.get_calculation_history()
    stats = {
        'total_calculations': cost_calculator.get_history_size(),
        'total_cost': cost_calculator.get_total_cost(),
        'average_cost': cost_calculator.get_average_cost(),
        'history': history
    }
    return jsonify(stats)

# ============ LIVE TRACKING ENDPOINTS ============

@app.route('/api/track/<tracking_id>', methods=['GET'])
def track_parcel(tracking_id):
    """Track parcel by ID"""
    tracking_info = live_tracking.get_parcel_tracking_info(tracking_id)
    
    if not tracking_info:
        return jsonify({'success': False, 'message': 'Parcel not found'}), 404
    
    return jsonify({
        'success': True,
        'parcel': tracking_info
    })

@app.route('/api/search-parcel', methods=['GET'])
def search_parcel():
    """Search parcel by multiple criteria"""
    search_term = request.args.get('q', '')
    search_by = request.args.get('by', 'all')  # 'tracking', 'sender', 'receiver', 'all'
    
    if not search_term:
        return jsonify({'success': False, 'message': 'Search term required'}), 400
    
    results = []
    
    if search_by == 'tracking':
        parcel = live_tracking.linear_search_by_tracking(search_term)
        if parcel:
            results.append({
                'tracking_id': parcel.tracking_id,
                'sender': parcel.sender,
                'receiver': parcel.receiver,
                'status': parcel.status
            })
    elif search_by == 'sender':
        parcels = live_tracking.linear_search_by_sender(search_term)
        results = [{'tracking_id': p.tracking_id, 'sender': p.sender, 'receiver': p.receiver, 'status': p.status} for p in parcels]
    elif search_by == 'receiver':
        parcels = live_tracking.linear_search_by_receiver(search_term)
        results = [{'tracking_id': p.tracking_id, 'sender': p.sender, 'receiver': p.receiver, 'status': p.status} for p in parcels]
    else:  # all
        parcels = live_tracking.search_all_parcels(search_term)
        results = [{'tracking_id': p.tracking_id, 'sender': p.sender, 'receiver': p.receiver, 'status': p.status} for p in parcels]
    
    return jsonify({
        'success': True,
        'count': len(results),
        'results': results
    })

# ============ MANAGEMENT ENDPOINTS ============

@app.route('/api/queue/add', methods=['POST'])
def add_to_queue():
    """Add parcel to delivery queue"""
    data = request.json
    tracking_id = data.get('tracking_id')
    
    success, message = management.add_to_queue(tracking_id)
    
    if not success:
        return jsonify({'success': False, 'message': message}), 400
    
    return jsonify({'success': True, 'message': message})

@app.route('/api/queue/process', methods=['POST'])
def process_delivery():
    """Process next delivery in queue"""
    success, message, delivery_info = management.process_delivery()
    
    if not success:
        return jsonify({'success': False, 'message': message}), 400
    
    return jsonify({
        'success': True,
        'message': message,
        'delivery': delivery_info
    })

@app.route('/api/queue/info', methods=['GET'])
def get_queue_info():
    """Get delivery queue information"""
    queue_info = management.get_queue_info()
    return jsonify(queue_info)

@app.route('/api/queue/list', methods=['GET'])
def get_queue_list():
    """Get list of parcels in queue"""
    queue_list = management.get_queue_list()
    return jsonify({
        'queue_size': len(queue_list),
        'parcels': queue_list
    })

@app.route('/api/parcel/<tracking_id>/status', methods=['PUT'])
def update_status(tracking_id):
    """Update parcel status"""
    data = request.json
    new_status = data.get('status')
    
    success, message = management.update_parcel_status(tracking_id, new_status)
    
    if not success:
        return jsonify({'success': False, 'message': message}), 400
    
    return jsonify({'success': True, 'message': message})

@app.route('/api/delivered', methods=['GET'])
def get_delivered():
    """Get delivered parcels"""
    delivered = management.get_delivered_parcels()
    return jsonify({
        'count': management.get_delivered_count(),
        'parcels': delivered
    })

# ============ REPORTS ENDPOINTS ============

@app.route('/api/reports/all', methods=['GET'])
def get_all_parcels_report():
    """Get all parcels report"""
    parcels_report = reports.get_all_parcels_report()
    return jsonify({
        'total': len(parcels_report),
        'parcels': parcels_report
    })

@app.route('/api/reports/by-weight', methods=['GET'])
def get_weight_report():
    """Get parcels sorted by weight"""
    ascending = request.args.get('order', 'asc') == 'asc'
    report = reports.get_report_by_weight(ascending=ascending)
    return jsonify({
        'count': len(report),
        'parcels': report
    })

@app.route('/api/reports/by-destination', methods=['GET'])
def get_destination_report():
    """Get parcels sorted by destination"""
    report = reports.get_report_by_destination()
    return jsonify({
        'count': len(report),
        'parcels': report
    })

@app.route('/api/reports/statistics', methods=['GET'])
def get_statistics():
    """Get delivery statistics"""
    stats = reports.get_delivery_statistics()
    return jsonify(stats)

@app.route('/api/reports/by-status', methods=['GET'])
def get_status_report():
    """Get parcels filtered by status"""
    status = request.args.get('status', 'Registered')
    report = reports.get_report_by_status(status)
    return jsonify({
        'status': status,
        'count': len(report),
        'parcels': report
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
