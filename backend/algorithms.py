"""
ALGORITHMS MODULE
==================
Implements: Linear Search, Binary Search, Bubble Sort, Selection Sort,
Merge Sort, and Dijkstra's Shortest Path.

All functions take/return plain dicts (parcels) or a Graph (see
data_structures.py) so they can be called directly from the Flask
routes in app.py and their result shown in the UI.
"""

import heapq


# ============================================================
# LINEAR SEARCH
# Purpose : find a parcel by scanning every record - works on any
#           field, sorted or not
# Time    : O(n)
# Space   : O(1)
# ============================================================
def linear_search(parcels, field, value):
    for parcel in parcels:
        if str(parcel.get(field, '')).lower() == str(value).lower():
            return parcel
    return None


# ============================================================
# BINARY SEARCH
# Purpose : fast lookup once parcels are sorted by the search field
# Time    : O(log n)
# Space   : O(1)
# Note    : caller must pass a list already sorted (ascending) on
#           `field` - see merge_sort() below.
# ============================================================
def binary_search(sorted_parcels, field, value):
    left, right = 0, len(sorted_parcels) - 1
    target = str(value).lower()

    while left <= right:
        mid = (left + right) // 2
        mid_value = str(sorted_parcels[mid].get(field, '')).lower()

        if mid_value == target:
            return sorted_parcels[mid]
        elif mid_value < target:
            left = mid + 1
        else:
            right = mid - 1
    return None


# ============================================================
# BUBBLE SORT
# Purpose : simple comparison sort, kept for the algorithm defense
# Time    : O(n^2)
# Space   : O(1) extra (sorts a copy, in place)
# ============================================================
def bubble_sort(parcels, field, reverse=False):
    arr = list(parcels)
    n = len(arr)
    for i in range(n - 1):
        for j in range(n - i - 1):
            should_swap = arr[j][field] > arr[j + 1][field]
            if reverse:
                should_swap = arr[j][field] < arr[j + 1][field]
            if should_swap:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr


# ============================================================
# SELECTION SORT
# Purpose : second simple comparison sort, for side-by-side comparison
# Time    : O(n^2)
# Space   : O(1) extra
# ============================================================
def selection_sort(parcels, field, reverse=False):
    arr = list(parcels)
    n = len(arr)
    for i in range(n - 1):
        target_index = i
        for j in range(i + 1, n):
            better = arr[j][field] < arr[target_index][field]
            if reverse:
                better = arr[j][field] > arr[target_index][field]
            if better:
                target_index = j
        if target_index != i:
            arr[i], arr[target_index] = arr[target_index], arr[i]
    return arr


# ============================================================
# MERGE SORT
# Purpose : efficient divide-and-conquer sort, used to prepare the
#           list for binary_search() above
# Time    : O(n log n)
# Space   : O(n)
# ============================================================
def merge_sort(parcels, field, reverse=False):
    if len(parcels) <= 1:
        return list(parcels)

    mid = len(parcels) // 2
    left = merge_sort(parcels[:mid], field, reverse)
    right = merge_sort(parcels[mid:], field, reverse)
    return _merge(left, right, field, reverse)


def _merge(left, right, field, reverse):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        take_left = left[i][field] <= right[j][field]
        if reverse:
            take_left = left[i][field] >= right[j][field]
        if take_left:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


# ============================================================
# DIJKSTRA'S SHORTEST PATH
# Purpose : find the shortest road distance between two towns in the
#           delivery network (Graph from data_structures.py); the
#           result feeds the cost calculator's distance_km figure
# Time    : O((V + E) log V) with a binary heap as the priority queue
# Space   : O(V)
# ============================================================
def dijkstra(graph, start, end):
    if start not in graph.adjacency or end not in graph.adjacency:
        return None, float('inf')

    distances = {town: float('inf') for town in graph.adjacency}
    previous = {town: None for town in graph.adjacency}
    distances[start] = 0

    visited = set()
    heap = [(0, start)]

    while heap:
        current_distance, current_town = heapq.heappop(heap)
        if current_town in visited:
            continue
        visited.add(current_town)

        if current_town == end:
            break

        for neighbour, weight in graph.neighbours(current_town):
            new_distance = current_distance + weight
            if new_distance < distances[neighbour]:
                distances[neighbour] = new_distance
                previous[neighbour] = current_town
                heapq.heappush(heap, (new_distance, neighbour))

    if distances[end] == float('inf'):
        return None, float('inf')

    # Walk the `previous` chain backwards to rebuild the path
    path = []
    node = end
    while node is not None:
        path.append(node)
        node = previous[node]
    path.reverse()

    return path, distances[end]
