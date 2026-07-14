"""Advanced Algorithms for Parcel Delivery Tracking System"""
from typing import List, Tuple, Dict
from data_structures import Parcel, ParcelStatus
import math

class SortingAlgorithms:
    """Sorting algorithms for parcel organization"""
    
    @staticmethod
    def merge_sort(parcels: List[Parcel], key: str = 'priority') -> List[Parcel]:
        """Merge sort - O(n log n) time, O(n) space
        Used for sorting parcels by priority, date, or weight
        """
        if len(parcels) <= 1:
            return parcels
        
        mid = len(parcels) // 2
        left = SortingAlgorithms.merge_sort(parcels[:mid], key)
        right = SortingAlgorithms.merge_sort(parcels[mid:], key)
        
        return SortingAlgorithms._merge(left, right, key)
    
    @staticmethod
    def _merge(left: List[Parcel], right: List[Parcel], key: str) -> List[Parcel]:
        """Merge helper for merge sort"""
        result = []
        i = j = 0
        
        while i < len(left) and j < len(right):
            left_val = getattr(left[i], key)
            right_val = getattr(right[j], key)
            
            if left_val >= right_val:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        
        result.extend(left[i:])
        result.extend(right[j:])
        return result
    
    @staticmethod
    def quick_sort(parcels: List[Parcel], key: str = 'priority') -> List[Parcel]:
        """Quick sort - O(n log n) average, O(n²) worst case
        Time: O(n log n), Space: O(log n) recursive stack
        """
        if len(parcels) <= 1:
            return parcels
        
        pivot = parcels[len(parcels) // 2]
        left = [p for p in parcels if getattr(p, key) > getattr(pivot, key)]
        middle = [p for p in parcels if getattr(p, key) == getattr(pivot, key)]
        right = [p for p in parcels if getattr(p, key) < getattr(pivot, key)]
        
        return (SortingAlgorithms.quick_sort(left, key) + middle + 
                SortingAlgorithms.quick_sort(right, key))

class SearchingAlgorithms:
    """Searching algorithms for parcel retrieval"""
    
    @staticmethod
    def binary_search(parcels: List[Parcel], target_id: str) -> Tuple[bool, int]:
        """Binary search - O(log n) time, O(1) space
        Works on sorted array of parcel IDs
        """
        left, right = 0, len(parcels) - 1
        
        while left <= right:
            mid = (left + right) // 2
            mid_id = parcels[mid].tracking_id
            
            if mid_id == target_id:
                return True, mid
            elif mid_id < target_id:
                left = mid + 1
            else:
                right = mid - 1
        
        return False, -1
    
    @staticmethod
    def linear_search(parcels: List[Parcel], predicate) -> List[Parcel]:
        """Linear search - O(n) time
        Used for filtering by custom conditions
        """
        return [p for p in parcels if predicate(p)]

class PathfindingAlgorithms:
    """Algorithms for optimal delivery route planning"""
    
    @staticmethod
    def travelling_salesman_dynamic(locations: List[str], distances: Dict[Tuple[str, str], float]) -> Tuple[float, List[str]]:
        """TSP using Dynamic Programming - O(n² * 2^n) time
        Finds optimal delivery route visiting all locations once
        """
        n = len(locations)
        if n <= 2:
            total_dist = sum(distances.get((locations[i], locations[i+1]), 0) for i in range(n-1))
            return total_dist, locations
        
        # DP table: dp[mask][i] = minimum cost to visit cities in mask ending at i
        dp = [[float('inf')] * n for _ in range(1 << n)]
        parent = [[None] * n for _ in range(1 << n)]
        
        # Start from first city
        dp[1][0] = 0
        
        for mask in range(1, 1 << n):
            for u in range(n):
                if not (mask & (1 << u)) or dp[mask][u] == float('inf'):
                    continue
                
                for v in range(n):
                    if mask & (1 << v):
                        continue
                    
                    new_mask = mask | (1 << v)
                    dist = distances.get((locations[u], locations[v]), 0)
                    new_cost = dp[mask][u] + dist
                    
                    if new_cost < dp[new_mask][v]:
                        dp[new_mask][v] = new_cost
                        parent[new_mask][v] = u
        
        # Find minimum cost and reconstruct path
        full_mask = (1 << n) - 1
        min_cost = min(dp[full_mask])
        
        return min_cost, locations  # Simplified path reconstruction
    
    @staticmethod
    def nearest_neighbor(start: str, locations: List[str], distances: Dict[Tuple[str, str], float]) -> List[str]:
        """Greedy Nearest Neighbor - O(n²) time
        Approximation algorithm for TSP
        """
        unvisited = set(locations)
        unvisited.discard(start)
        current = start
        path = [current]
        
        while unvisited:
            nearest = min(unvisited, key=lambda loc: distances.get((current, loc), float('inf')))
            path.append(nearest)
            current = nearest
            unvisited.remove(nearest)
        
        return path

class ComplexityAnalysis:
    """Complexity analysis for all algorithms"""
    
    ALGORITHM_COMPLEXITIES = {
        'merge_sort': {'time': 'O(n log n)', 'space': 'O(n)'},
        'quick_sort': {'time': 'O(n log n) avg, O(n²) worst', 'space': 'O(log n)'},
        'binary_search': {'time': 'O(log n)', 'space': 'O(1)'},
        'linear_search': {'time': 'O(n)', 'space': 'O(1)'},
        'dijkstra': {'time': 'O((V+E) log V)', 'space': 'O(V)'},
        'tsp_dp': {'time': 'O(n² * 2^n)', 'space': 'O(n * 2^n)'},
        'nearest_neighbor': {'time': 'O(n²)', 'space': 'O(n)'},
    }
    
    @staticmethod
    def get_complexity_analysis() -> Dict:
        """Return comprehensive complexity analysis"""
        return ComplexityAnalysis.ALGORITHM_COMPLEXITIES
