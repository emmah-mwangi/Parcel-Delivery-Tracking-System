/**
 * DATA STRUCTURES MODULE
 * Implements: Array, Queue (FIFO), Stack (LIFO)
 */

// ============================================
// ARRAY - Store all parcels
// Time Complexity: Access O(1), Insert/Delete O(n)
// ============================================
class ParcelArray {
  constructor() {
    this.parcels = [];
  }

  add(parcel) {
    this.parcels.push(parcel);
  }

  getAll() {
    return this.parcels;
  }

  findByTrackingNumber(trackingNumber) {
    for (let i = 0; i < this.parcels.length; i++) {
      if (this.parcels[i].trackingNumber === trackingNumber) {
        return this.parcels[i];
      }
    }
    return null;
  }

  updateByTrackingNumber(trackingNumber, updates) {
    for (let i = 0; i < this.parcels.length; i++) {
      if (this.parcels[i].trackingNumber === trackingNumber) {
        this.parcels[i] = { ...this.parcels[i], ...updates };
        return true;
      }
    }
    return false;
  }

  deleteByTrackingNumber(trackingNumber) {
    this.parcels = this.parcels.filter(p => p.trackingNumber !== trackingNumber);
  }

  size() {
    return this.parcels.length;
  }
}

// ============================================
// QUEUE - Process parcels in FIFO order
// Operations: Enqueue O(1), Dequeue O(1)
// ============================================
class ParcelQueue {
  constructor() {
    this.queue = [];
  }

  // Add parcel to end of queue
  enqueue(parcel) {
    this.queue.push(parcel);
  }

  // Remove parcel from front of queue
  dequeue() {
    return this.queue.shift();
  }

  // View parcel at front without removing
  front() {
    return this.queue[0] || null;
  }

  isEmpty() {
    return this.queue.length === 0;
  }

  size() {
    return this.queue.length;
  }

  getAll() {
    return this.queue;
  }
}

// ============================================
// STACK - Maintain status history (LIFO)
// Operations: Push O(1), Pop O(1)
// ============================================
class StatusStack {
  constructor() {
    this.stack = [];
  }

  // Add status update to top
  push(status, timestamp) {
    this.stack.push({
      status: status,
      timestamp: timestamp
    });
  }

  // Remove and return top status
  pop() {
    return this.stack.pop();
  }

  // View top status without removing
  peek() {
    return this.stack[this.stack.length - 1] || null;
  }

  isEmpty() {
    return this.stack.length === 0;
  }

  size() {
    return this.stack.length;
  }

  getAll() {
    return this.stack;
  }
}
