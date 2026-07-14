"""Parcel Reports Module - Generate reports with sorting"""
from typing import List

class ParcelReports:
    """Generates reports using Bubble Sort and Selection Sort
    
    Time Complexity:
    - bubble_sort: O(n^2)
    - selection_sort: O(n^2)
    - get_all_parcels: O(n)
    
    Space Complexity: O(n) for sorting arrays
    """
    
    def __init__(self, registration_module, management_module):
        """Initialize reports with modules"""
        self.registration = registration_module
        self.management = management_module
    
    def bubble_sort_by_weight(self, reverse=False) -> List:
        """Sort parcels by weight using Bubble Sort - O(n^2)"""
        parcels = self.registration.get_all_parcels()
        arr = parcels.copy()
        n = len(arr)
        
        # Bubble sort
        for i in range(n):
            for j in range(0, n - i - 1):
                if reverse:
                    if arr[j].weight < arr[j + 1].weight:
                        arr[j], arr[j + 1] = arr[j + 1], arr[j]
                else:
                    if arr[j].weight > arr[j + 1].weight:
                        arr[j], arr[j + 1] = arr[j + 1], arr[j]
        
        return arr
    
    def selection_sort_by_destination(self) -> List:
        """Sort parcels by destination using Selection Sort - O(n^2)"""
        parcels = self.registration.get_all_parcels()
        arr = parcels.copy()
        n = len(arr)
        
        # Selection sort
        for i in range(n):
            min_idx = i
            for j in range(i + 1, n):
                if arr[j].destination < arr[min_idx].destination:
                    min_idx = j
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
        
        return arr
    
    def bubble_sort_by_cost(self, reverse=False) -> List:
        """Sort parcels by cost using Bubble Sort - O(n^2)"""
        parcels = self.registration.get_all_parcels()
        arr = parcels.copy()
        n = len(arr)
        
        for i in range(n):
            for j in range(0, n - i - 1):
                if reverse:
                    if arr[j].cost < arr[j + 1].cost:
                        arr[j], arr[j + 1] = arr[j + 1], arr[j]
                else:
                    if arr[j].cost > arr[j + 1].cost:
                        arr[j], arr[j + 1] = arr[j + 1], arr[j]
        
        return arr
    
    def get_all_parcels_report(self) -> List:
        """Get all parcels as report - O(n)"""
        parcels = self.registration.get_all_parcels()
        return [{
            'tracking_id': p.tracking_id,
            'sender': p.sender,
            'receiver': p.receiver,
            'origin': p.origin,
            'destination': p.destination,
            'weight': p.weight,
            'status': p.status,
            'cost': p.cost
        } for p in parcels]
    
    def get_report_by_weight(self, ascending=True) -> List:
        """Get report sorted by weight - O(n^2)"""
        sorted_parcels = self.bubble_sort_by_weight(reverse=not ascending)
        return [{
            'tracking_id': p.tracking_id,
            'receiver': p.receiver,
            'weight': p.weight,
            'destination': p.destination
        } for p in sorted_parcels]
    
    def get_report_by_destination(self) -> List:
        """Get report sorted by destination - O(n^2)"""
        sorted_parcels = self.selection_sort_by_destination()
        return [{
            'tracking_id': p.tracking_id,
            'destination': p.destination,
            'receiver': p.receiver,
            'status': p.status
        } for p in sorted_parcels]
    
    def get_delivery_statistics(self) -> dict:
        """Get delivery statistics - O(n)"""
        parcels = self.registration.get_all_parcels()
        
        total = len(parcels)
        registered = sum(1 for p in parcels if p.status == "Registered")
        dispatched = sum(1 for p in parcels if p.status == "Dispatched")
        in_transit = sum(1 for p in parcels if p.status == "In Transit")
        out_for_delivery = sum(1 for p in parcels if p.status == "Out For Delivery")
        delivered = sum(1 for p in parcels if p.status == "Delivered")
        cancelled = sum(1 for p in parcels if p.status == "Cancelled")
        
        total_weight = sum(p.weight for p in parcels)
        total_revenue = sum(p.cost for p in parcels)
        avg_weight = total_weight / total if total > 0 else 0
        avg_cost = total_revenue / total if total > 0 else 0
        
        return {
            'total_parcels': total,
            'registered': registered,
            'dispatched': dispatched,
            'in_transit': in_transit,
            'out_for_delivery': out_for_delivery,
            'delivered': delivered,
            'cancelled': cancelled,
            'total_weight': round(total_weight, 2),
            'total_revenue': round(total_revenue, 2),
            'average_weight': round(avg_weight, 2),
            'average_cost': round(avg_cost, 2)
        }
    
    def get_report_by_status(self, status: str) -> List:
        """Get parcels filtered by status - O(n)"""
        parcels = self.registration.get_all_parcels()
        filtered = [p for p in parcels if p.status == status]
        
        return [{
            'tracking_id': p.tracking_id,
            'receiver': p.receiver,
            'destination': p.destination,
            'weight': p.weight,
            'cost': p.cost
        } for p in filtered]
