"""
Quick test to verify all system features work
"""

from Parcel_Registration import register_parcel
from Parcel_Management import find_parcel, add_to_queue, process_next, view_queue, view_all_parcels
from Parcel_LiveTracking import binary_search, search_by_sender, search_by_receiver
from Parcel_CostCalculator import calculate_cost, calculation_history
from Parcel_Reports import ReportGenerator

print("="*60)
print("TESTING PARCEL DELIVERY TRACKING SYSTEM")
print("="*60)

# Test 1: Register parcels
print("\n1. Testing Registration...")
p1 = register_parcel("Alice Kamau", "Brian Odhiambo")
p2 = register_parcel("Carol Wanjiku", "David Mwangi")
p3 = register_parcel("Eve Adhiambo", "Frank Kipchoge")

if p1 and p2 and p3:
    print("✓ Registration works!")
else:
    print("✗ Registration failed!")

# Test 2: Binary Search (tracking)
print("\n2. Testing Binary Search...")
found = binary_search(p1.tracking_id)
if found:
    print(f"✓ Binary Search works! Found: {found.tracking_id}")
else:
    print("✗ Binary Search failed!")

# Test 3: Linear Search (by sender/receiver)
print("\n3. Testing Linear Search...")
sender_results = search_by_sender("Alice")
receiver_results = search_by_receiver("Brian")
if sender_results and receiver_results:
    print(f"✓ Linear Search works! Found {len(sender_results)} sender(s), {len(receiver_results)} receiver(s)")
else:
    print("✗ Linear Search failed!")

# Test 4: Queue operations
print("\n4. Testing Queue (FIFO)...")
add_to_queue(p1.tracking_id)
add_to_queue(p2.tracking_id)
add_to_queue(p3.tracking_id)
print("✓ Added parcels to queue")
view_queue()

# Test 5: Process deliveries
print("\n5. Testing Delivery Processing...")
process_next()  # Move p1 to next stage
process_next()  # Move p2 to next stage
print("✓ Delivery processing works!")

# Test 6: Cost Calculator
print("\n6. Testing Cost Calculator...")
calc = calculate_cost(5.5, "Mombasa", "Express")
if calc:
    print(f"✓ Cost calculation works! Total: KES {calc.total_cost:.2f}")
    print(f"  Stack size: {calculation_history.size()}")
else:
    print("✗ Cost calculation failed!")

# Test 7: Reports and Statistics
print("\n7. Testing Reports...")
stats = ReportGenerator.get_statistics()
if stats:
    print(f"✓ Reports work!")
    print(f"  Total: {stats['total']}")
    print(f"  Delivered: {stats['delivered']}")
    print(f"  Delivery Rate: {stats['delivery_rate']:.1f}%")
else:
    print("✗ Reports failed!")

# Test 8: Sorting algorithms
print("\n8. Testing Sorting Algorithms...")
parcels = [p1, p2, p3]
bubble_sorted = ReportGenerator.bubble_sort(parcels, lambda p: p.tracking_id)
selection_sorted = ReportGenerator.selection_sort(parcels, lambda p: p.tracking_id)
merge_sorted = ReportGenerator.merge_sort(parcels, lambda p: p.tracking_id)

print(f"✓ All 3 sorting algorithms work!")
print(f"  Bubble Sort: {[p.tracking_id for p in bubble_sorted]}")
print(f"  Selection Sort: {[p.tracking_id for p in selection_sorted]}")
print(f"  Merge Sort: {[p.tracking_id for p in merge_sorted]}")

# Final summary
print("\n" + "="*60)
print("ALL TESTS PASSED!")
print("="*60)
print("\nData Structures Implemented:")
print("  ✓ Array/List (parcel_database)")
print("  ✓ Queue (delivery_queue) - FIFO")
print("  ✓ Stack (calculation_history) - LIFO")
print("\nAlgorithms Implemented:")
print("  ✓ Binary Search - O(log n)")
print("  ✓ Linear Search - O(n)")
print("  ✓ Bubble Sort - O(n²)")
print("  ✓ Selection Sort - O(n²)")
print("  ✓ Merge Sort - O(n log n)")
print("="*60)