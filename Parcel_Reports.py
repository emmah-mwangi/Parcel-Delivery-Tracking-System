"""
PARCEL REPORTS MODULE
=====================

This module generates reports and sorts parcel data.

SORTING ALGORITHMS USED:
1. Bubble Sort - O(n²)
   - Simple sorting algorithm
   - Repeatedly swaps adjacent elements
   - Easy to understand and implement

2. Selection Sort - O(n²)
   - Finds minimum element and places it
   - Simple but not very efficient
   - Good for small datasets

3. Merge Sort - O(n log n)
   - Divide and conquer algorithm
   - Splits list in half, sorts each half, merges
   - Much faster for large datasets

DATA STRUCTURES:
- Array/List (parcel_database): Stores parcels for sorting
"""

from parcel_core import parcel_database, DELIVERY_STAGES

class ReportGenerator:
    """Generate reports with sorting algorithms"""
    
    # ========== BUBBLE SORT ==========
    
    @staticmethod
    def bubble_sort(parcels, key_func, reverse=False):
        """
        Sort parcels using BUBBLE SORT algorithm.
        
        Algorithm: Bubble Sort
        - Compare adjacent elements
        - Swap if they're in wrong order
        - Repeat until no swaps needed
        
        Time Complexity: O(n²) - slow for large lists
        Space Complexity: O(1) - sorts in place
        
        Example:
            [5, 2, 8, 1]
            Pass 1: [2, 5, 1, 8] (8 bubbled to end)
            Pass 2: [2, 1, 5, 8] (5 bubbled to position)
            Pass 3: [1, 2, 5, 8] (sorted!)
        """
        n = len(parcels)
        arr = parcels.copy()
        
        for i in range(n):
            swapped = False
            for j in range(0, n - i - 1):
                # Compare using key_func
                if reverse:
                    condition = key_func(arr[j]) < key_func(arr[j + 1])
                else:
                    condition = key_func(arr[j]) > key_func(arr[j + 1])
                
                if condition:
                    # Swap elements
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    swapped = True
            
            # If no swaps, list is sorted
            if not swapped:
                break
        
        return arr
    
    # ========== SELECTION SORT ==========
    
    @staticmethod
    def selection_sort(parcels, key_func, reverse=False):
        """
        Sort parcels using SELECTION SORT algorithm.
        
        Algorithm: Selection Sort
        - Find minimum/maximum element
        - Place it at the beginning
        - Repeat for remaining elements
        
        Time Complexity: O(n²)
        Space Complexity: O(1)
        
        Example:
            [5, 2, 8, 1]
            Pass 1: [1, 5, 8, 2] (1 is minimum, swap with first)
            Pass 2: [1, 2, 8, 5] (2 is minimum of rest, swap)
            Pass 3: [1, 2, 5, 8] (sorted!)
        """
        arr = parcels.copy()
        n = len(arr)
        
        for i in range(n):
            # Find minimum/maximum in unsorted part
            extreme_idx = i
            for j in range(i + 1, n):
                if reverse:
                    if key_func(arr[j]) > key_func(arr[extreme_idx]):
                        extreme_idx = j
                else:
                    if key_func(arr[j]) < key_func(arr[extreme_idx]):
                        extreme_idx = j
            
            # Swap with current position
            arr[i], arr[extreme_idx] = arr[extreme_idx], arr[i]
        
        return arr
    
    # ========== MERGE SORT ==========
    
    @staticmethod
    def merge_sort(parcels, key_func, reverse=False):
        """
        Sort parcels using MERGE SORT algorithm.
        
        Algorithm: Merge Sort
        - Divide list into two halves
        - Recursively sort each half
        - Merge the sorted halves
        
        Time Complexity: O(n log n) - fast!
        Space Complexity: O(n) - needs extra space
        
        Example:
            [5, 2, 8, 1]
            Divide: [5, 2] and [8, 1]
            Sort: [2, 5] and [1, 8]
            Merge: [1, 2, 5, 8]
        """
        if len(parcels) <= 1:
            return parcels.copy()
        
        # Divide
        mid = len(parcels) // 2
        left = ReportGenerator.merge_sort(parcels[:mid], key_func, reverse)
        right = ReportGenerator.merge_sort(parcels[mid:], key_func, reverse)
        
        # Merge
        return ReportGenerator._merge(left, right, key_func, reverse)
    
    @staticmethod
    def _merge(left, right, key_func, reverse):
        """Helper function to merge two sorted lists"""
        result = []
        i = j = 0
        
        while i < len(left) and j < len(right):
            if reverse:
                if key_func(left[i]) >= key_func(right[j]):
                    result.append(left[i])
                    i += 1
                else:
                    result.append(right[j])
                    j += 1
            else:
                if key_func(left[i]) <= key_func(right[j]):
                    result.append(left[i])
                    i += 1
                else:
                    result.append(right[j])
                    j += 1
        
        # Add remaining elements
        result.extend(left[i:])
        result.extend(right[j:])
        
        return result
    
    # ========== STATISTICS ==========
    
    @staticmethod
    def get_statistics():
        """Get delivery statistics"""
        if not parcel_database:
            return None
        
        total = len(parcel_database)
        registered = sum(1 for p in parcel_database if p.status == "Registered")
        picked_up = sum(1 for p in parcel_database if p.status == "Picked Up")
        in_transit = sum(1 for p in parcel_database if p.status == "In Transit")
        out_for_delivery = sum(1 for p in parcel_database if p.status == "Out for Delivery")
        delivered = sum(1 for p in parcel_database if p.status == "Delivered")
        
        return {
            "total": total,
            "registered": registered,
            "picked_up": picked_up,
            "in_transit": in_transit,
            "out_for_delivery": out_for_delivery,
            "delivered": delivered,
            "delivery_rate": (delivered/total*100) if total > 0 else 0
        }
    
    @staticmethod
    def get_all_parcels_data():
        """Get all parcels data for API"""
        if not parcel_database:
            return []
        
        return [{
            "tracking_id": p.tracking_id,
            "sender": p.sender,
            "receiver": p.receiver,
            "status": p.status,
            "registered_date": p.history[0][1] if p.history else None,
            "latest_date": p.history[-1][1] if len(p.history) > 0 else None,
            "latest_status": p.history[-1][0] if len(p.history) > 0 else p.status
        } for p in parcel_database]