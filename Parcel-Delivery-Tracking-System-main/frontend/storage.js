/**
 * LOCAL STORAGE MODULE
 * Handles all data persistence using browser's Local Storage
 */

const STORAGE_KEY = 'parcels';
const QUEUE_KEY = 'parcel_queue';
const NEXT_ID_KEY = 'next_tracking_id';

// ============================================
// INITIALIZATION
// ============================================
function initStorage() {
  // Initialize next tracking ID if not exists
  if (!localStorage.getItem(NEXT_ID_KEY)) {
    localStorage.setItem(NEXT_ID_KEY, '1');
  }

  // Initialize parcels array if not exists
  if (!localStorage.getItem(STORAGE_KEY)) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify([]));
  }

  // Initialize queue if not exists
  if (!localStorage.getItem(QUEUE_KEY)) {
    localStorage.setItem(QUEUE_KEY, JSON.stringify([]));
  }
}

// ============================================
// PARCEL OPERATIONS
// ============================================

// Get all parcels from Local Storage
function getAllParcels() {
  return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
}

// Save all parcels to Local Storage
function saveParcels(parcels) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(parcels));
}

// Add new parcel
function addParcel(parcel) {
  let parcels = getAllParcels();
  parcels.push(parcel);
  saveParcels(parcels);
}

// Find parcel by tracking number
function findParcel(trackingNumber) {
  let parcels = getAllParcels();
  return parcels.find(p => p.trackingNumber === trackingNumber) || null;
}

// Update parcel
function updateParcel(trackingNumber, updates) {
  let parcels = getAllParcels();
  let index = parcels.findIndex(p => p.trackingNumber === trackingNumber);
  if (index !== -1) {
    parcels[index] = { ...parcels[index], ...updates };
    saveParcels(parcels);
    return true;
  }
  return false;
}

// Delete parcel
function deleteParcel(trackingNumber) {
  let parcels = getAllParcels();
  parcels = parcels.filter(p => p.trackingNumber !== trackingNumber);
  saveParcels(parcels);
}

// ============================================
// TRACKING NUMBER GENERATION
// ============================================
function generateTrackingNumber() {
  let id = parseInt(localStorage.getItem(NEXT_ID_KEY));
  localStorage.setItem(NEXT_ID_KEY, String(id + 1));
  return 'PK' + String(id).padStart(3, '0');
}

// ============================================
// QUEUE OPERATIONS
// ============================================

// Get all queued parcels
function getQueue() {
  return JSON.parse(localStorage.getItem(QUEUE_KEY) || '[]');
}

// Save queue
function saveQueue(queue) {
  localStorage.setItem(QUEUE_KEY, JSON.stringify(queue));
}

// Add parcel to queue (FIFO - add to end)
function enqueueParcel(trackingNumber) {
  let queue = getQueue();
  queue.push(trackingNumber);
  saveQueue(queue);
}

// Remove parcel from queue (FIFO - remove from front)
function dequeueParcel() {
  let queue = getQueue();
  let trackingNumber = queue.shift();
  saveQueue(queue);
  return trackingNumber;
}

// View front of queue without removing
function peekQueue() {
  let queue = getQueue();
  return queue[0] || null;
}

// ============================================
// CLEAR ALL DATA (for testing)
// ============================================
function clearAllData() {
  localStorage.removeItem(STORAGE_KEY);
  localStorage.removeItem(QUEUE_KEY);
  localStorage.removeItem(NEXT_ID_KEY);
  initStorage();
}
