"""
DATA STRUCTURES MODULE
=======================
Every structure below is hand-built (no dict/list used as a black box)
so the implementation can be explained and defended in the demo.

Structures implemented:
  1. HashTable      - O(1) average lookup of a parcel by tracking number
  2. ParcelQueue     - FIFO processing queue (deque-backed)
  3. StatusStack     - LIFO log of status changes, supports "undo"
  4. PriorityQueue   - min-heap; express/overnight parcels jump the queue
  5. Graph           - adjacency list of the town-to-town delivery network
"""

from collections import deque
import heapq
import itertools


# ============================================================
# 1. HASH TABLE
# Purpose : O(1) average lookup of a parcel by tracking number
# Design  : separate chaining (list of buckets, each bucket a list
#           of [key, value] pairs) so collisions are handled explicitly
# Time    : insert/search/delete -> O(1) average, O(n) worst case
# Space   : O(n)
# ============================================================
class HashTable:
    def __init__(self, capacity=101):  # 101 is prime -> fewer collisions
        self.capacity = capacity
        self.size = 0
        self.buckets = [[] for _ in range(self.capacity)]

    def _hash(self, key):
        # Sum the character codes then mod by capacity.
        total = sum(ord(ch) for ch in str(key))
        return total % self.capacity

    def set(self, key, value):
        index = self._hash(key)
        bucket = self.buckets[index]
        for pair in bucket:
            if pair[0] == key:
                pair[1] = value  # key exists -> overwrite
                return
        bucket.append([key, value])  # new key -> append to chain
        self.size += 1

    def get(self, key):
        index = self._hash(key)
        bucket = self.buckets[index]
        for pair in bucket:
            if pair[0] == key:
                return pair[1]
        return None

    def delete(self, key):
        index = self._hash(key)
        bucket = self.buckets[index]
        for i, pair in enumerate(bucket):
            if pair[0] == key:
                bucket.pop(i)
                self.size -= 1
                return True
        return False

    def contains(self, key):
        return self.get(key) is not None

    def rebuild(self, items, key_fn):
        """Clear and reload the table from an iterable of items."""
        self.buckets = [[] for _ in range(self.capacity)]
        self.size = 0
        for item in items:
            self.set(key_fn(item), item)


# ============================================================
# 2. QUEUE (FIFO)
# Purpose : holds parcels waiting to be dispatched, in arrival order
# Design  : wraps collections.deque so both ends are O(1)
# Time    : enqueue/dequeue/front -> O(1)
# Space   : O(n)
# ============================================================
class ParcelQueue:
    def __init__(self):
        self.items = deque()

    def enqueue(self, item):
        self.items.append(item)

    def dequeue(self):
        if self.is_empty():
            return None
        return self.items.popleft()

    def front(self):
        return self.items[0] if self.items else None

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

    def to_list(self):
        return list(self.items)


# ============================================================
# 3. STACK (LIFO)
# Purpose : logs every status change system-wide so the most recent
#           one can be "undone" (popped) during the demo
# Design  : wraps a plain Python list, push/pop at the end
# Time    : push/pop/peek -> O(1)
# Space   : O(n)
# ============================================================
class StatusStack:
    def __init__(self):
        self.items = []

    def push(self, entry):
        self.items.append(entry)

    def pop(self):
        if self.is_empty():
            return None
        return self.items.pop()

    def peek(self):
        return self.items[-1] if self.items else None

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

    def to_list(self):
        # Return newest-first, since that's how a stack is read
        return list(reversed(self.items))


# ============================================================
# 4. PRIORITY QUEUE (min-heap)
# Purpose : overnight/express parcels are dispatched before standard
#           ones, mirroring a real triage / boarding-priority system
# Design  : Python's heapq on tuples of (priority, sequence, parcel).
#           `sequence` is a tie-breaker so parcels with equal priority
#           still come out FIFO (heapq is not stable on its own, and
#           dict/parcel objects are not comparable).
# Time    : push/pop -> O(log n)
# Space   : O(n)
# ============================================================
PRIORITY_RANK = {'overnight': 1, 'express': 2, 'standard': 3}


class PriorityQueue:
    def __init__(self):
        self.heap = []
        self._counter = itertools.count()  # tie-breaker / insertion order

    def push(self, parcel, delivery_type='standard'):
        priority = PRIORITY_RANK.get(delivery_type, 3)
        entry = (priority, next(self._counter), parcel)
        heapq.heappush(self.heap, entry)

    def pop(self):
        if self.is_empty():
            return None
        _, _, parcel = heapq.heappop(self.heap)
        return parcel

    def peek(self):
        if self.is_empty():
            return None
        return self.heap[0][2]

    def is_empty(self):
        return len(self.heap) == 0

    def size(self):
        return len(self.heap)

    def to_ordered_list(self):
        """Non-destructive view of the queue in dispatch order."""
        return [entry[2] for entry in sorted(self.heap)]


# ============================================================
# 5. GRAPH (weighted, undirected)
# Purpose : represents the town-to-town delivery road network so the
#           shortest route/distance between two towns can be computed
# Design  : adjacency list -> {town: [(neighbour, distance_km), ...]}
# Time    : add_edge -> O(1)
# Space   : O(V + E)
# ============================================================
class Graph:
    def __init__(self):
        self.adjacency = {}

    def add_town(self, town):
        self.adjacency.setdefault(town, [])

    def add_edge(self, town_a, town_b, distance_km):
        self.add_town(town_a)
        self.add_town(town_b)
        self.adjacency[town_a].append((town_b, distance_km))
        self.adjacency[town_b].append((town_a, distance_km))

    def neighbours(self, town):
        return self.adjacency.get(town, [])

    def towns(self):
        return sorted(self.adjacency.keys())
