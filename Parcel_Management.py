"""
Parcel Management Module
Handles parcel operations including updates, deletions, searches, and reporting.

Data Structures Used:
1. Priority Queue (Heap) - O(log n) for priority-based parcel processing
2. Graph (Adjacency List) - O(V + E) for route optimization

Algorithms Used:
1. Dijkstra's Shortest Path - O((V + E) log V) for route optimization
2. Heap Sort / Priority Queue Operations - O(log n) for priority management
"""

import json
import os
import heapq
from datetime import datetime
from collections import defaultdict


class ParcelManagement:
    """
    Manages parcel operations with efficient data structures and algorithms.
    """
    
    def __init__(self, data_dir='data'):
        """
        Initialize the management system.
        
        Args:
            data_dir: Directory path for storing parcel data
        """
        self.data_dir = data_dir
        self.parcels_file = os.path.join(data_dir, 'parcels.json')
        os.makedirs(data_dir, exist_ok=True)
        
        # Data Structure 1: Priority Queue (Min-Heap) for priority-based processing
        # Format: (priority_score, timestamp, tracking_number, parcel_data)
        self.priority_queue = []
        
        # Data Structure 2: Graph (Adjacency List) for route optimization
        # Format: {location: [(neighbor, distance), ...]}
        self.route_graph = defaultdict(list)
        
        # Load existing data
        self._load_data()
        self._build_route_graph()
    
    def _load_data(self):
        """
        Load parcels from JSON file.
        Time Complexity: O(n)
        """
        if os.path.exists(self.parcels_file):
            try:
                with open(self.parcels_file, 'r', encoding='utf-8') as f:
                    self.parcels = json.load(f)
            except Exception:
                self.parcels = []
        else:
            self.parcels = []
    
    def _save_data(self):
        """
        Save parcels to JSON file.
        Time Complexity: O(n)
        """
        with open(self.parcels_file, 'w', encoding='utf-8') as f:
            json.dump(self.parcels, f, indent=2, ensure_ascii=False, default=str)
    
    def _build_route_graph(self):
        """
        Build route graph from parcel data for path optimization.
        
        Algorithm 1: Graph Construction
        Time Complexity: O(n) where n is number of parcels
        
        The graph represents possible routes between locations based on parcel origins and destinations.
        """
        # Clear existing graph
        self.route_graph = defaultdict(list)
        
        # Build edges from parcel data
        for parcel in self.parcels:
            origin = parcel.get('origin', '').lower()
            destination = parcel.get('destination', '').lower()
            distance = float(parcel.get('distance_km', 0))
            
            if origin and destination and distance > 0:
                # Add bidirectional edge
                self.route_graph[origin].append((destination, distance))
                self.route_graph[destination].append((origin, distance))
    
    def _calculate_priority_score(self, parcel):
        """
        Calculate priority score for a parcel based on multiple factors.
        
        Algorithm: Priority Scoring
        Time Complexity: O(1)
        
        Args:
            parcel: Parcel data dictionary
            
        Returns:
            float: Priority score (lower = higher priority)
        """
        score = 0.0
        
        # Factor 1: Weight (heavier = higher priority) - weight 30%
        try:
            weight = float(parcel.get('weight_kg', 0))
            score += (100 - min(weight, 100)) * 0.3
        except Exception:
            score += 50 * 0.3
        
        # Factor 2: Status (further along = higher priority) - weight 40%
        status_priority = {
            'delivered': 100,
            'out_for_delivery': 80,
            'in_transit': 60,
            'picked_up': 40,
            'registered': 20,
            'cancelled': 0,
            'returned': 10
        }
        status = parcel.get('status', 'registered')
        score += status_priority.get(status, 20) * 0.4
        
        # Factor 3: Age (older = higher priority) - weight 30%
        try:
            registered_at = parcel.get('registered_at', '')
            if registered_at:
                reg_time = datetime.fromisoformat(registered_at)
                age_hours = (datetime.utcnow() - reg_time).total_seconds() / 3600
                age_score = min(age_hours * 2, 100)  # Cap at 100
                score += age_score * 0.3
        except Exception:
            score += 50 * 0.3
        
        # Return negative score for min-heap (lower score = higher priority)
        return -score
    
    def _dijkstra_shortest_path(self, start, end):
        """
        Algorithm 1: Dijkstra's Shortest Path Algorithm
        Finds the shortest path between two locations in the route graph.
        
        Time Complexity: O((V + E) log V) where V is vertices (locations) and E is edges
        Space Complexity: O(V)
        
        Args:
            start: Starting location
            end: Destination location
            
        Returns:
            tuple: (shortest_distance, path_list) or (float('inf'), []) if no path exists
        """
        start = start.lower()
        end = end.lower()
        
        # Initialize distances and priority queue
        distances = {location: float('inf') for location in self.route_graph}
        distances[start] = 0
        pq = [(0, start, [start])]  # (distance, current_location, path)
        
        visited = set()
        
        while pq:
            current_dist, current_loc, path = heapq.heappop(pq)
            
            # Skip if already visited
            if current_loc in visited:
                continue
            
            visited.add(current_loc)
            
            # Found destination
            if current_loc == end:
                return current_dist, path
            
            # Explore neighbors
            for neighbor, weight in self.route_graph[current_loc]:
                if neighbor not in visited:
                    new_dist = current_dist + weight
                    
                    if new_dist < distances[neighbor]:
                        distances[neighbor] = new_dist
                        new_path = path + [neighbor]
                        heapq.heappush(pq, (new_dist, neighbor, new_path))
        
        # No path found
        return float('inf'), []
    
    def add_to_priority_queue(self, tracking_number):
        """
        Add parcel to priority queue for processing.
        
        Algorithm 2: Priority Queue Insertion (Heap Push)
        Time Complexity: O(log n)
        
        Args:
            tracking_number: Parcel tracking number
            
        Returns:
            bool: True if added successfully, False if parcel not found
        """
        parcel = self.get_parcel(tracking_number)
        
        if not parcel:
            return False
        
        priority_score = self._calculate_priority_score(parcel)
        timestamp = datetime.utcnow().isoformat()
        
        # Push to min-heap (lower score = higher priority)
        heapq.heappush(self.priority_queue, (priority_score, timestamp, tracking_number, parcel))
        
        return True
    
    def process_next_priority(self):
        """
        Process the next highest priority parcel.
        
        Algorithm 2: Priority Queue Extraction (Heap Pop)
        Time Complexity: O(log n)
        
        Returns:
            dict: Parcel data or None if queue is empty
        """
        if not self.priority_queue:
            return None
        
        # Pop highest priority item (lowest score)
        priority_score, timestamp, tracking_number, parcel = heapq.heappop(self.priority_queue)
        
        return {
            'tracking_number': tracking_number,
            'priority_score': abs(priority_score),  # Convert back to positive
            'parcel': parcel
        }
    
    def get_parcel(self, tracking_number):
        """
        Retrieve parcel by tracking number.
        
        Time Complexity: O(n) - linear search
        
        Args:
            tracking_number: Tracking number
            
        Returns:
            dict: Parcel data or None if not found
        """
        for parcel in self.parcels:
            if parcel.get('tracking_number') == tracking_number:
                return parcel
        return None
    
    def update_parcel(self, tracking_number, updates):
        """
        Update parcel information.
        
        Time Complexity: O(n)
        
        Args:
            tracking_number: Tracking number
            updates: Dictionary of fields to update
            
        Returns:
            dict: Updated parcel or error message
        """
        parcel = self.get_parcel(tracking_number)
        
        if not parcel:
            return {'error': 'Parcel not found'}
        
        # Update fields
        for key, value in updates.items():
            if key not in ['tracking_number', 'history']:  # Protect these fields
                parcel[key] = value
        
        # Add update to history
        if 'status' in updates:
            history_entry = {
                'status': updates['status'],
                'timestamp': datetime.utcnow().isoformat(),
                'location': updates.get('current_location', updates.get('location', ''))
            }
            parcel.setdefault('history', []).append(history_entry)
        
        # Save changes
        self._save_data()
        
        # Rebuild route graph if location changed
        if 'origin' in updates or 'destination' in updates:
            self._build_route_graph()
        
        return parcel
    
    def delete_parcel(self, tracking_number):
        """
        Delete a parcel from the system.
        
        Time Complexity: O(n)
        
        Args:
            tracking_number: Tracking number
            
        Returns:
            bool: True if deleted, False if not found
        """
        for i, parcel in enumerate(self.parcels):
            if parcel.get('tracking_number') == tracking_number:
                self.parcels.pop(i)
                self._save_data()
                self._build_route_graph()
                return True
        return False
    
    def search_parcels(self, **criteria):
        """
        Search parcels by multiple criteria.
        
        Time Complexity: O(n * m) where n is parcels and m is criteria
        
        Args:
            criteria: Key-value pairs to search
            
        Returns:
            list: Matching parcels
        """
        results = []
        
        for parcel in self.parcels:
            match = True
            for key, value in criteria.items():
                if parcel.get(key) != value:
                    match = False
                    break
            if match:
                results.append(parcel)
        
        return results
    
    def find_optimal_route(self, origin, destination):
        """
        Find optimal route between two locations using Dijkstra's algorithm.
        
        Algorithm 1: Dijkstra's Shortest Path
        Time Complexity: O((V + E) log V)
        
        Args:
            origin: Starting location
            destination: Ending location
            
        Returns:
            dict: Route information including distance and path
        """
        distance, path = self._dijkstra_shortest_path(origin, destination)
        
        if distance == float('inf'):
            return {
                'error': 'No route found',
                'origin': origin,
                'destination': destination
            }
        
        return {
            'origin': origin,
            'destination': destination,
            'distance_km': round(distance, 2),
            'path': path,
            'estimated_time_hours': round(distance / 60, 2)  # Assuming 60 km/h average speed
        }
    
    def get_parcels_by_route(self, origin, destination):
        """
        Get all parcels that travel between two locations.
        
        Time Complexity: O(n)
        
        Args:
            origin: Origin location
            destination: Destination location
            
        Returns:
            list: List of parcels on this route
        """
        origin = origin.lower()
        destination = destination.lower()
        
        return [
            p for p in self.parcels
            if p.get('origin', '').lower() == origin and p.get('destination', '').lower() == destination
        ]
    
    def batch_update_status(self, tracking_numbers, new_status, location=''):
        """
        Batch update status for multiple parcels.
        
        Time Complexity: O(n * m) where n is parcels and m is tracking numbers
        
        Args:
            tracking_numbers: List of tracking numbers
            new_status: New status to apply
            location: Location for the status update
            
        Returns:
            dict: Summary of batch update
        """
        successful = []
        failed = []
        
        for tracking in tracking_numbers:
            result = self.update_parcel(tracking, {
                'status': new_status,
                'current_location': location
            })
            
            if 'error' in result:
                failed.append({'tracking_number': tracking, 'error': result['error']})
            else:
                successful.append(tracking)
        
        return {
            'successful_count': len(successful),
            'failed_count': len(failed),
            'successful': successful,
            'failed': failed
        }
    
    def get_priority_list(self, limit=None):
        """
        Get parcels sorted by priority.
        
        Algorithm 2: Priority Queue Sorting
        Time Complexity: O(n log n) for heap operations
        
        Args:
            limit: Maximum number of results (None for all)
            
        Returns:
            list: List of parcels sorted by priority (highest first)
        """
        # Rebuild priority queue with all parcels
        self.priority_queue = []
        
        for parcel in self.parcels:
            priority_score = self._calculate_priority_score(parcel)
            timestamp = parcel.get('registered_at', datetime.utcnow().isoformat())
            tracking = parcel.get('tracking_number', '')
            heapq.heappush(self.priority_queue, (priority_score, timestamp, tracking, parcel))
        
        # Extract parcels
        results = []
        count = 0
        
        while self.priority_queue and (limit is None or count < limit):
            priority_score, timestamp, tracking, parcel = heapq.heappop(self.priority_queue)
            results.append({
                'tracking_number': tracking,
                'priority_score': abs(priority_score),
                'parcel': parcel
            })
            count += 1
        
        return results
    
    def get_statistics(self):
        """
        Get management statistics.
        
        Returns:
            dict: Management statistics
        """
        total = len(self.parcels)
        
        status_counts = {}
        weight_total = 0
        distance_total = 0
        
        for parcel in self.parcels:
            status = parcel.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
            
            try:
                weight_total += float(parcel.get('weight_kg', 0))
            except Exception:
                pass
            
            try:
                distance_total += float(parcel.get('distance_km', 0))
            except Exception:
                pass
        
        # Count graph nodes and edges
        graph_nodes = len(self.route_graph)
        graph_edges = sum(len(neighbors) for neighbors in self.route_graph.values()) // 2  # Bidirectional
        
        return {
            'total_parcels': total,
            'status_distribution': status_counts,
            'total_weight_kg': round(weight_total, 2),
            'total_distance_km': round(distance_total, 2),
            'average_weight_kg': round(weight_total / total, 2) if total > 0 else 0,
            'average_distance_km': round(distance_total / total, 2) if total > 0 else 0,
            'route_graph': {
                'locations': graph_nodes,
                'routes': graph_edges
            }
        }
    
    def get_all_parcels(self):
        """
        Get all parcels.
        
        Returns:
            list: List of all parcels
        """
        return list(self.parcels)
    
    def clear_priority_queue(self):
        """
        Clear the priority queue.
        
        Time Complexity: O(1)
        """
        self.priority_queue = []


# Example usage and testing
if __name__ == '__main__':
    # Initialize management system
    mgmt_system = ParcelManagement()
    
    print("Parcel Management System Test")
    print("=" * 50)
    
    # Test 1: Register some parcels first
    print("\nTest 1: Setting up test data...")
    from Parcel_Registration import ParcelRegistration
    reg_system = ParcelRegistration()
    
    parcel1 = reg_system.register_parcel("Sender A", "Receiver B", "Nairobi", "Mombasa", 10.0)
    parcel2 = reg_system.register_parcel("Sender C", "Receiver D", "Kisumu", "Eldoret", 5.0)
    parcel3 = reg_system.register_parcel("Sender E", "Receiver F", "Mombasa", "Nairobi", 15.0)
    
    print(f"Registered 3 parcels")
    
    # Reload management system
    mgmt_system = ParcelManagement()
    
    # Test 2: Priority Queue
    print("\nTest 2: Priority Queue Operations...")
    mgmt_system.add_to_priority_queue(parcel1['tracking_number'])
    mgmt_system.add_to_priority_queue(parcel2['tracking_number'])
    mgmt_system.add_to_priority_queue(parcel3['tracking_number'])
    
    print("Processing by priority:")
    for i in range(3):
        next_item = mgmt_system.process_next_priority()
        if next_item:
            print(f"  {i+1}. {next_item['tracking_number']} - Priority: {next_item['priority_score']:.2f}")
    
    # Test 3: Dijkstra's Shortest Path
    print("\nTest 3: Route Optimization (Dijkstra's Algorithm)...")
    route = mgmt_system.find_optimal_route("mombasa", "nairobi")
    if 'error' not in route:
        print(f"Route: {' -> '.join(route['path'])}")
        print(f"Distance: {route['distance_km']} km")
        print(f"Estimated time: {route['estimated_time_hours']} hours")
    else:
        print(f"Error: {route['error']}")
    
    # Test 4: Batch Update
    print("\nTest 4: Batch Status Update...")
    result = mgmt_system.batch_update_status(
        [parcel1['tracking_number'], parcel2['tracking_number']],
        'picked_up',
        'Collection Center'
    )
    print(f"Updated {result['successful_count']} parcels successfully")
    
    # Test 5: Statistics
    print("\nTest 5: Management Statistics...")
    stats = mgmt_system.get_statistics()
    print(f"Total parcels: {stats['total_parcels']}")
    print(f"Status distribution: {stats['status_distribution']}")
    print(f"Route graph: {stats['route_graph']['locations']} locations, {stats['route_graph']['routes']} routes")
    
    # Test 6: Priority List
    print("\nTest 6: Priority List...")
    priority_list = mgmt_system.get_priority_list(limit=3)
    print("Top 3 priority parcels:")
    for i, item in enumerate(priority_list, 1):
        print(f"  {i}. {item['tracking_number']} - Score: {item['priority_score']:.2f}")