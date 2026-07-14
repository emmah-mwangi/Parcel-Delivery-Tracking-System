"""Flask backend for Parcel Delivery Tracking System"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import uuid
from data_structures import (
    Parcel, ParcelStatus, ParcelLinkedList, HashTable,
    LocationBST, ParcelPriorityQueue, Graph
)
from algorithms import SortingAlgorithms, SearchingAlgorithms, PathfindingAlgorithms

app = Flask(__name__)
CORS(app)

# Initialize data structures
parcel_hash_table = HashTable()
parcel_linked_list = ParcelLinkedList()
location_bst = LocationBST()
delivery_queue = ParcelPriorityQueue()
location_graph = Graph()

# Sample locations and distances for route optimization
LOCATIONS = {
    'Downtown': (1.2862, 36.8172),
    'Westlands': (1.2688, 36.8160),
    'Kilimani': (1.2921, 36.8025),
    'Parklands': (1.2500, 36.8300),
    'Upper Hill': (1.3000, 36.8000),
}

@app.route('/api/parcels', methods=['POST'])
def create_parcel():
    """Create new parcel - demonstrates CRUD and data structure insertion"""
    data = request.json
    
    # Generate unique tracking ID
    tracking_id = f"PKL-{uuid.uuid4().hex[:8].upper()}"
    
    # Create parcel object
    parcel = Parcel(
        tracking_id=tracking_id,
        sender=data.get('sender'),
        recipient=data.get('recipient'),
        origin=data.get('origin'),
        destination=data.get('destination'),
        weight=float(data.get('weight', 0)),
        priority=int(data.get('priority', 5))
    )
    
    # Insert into all data structures
    parcel_hash_table.insert(tracking_id, parcel)
    parcel_linked_list.append(parcel)
    location_bst.insert(parcel.origin, parcel)
    delivery_queue.enqueue(parcel)
    
    return jsonify({
        'success': True,
        'tracking_id': tracking_id,
        'message': 'Parcel created successfully'
    }), 201

@app.route('/api/parcels/<tracking_id>', methods=['GET'])
def get_parcel(tracking_id):
    """Retrieve parcel by ID - O(1) hash table lookup"""
    parcel = parcel_hash_table.search(tracking_id)
    
    if not parcel:
        return jsonify({'error': 'Parcel not found'}), 404
    
    return jsonify({
        'tracking_id': parcel.tracking_id,
        'sender': parcel.sender,
        'recipient': parcel.recipient,
        'origin': parcel.origin,
        'destination': parcel.destination,
        'status': parcel.status.value,
        'weight': parcel.weight,
        'priority': parcel.priority,
        'created_at': parcel.created_at.isoformat(),
        'location_history': parcel.location_history
    }), 200

@app.route('/api/parcels', methods=['GET'])
def list_parcels():
    """List all parcels with sorting options"""
    sort_by = request.args.get('sort_by', 'priority')
    order = request.args.get('order', 'desc')
    
    # Get all parcels
    all_parcels = parcel_hash_table.get_all()
    
    # Sort using merge sort algorithm - O(n log n)
    sorted_parcels = SortingAlgorithms.merge_sort(all_parcels, sort_by)
    
    if order == 'asc':
        sorted_parcels.reverse()
    
    return jsonify({
        'total': len(sorted_parcels),
        'parcels': [
            {
                'tracking_id': p.tracking_id,
                'sender': p.sender,
                'recipient': p.recipient,
                'status': p.status.value,
                'priority': p.priority,
                'origin': p.origin,
                'destination': p.destination
            }
            for p in sorted_parcels
        ]
    }), 200

@app.route('/api/parcels/<tracking_id>/update-status', methods=['PUT'])
def update_parcel_status(tracking_id):
    """Update parcel status and location"""
    parcel = parcel_hash_table.search(tracking_id)
    
    if not parcel:
        return jsonify({'error': 'Parcel not found'}), 404
    
    data = request.json
    new_status = ParcelStatus(data.get('status'))
    current_location = data.get('location')
    
    # Update parcel
    parcel.status = new_status
    parcel.updated_at = datetime.now()
    
    if current_location:
        parcel.location_history.append(current_location)
    
    return jsonify({
        'success': True,
        'tracking_id': tracking_id,
        'status': new_status.value,
        'updated_at': parcel.updated_at.isoformat()
    }), 200

@app.route('/api/parcels/search/by-location', methods=['GET'])
def search_by_location():
    """Search parcels by location - uses BST - O(log n)"""
    location = request.args.get('location')
    
    if not location:
        return jsonify({'error': 'Location parameter required'}), 400
    
    parcels = location_bst.search(location)
    
    return jsonify({
        'location': location,
        'count': len(parcels),
        'parcels': [
            {
                'tracking_id': p.tracking_id,
                'sender': p.sender,
                'recipient': p.recipient,
                'status': p.status.value
            }
            for p in parcels
        ]
    }), 200

@app.route('/api/parcels/search/by-status', methods=['GET'])
def search_by_status():
    """Search parcels by status - linear search - O(n)"""
    status = request.args.get('status')
    
    if not status:
        return jsonify({'error': 'Status parameter required'}), 400
    
    all_parcels = parcel_hash_table.get_all()
    
    def status_filter(parcel):
        return parcel.status.value == status
    
    matching = SearchingAlgorithms.linear_search(all_parcels, status_filter)
    
    return jsonify({
        'status': status,
        'count': len(matching),
        'parcels': [
            {
                'tracking_id': p.tracking_id,
                'sender': p.sender,
                'recipient': p.recipient,
                'origin': p.origin,
                'destination': p.destination
            }
            for p in matching
        ]
    }), 200

@app.route('/api/delivery-queue', methods=['GET'])
def get_delivery_queue():
    """Get next parcels for delivery - priority queue - O(1)"""
    count = int(request.args.get('count', 5))
    next_parcels = []
    
    # Create temporary queue to peek
    temp_parcel = delivery_queue.peek()
    
    return jsonify({
        'queue_size': delivery_queue.size(),
        'next_to_deliver': {
            'tracking_id': temp_parcel.tracking_id,
            'recipient': temp_parcel.recipient,
            'destination': temp_parcel.destination,
            'priority': temp_parcel.priority
        } if temp_parcel else None
    }), 200

@app.route('/api/route-optimization', methods=['POST'])
def optimize_route():
    """Optimize delivery route - uses Dijkstra's algorithm"""
    data = request.json
    start_location = data.get('start')
    end_location = data.get('end')
    
    # Initialize graph with sample locations
    location_graph.add_edge('Downtown', 'Westlands', 5.2)
    location_graph.add_edge('Downtown', 'Kilimani', 3.8)
    location_graph.add_edge('Westlands', 'Parklands', 4.1)
    location_graph.add_edge('Kilimani', 'Upper Hill', 2.5)
    location_graph.add_edge('Parklands', 'Upper Hill', 6.3)
    
    distance, path = location_graph.dijkstra(start_location, end_location)
    
    return jsonify({
        'start': start_location,
        'end': end_location,
        'optimal_distance': distance,
        'optimal_path': path,
        'algorithm': 'Dijkstra\'s Shortest Path'
    }), 200

@app.route('/api/algorithm-analysis', methods=['GET'])
def get_complexity_analysis():
    """Get complexity analysis for all algorithms"""
    from algorithms import ComplexityAnalysis
    
    analysis = ComplexityAnalysis.get_complexity_analysis()
    
    return jsonify({
        'algorithms': analysis,
        'note': 'Time and space complexity for all implemented algorithms'
    }), 200

@app.route('/api/system-stats', methods=['GET'])
def get_system_stats():
    """Get system statistics"""
    all_parcels = parcel_hash_table.get_all()
    
    status_counts = {}
    for parcel in all_parcels:
        status = parcel.status.value
        status_counts[status] = status_counts.get(status, 0) + 1
    
    return jsonify({
        'total_parcels': len(all_parcels),
        'queue_size': delivery_queue.size(),
        'status_distribution': status_counts,
        'data_structures_used': [
            'Hash Table (O(1) lookup)',
            'Doubly-Linked List (O(1) insertion)',
            'Binary Search Tree (O(log n) search)',
            'Priority Queue/Min-Heap (O(log n) operations)',
            'Graph (O(V+E) traversal)'
        ],
        'algorithms_used': [
            'Merge Sort O(n log n)',
            'Binary Search O(log n)',
            'Dijkstra Shortest Path O((V+E) log V)',
            'Nearest Neighbor TSP O(n²)',
            'Priority Queue Management'
        ]
    }), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
