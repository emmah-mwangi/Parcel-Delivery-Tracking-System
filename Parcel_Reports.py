"""
5. Parcel_Reports.py
Responsibilities
Display all parcel records
Generate delivery reports
Sort parcels by weight
Sort parcels by destination
Show delivery statistics
DSA to Use
Bubble Sort
Selection Sort
Array/List
"""

from datetime import datetime
from Parcel_Management import parcel_database, DELIVERY_STAGES

class ReportGenerator:
    """Generate various reports with sorting algorithms"""
    
    @staticmethod
    def bubble_sort(parcels, key_func, reverse=False):
        """
        Bubble Sort - for sorting parcel records
        Time Complexity  : O(n²) - worst/average case
        Space Complexity : O(1)
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
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    swapped = True
            
            if not swapped:
                break
        
        return arr
    
    @staticmethod
    def selection_sort(parcels, key_func, reverse=False):
        """
        Selection Sort - alternative sorting algorithm
        Time Complexity  : O(n²)
        Space Complexity : O(1)
        """
        arr = parcels.copy()
        n = len(arr)
        
        for i in range(n):
            # Find minimum/maximum
            extreme_idx = i
            for j in range(i + 1, n):
                if reverse:
                    if key_func(arr[j]) > key_func(arr[extreme_idx]):
                        extreme_idx = j
                else:
                    if key_func(arr[j]) < key_func(arr[extreme_idx]):
                        extreme_idx = j
            
            arr[i], arr[extreme_idx] = arr[extreme_idx], arr[i]
        
        return arr
    
    @staticmethod
    def get_statistics():
        """Get statistics data"""
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
