"""Advanced Data Structures for Parcel Delivery Tracking System"""
import heapq
from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class ParcelStatus(Enum):
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    FAILED = "failed"

@dataclass
class Parcel:
    """Represents a parcel with tracking information"""
    tracking_id: str
    sender: str
    recipient: str
    origin: str
    destination: str
    status: ParcelStatus = ParcelStatus.PENDING
    weight: float = 0.0
    priority: int = 0  # 1-10, higher = more urgent
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    location_history: List[str] = field(default_factory=list)
    
    def __lt__(self, other):
        """For priority queue comparison"""
        return self.priority > other.priority  # Max heap (higher priority first)

class LinkedListNode:
    """Node for doubly-linked list implementation"""
    def __init__(self, parcel: Parcel):
        self.parcel = parcel
        self.next = None
        self.prev = None

class ParcelLinkedList:
    """Doubly-linked list for parcel history/trail
    
    Time Complexity: O(1) insertion/deletion at known position, O(n) search
    Space Complexity: O(n)
    """
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0
    
    def append(self, parcel: Parcel) -> None:
        """Add parcel to end of list"""
        node = LinkedListNode(parcel)
        if not self.head:
            self.head = self.tail = node
        else:
            self.tail.next = node
            node.prev = self.tail
            self.tail = node
        self.size += 1
    
    def get_all(self) -> List[Parcel]:
        """Retrieve all parcels in order"""
        result = []
        current = self.head
        while current:
            result.append(current.parcel)
            current = current.next
        return result
    
    def reverse_traverse(self) -> List[Parcel]:
        """Traverse linked list backwards - for delivery history"""
        result = []
        current = self.tail
        while current:
            result.append(current.parcel)
            current = current.prev
        return result

class HashTable:
    """Hash table implementation for O(1) parcel lookup
    
    Time Complexity: O(1) average case, O(n) worst case
    Space Complexity: O(n)
    """
    def __init__(self, size: int = 1000):
        self.size = size
        self.table: List[List[Tuple[str, Parcel]]] = [[] for _ in range(size)]
        self.count = 0
    
    def _hash(self, key: str) -> int:
        """Hash function using polynomial rolling hash"""
        hash_val = 0
        for i, char in enumerate(key):
            hash_val += ord(char) * (31 ** i)
        return hash_val % self.size
    
    def insert(self, tracking_id: str, parcel: Parcel) -> None:
        """Insert parcel with O(1) average time"""
        index = self._hash(tracking_id)
        self.table[index].append((tracking_id, parcel))
        self.count += 1
    
    def search(self, tracking_id: str) -> Optional[Parcel]:
        """Search for parcel - O(1) average"""
        index = self._hash(tracking_id)
        for key, parcel in self.table[index]:
            if key == tracking_id:
                return parcel
        return None
    
    def delete(self, tracking_id: str) -> bool:
        """Delete parcel"""
        index = self._hash(tracking_id)
        for i, (key, _) in enumerate(self.table[index]):
            if key == tracking_id:
                self.table[index].pop(i)
                self.count -= 1
                return True
        return False
    
    def get_all(self) -> List[Parcel]:
        """Get all parcels"""
        result = []
        for bucket in self.table:
            for _, parcel in bucket:
                result.append(parcel)
        return result

class TreeNode:
    """Node for binary search tree (route optimization)"""
    def __init__(self, location: str):
        self.location = location
        self.left = None
        self.right = None
        self.parcels: List[Parcel] = []

class LocationBST:
    """Binary Search Tree for location-based parcel organization
    
    Time Complexity: O(log n) average case for insertion/search
    Space Complexity: O(n)
    """
    def __init__(self):
        self.root = None
    
    def insert(self, location: str, parcel: Parcel) -> None:
        """Insert parcel by location"""
        if not self.root:
            self.root = TreeNode(location)
            self.root.parcels.append(parcel)
        else:
            self._insert_recursive(self.root, location, parcel)
    
    def _insert_recursive(self, node: TreeNode, location: str, parcel: Parcel) -> None:
        if location < node.location:
            if node.left is None:
                node.left = TreeNode(location)
            node.left.parcels.append(parcel) if location == node.left.location else self._insert_recursive(node.left, location, parcel)
        else:
            if node.right is None:
                node.right = TreeNode(location)
            node.right.parcels.append(parcel) if location == node.right.location else self._insert_recursive(node.right, location, parcel)
    
    def search(self, location: str) -> List[Parcel]:
        """Search for parcels in location"""
        return self._search_recursive(self.root, location)
    
    def _search_recursive(self, node: Optional[TreeNode], location: str) -> List[Parcel]:
        if not node:
            return []
        if location == node.location:
            return node.parcels
        elif location < node.location:
            return self._search_recursive(node.left, location)
        else:
            return self._search_recursive(node.right, location)

class ParcelPriorityQueue:
    """Priority queue for delivery scheduling - Min/Max Heap
    
    Time Complexity: O(log n) for insertion/deletion, O(1) for peek
    Space Complexity: O(n)
    """
    def __init__(self):
        self.heap: List[Parcel] = []
    
    def enqueue(self, parcel: Parcel) -> None:
        """Add parcel to queue based on priority"""
        heapq.heappush(self.heap, parcel)
    
    def dequeue(self) -> Optional[Parcel]:
        """Remove and return highest priority parcel"""
        return heapq.heappop(self.heap) if self.heap else None
    
    def peek(self) -> Optional[Parcel]:
        """View highest priority without removing"""
        return self.heap[0] if self.heap else None
    
    def size(self) -> int:
        """Get queue size"""
        return len(self.heap)

class Graph:
    """Graph for route optimization using Dijkstra's algorithm
    
    Time Complexity: O((V + E) log V) for Dijkstra
    Space Complexity: O(V + E)
    """
    def __init__(self):
        self.graph: Dict[str, List[Tuple[str, float]]] = {}
    
    def add_edge(self, location1: str, location2: str, distance: float) -> None:
        """Add bidirectional edge"""
        if location1 not in self.graph:
            self.graph[location1] = []
        if location2 not in self.graph:
            self.graph[location2] = []
        self.graph[location1].append((location2, distance))
        self.graph[location2].append((location1, distance))
    
    def dijkstra(self, start: str, end: str) -> Tuple[float, List[str]]:
        """Find shortest path between locations"""
        distances = {node: float('inf') for node in self.graph}
        distances[start] = 0
        previous = {node: None for node in self.graph}
        unvisited = set(self.graph.keys())
        
        while unvisited:
            current = min(unvisited, key=lambda node: distances[node])
            if distances[current] == float('inf'):
                break
            
            for neighbor, weight in self.graph[current]:
                if neighbor in unvisited:
                    new_distance = distances[current] + weight
                    if new_distance < distances[neighbor]:
                        distances[neighbor] = new_distance
                        previous[neighbor] = current
            
            unvisited.remove(current)
        
        # Reconstruct path
        path = []
        current = end
        while current:
            path.insert(0, current)
            current = previous[current]
        
        return distances[end], path if path[0] == start else []
