# Parcel Delivery Tracking System - Backend Implementation

## 🎯 Overview
Complete backend logic using **Vanilla JavaScript** and **Local Storage** with clear implementation of Data Structures and Algorithms for academic presentation.

---

## 📁 File Structure

```
frontend/
├── index.html              # Main UI (already complete)
├── styles.css              # Styling (enhanced)
├── app.js                  # Main application logic
├── dataStructures.js       # Array, Queue, Stack classes
├── algorithms.js           # Search & Sort algorithms
├── storage.js              # Local Storage operations
├── calculations.js         # Cost & statistics calculations
└── parcelManager.js        # Business logic
```

---

## 🏗️ Data Structures Implemented

### 1. **ARRAY - Store All Parcels**
```javascript
class ParcelArray {
  add(parcel)                           // O(1)
  getAll()                              // O(1)
  findByTrackingNumber(number)          // O(n) - Linear
  updateByTrackingNumber(number, data)  // O(n)
  deleteByTrackingNumber(number)        // O(n)
  size()                                // O(1)
}
```
- **Location**: `dataStructures.js`
- **Used for**: Storing all parcel objects
- **Access Pattern**: Direct array indexing

### 2. **QUEUE - Process Parcels (FIFO)**
```javascript
class ParcelQueue {
  enqueue(parcel)   // Add to end      O(1)
  dequeue()         // Remove from front O(1)
  front()           // View without removing
  isEmpty()
  size()
}
```
- **Location**: `dataStructures.js`
- **Used for**: Processing parcels in registration order
- **Example**: PK001 → PK002 → PK003
- **Status**: When parcel registered → added to queue

### 3. **STACK - Status History (LIFO)**
```javascript
class StatusStack {
  push(status, timestamp)   // Add to top      O(1)
  pop()                     // Remove from top O(1)
  peek()                    // View top
  getAll()                  // Get full history
}
```
- **Location**: `dataStructures.js`
- **Used for**: Maintaining parcel status history
- **Display Order**: Newest first (reverse chronological)
- **Example**: Delivered → Out For Delivery → In Transit → Registered

---

## 🔍 Algorithms Implemented

### 1. **LINEAR SEARCH**
```javascript
function linearSearch(parcels, fieldName, searchValue)
```
- **Time Complexity**: **O(n)**
- **Space Complexity**: O(1)
- **Location**: `algorithms.js`
- **Search Fields**:
  - Tracking Number
  - Sender Name
  - Sender Phone
  - Receiver Name
  - Receiver Phone
- **Process**: Check every parcel one by one

### 2. **BINARY SEARCH**
```javascript
function binarySearch(sortedParcels, trackingNumber)
```
- **Time Complexity**: **O(log n)**
- **Space Complexity**: O(1)
- **Location**: `algorithms.js`
- **Requirement**: Parcels must be sorted by tracking number
- **Process**:
  1. Divide search space in half
  2. Compare middle element
  3. Eliminate half of remaining elements
  4. Repeat until found

### 3. **BUBBLE SORT**
```javascript
function bubbleSort(parcels, fieldName)
```
- **Time Complexity**: **O(n²)**
- **Space Complexity**: O(1)
- **Location**: `algorithms.js`
- **Process**:
  1. Compare adjacent elements
  2. Swap if out of order
  3. Repeat n times
- **Use Case**: Educational demonstration

### 4. **SELECTION SORT**
```javascript
function selectionSort(parcels, fieldName)
```
- **Time Complexity**: **O(n²)**
- **Space Complexity**: O(1)
- **Location**: `algorithms.js`
- **Process**:
  1. Find minimum element
  2. Swap with current position
  3. Move to next position
  4. Repeat
- **Use Case**: Simple teaching example

### 5. **MERGE SORT**
```javascript
function mergeSort(parcels, fieldName)
function merge(left, right, fieldName)
```
- **Time Complexity**: **O(n log n)**
- **Space Complexity**: O(n)
- **Location**: `algorithms.js`
- **Process**:
  1. **Divide**: Split array in half
  2. **Conquer**: Recursively sort both halves
  3. **Combine**: Merge sorted halves
- **Use Case**: Efficient for larger datasets

---

## 📊 Features Implemented

### **Dashboard**
- ✅ Total Parcels count
- ✅ Registered count
- ✅ In Transit count
- ✅ Delivered count
- ✅ Delivery Rate: (Delivered ÷ Total × 100)
- ✅ Total Revenue: Sum of all costs

### **Register Parcel**
```
FORM FIELDS:
├── Sender Details
│   ├── Name (required)
│   ├── Phone
│   ├── Email
│   └── Pickup Location
├── Receiver Details
│   ├── Name (required)
│   ├── Phone
│   ├── Email
│   └── Delivery Location (required)
└── Parcel Details
    ├── Description
    ├── Weight (kg) (required)
    ├── Delivery Type (Standard/Express)
    └── Fragile (Yes/No)

AUTOMATIC ACTIONS:
→ Validate required fields
→ Calculate delivery cost
→ Generate unique tracking number (PK001, PK002...)
→ Set status to "Registered"
→ Record registration date/time
→ Create empty status history
→ Store in Local Storage
→ Add to processing queue
```

### **Track Parcel**
- ✅ Search by Tracking Number (Linear Search)
- ✅ Search by Sender Name (Linear Search)
- ✅ Search by Sender Phone (Linear Search)
- ✅ Search by Receiver Name (Linear Search)
- ✅ Search by Receiver Phone (Linear Search)
- ✅ Display tracking info
- ✅ Show status history (reversed chronological)

### **Manage Parcels**
**Table Display**:
- Tracking Number
- Sender
- Receiver
- Destination
- Status
- Cost

**Actions**:
- ✅ View (Shows full history)
- ✅ Update Status (Dropdown: Registered → Dispatched → In Transit → Out For Delivery → Delivered / Cancelled / Returned)
- ✅ Delete

**Sorting**:
- ✅ By Tracking Number
- ✅ By Destination
- ✅ By Status
- ✅ By Cost
- ✅ Choose Algorithm: Bubble Sort, Selection Sort, Merge Sort

### **Cost Calculator**
```
FORMULA:
Base Fee = 300 KSh
Weight Charge = Weight (kg) × 100
Express = +300 KSh (if Express)
Fragile = +200 KSh (if Fragile)

Total = Base + Weight + Express + Fragile

EXAMPLE:
Weight: 2.5 kg
Type: Express
Fragile: Yes

Calculation:
300 (base) + 250 (2.5×100) + 300 (express) + 200 (fragile) = 1050 KSh
```

### **Reports**
- ✅ Total Parcels
- ✅ Registered Parcels
- ✅ In Transit
- ✅ Delivered
- ✅ Cancelled
- ✅ Total Revenue
- ✅ Delivery Rate
- ✅ Most Common Destination
- ✅ Queue Status (Parcels waiting to process)
- ✅ Print Report
- ✅ Export to CSV

---

## 💾 Local Storage Schema

```javascript
// KEY: 'parcels' - Array of parcel objects
[
  {
    trackingNumber: "PK001",
    senderName: "John Doe",
    senderPhone: "0712345678",
    senderEmail: "john@example.com",
    pickupLocation: "Nairobi",
    receiverName: "Jane Smith",
    receiverPhone: "0787654321",
    receiverEmail: "jane@example.com",
    deliveryLocation: "Mombasa",
    parcelDescription: "Books",
    weight: 2.5,
    deliveryType: "express",
    isFragile: true,
    cost: 1050,
    status: "In Transit",
    registrationDate: "2026-07-04T10:30:00Z",
    statusHistory: [
      { status: "In Transit", timestamp: "2026-07-04T12:00:00Z" },
      { status: "Dispatched", timestamp: "2026-07-04T11:00:00Z" },
      { status: "Registered", timestamp: "2026-07-04T10:30:00Z" }
    ]
  }
]

// KEY: 'parcel_queue' - Array of tracking numbers (FIFO)
["PK001", "PK002", "PK003"]

// KEY: 'next_tracking_id' - Counter for tracking numbers
"4"
```

---

## 🚀 How to Use

### 1. **Initialize System**
```javascript
initStorage();  // Creates empty storage if not exists
```

### 2. **Register a Parcel**
```javascript
let result = createParcel({
  senderName: "John",
  receiverName: "Jane",
  deliveryLocation: "Mombasa",
  weight: 2.5,
  deliveryType: "express",
  isFragile: true
});
// Returns: { success: true, trackingNumber: "PK001", cost: 1050 }
```

### 3. **Track a Parcel**
```javascript
let info = trackParcel("PK001", "trackingNumber");
// Returns: { trackingNumber, sender, receiver, ... statusHistory }
```

### 4. **Update Status**
```javascript
updateParcelStatus("PK001", "Delivered");
// Automatically adds to status stack
```

### 5. **Sort Parcels**
```javascript
let sorted = sortParcels("merge", "trackingNumber");
// Choose: "bubble", "selection", or "merge"
```

### 6. **Get Statistics**
```javascript
let stats = getStatistics(getAllParcels());
// Returns: { totalParcels, registered, inTransit, delivered, deliveryRate, totalRevenue }
```

---

## 🎓 Perfect for Presentation

✅ **Simple & Minimalistic** - No frameworks, just vanilla JS
✅ **Well-Commented** - Every algorithm explains purpose, steps, complexity
✅ **Educational** - Clearly demonstrates DSA concepts
✅ **Interactive** - All features work in browser
✅ **Visual** - Dashboard updates in real-time
✅ **Modular** - Separate files for structures, algorithms, storage

---

## 📈 Time Complexity Summary

| Operation | Time | Space |
|-----------|------|-------|
| Add Parcel | O(1) | O(n) |
| Linear Search | O(n) | O(1) |
| Binary Search | O(log n) | O(1) |
| Bubble Sort | O(n²) | O(1) |
| Selection Sort | O(n²) | O(1) |
| Merge Sort | O(n log n) | O(n) |
| Queue (Enqueue/Dequeue) | O(1) | O(n) |
| Stack (Push/Pop) | O(1) | O(n) |

---

## ✨ Key Highlights

1. **No Backend Server** - Everything runs in browser using Local Storage
2. **Persistent Data** - Survives page refresh
3. **Zero Dependencies** - Pure JavaScript
4. **Educational Value** - Perfect demonstration of DSA
5. **Easy to Explain** - Step-by-step commented code
6. **Production Ready** - Fully functional system

---

## 🔧 Testing Checklist

- [ ] Register a parcel → Check dashboard updates
- [ ] Search by different fields → Verify linear search works
- [ ] Update parcel status → Confirm stack pushes new status
- [ ] Sort by different fields → Test all 3 algorithms
- [ ] Calculate cost → Verify formula
- [ ] Export to CSV → Check data integrity
- [ ] Clear browser storage → Initialize fresh system

---

## 📝 Notes

- **Tracking Numbers**: Auto-generated as PK001, PK002, etc.
- **Statuses**: Registered → Dispatched → In Transit → Out For Delivery → Delivered (or Cancelled/Returned)
- **Cost Formula**: Designed to be simple yet realistic
- **Queue**: Automatically processes parcels in registration order
- **History**: Stack maintains full audit trail in reverse chronological order

---

**Built with ❤️ for Academic Excellence**
