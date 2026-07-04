/**
 * PARCEL MANAGER MODULE
 * Handles all parcel operations and business logic
 */

// Initialize storage on load
iniStorage();

// ============================================
// PARCEL CREATION
// ============================================
function createParcel(data) {
  // Validate required fields
  if (!data.senderName || !data.receiverName || !data.deliveryLocation || !data.weight) {
    return { error: 'Missing required fields' };
  }

  // Generate tracking number
  let trackingNumber = generateTrackingNumber();

  // Calculate cost
  let cost = calculateDeliveryCost(
    parseFloat(data.weight),
    data.deliveryType || 'standard',
    data.isFragile === true || data.isFragile === 'on'
  );

  // Create parcel object
  let parcel = {
    trackingNumber: trackingNumber,
    senderName: data.senderName,
    senderPhone: data.senderPhone || '',
    senderEmail: data.senderEmail || '',
    pickupLocation: data.pickupLocation || '',
    receiverName: data.receiverName,
    receiverPhone: data.receiverPhone || '',
    receiverEmail: data.receiverEmail || '',
    deliveryLocation: data.deliveryLocation,
    parcelDescription: data.parcelDescription || '',
    weight: parseFloat(data.weight),
    deliveryType: data.deliveryType || 'standard',
    isFragile: data.isFragile === true || data.isFragile === 'on',
    cost: cost,
    status: 'Registered',
    registrationDate: new Date().toISOString(),
    statusHistory: [
      {
        status: 'Registered',
        timestamp: new Date().toISOString()
      }
    ]
  };

  // Save to storage
  addParcel(parcel);

  // Add to queue for processing
  enqueueParcel(trackingNumber);

  return { success: true, trackingNumber: trackingNumber, cost: cost };
}

// ============================================
// PARCEL TRACKING
// ============================================
function trackParcel(searchValue, searchType = 'trackingNumber') {
  let parcels = getAllParcels();

  // Use linear search for most fields
  let fieldMap = {
    'trackingNumber': 'trackingNumber',
    'senderName': 'senderName',
    'senderPhone': 'senderPhone',
    'receiverName': 'receiverName',
    'receiverPhone': 'receiverPhone'
  };

  let fieldName = fieldMap[searchType] || 'trackingNumber';
  let parcel = linearSearch(parcels, fieldName, searchValue);

  if (!parcel) {
    return { error: 'Parcel not found' };
  }

  // Format for display
  return {
    trackingNumber: parcel.trackingNumber,
    sender: parcel.senderName + ' (' + parcel.senderPhone + ')',
    receiver: parcel.receiverName + ' (' + parcel.receiverPhone + ')',
    deliveryLocation: parcel.deliveryLocation,
    currentStatus: parcel.status,
    cost: formatCost(parcel.cost),
    registrationDate: new Date(parcel.registrationDate).toLocaleDateString(),
    statusHistory: parcel.statusHistory
  };
}

// ============================================
// UPDATE PARCEL STATUS
// ============================================
function updateParcelStatus(trackingNumber, newStatus) {
  let parcel = findParcel(trackingNumber);
  if (!parcel) {
    return { error: 'Parcel not found' };
  }

  // Update status
  parcel.status = newStatus;

  // Add to status history (stack - push operation)
  if (!parcel.statusHistory) {
    parcel.statusHistory = [];
  }
  parcel.statusHistory.push({
    status: newStatus,
    timestamp: new Date().toISOString()
  });

  // Save updates
  updateParcel(trackingNumber, parcel);

  return { success: true, newStatus: newStatus };
}

// ============================================
// DELETE PARCEL
// ============================================
function removeParcel(trackingNumber) {
  deleteParcel(trackingNumber);
  return { success: true };
}

// ============================================
// GET ALL PARCELS FOR DISPLAY
// ============================================
function getDisplayParcels() {
  let parcels = getAllParcels();
  return parcels.map(p => ({
    trackingNumber: p.trackingNumber,
    sender: p.senderName,
    receiver: p.receiverName,
    destination: p.deliveryLocation,
    weight: p.weight + ' kg',
    status: p.status,
    cost: formatCost(p.cost)
  }));
}

// ============================================
// SORTING
// ============================================
function sortParcels(algorithm = 'bubble', fieldName = 'trackingNumber') {
  let parcels = getAllParcels();

  let sorted;
  switch (algorithm) {
    case 'bubble':
      sorted = bubbleSort(parcels, fieldName);
      break;
    case 'selection':
      sorted = selectionSort(parcels, fieldName);
      break;
    case 'merge':
      sorted = mergeSort(parcels, fieldName);
      break;
    default:
      sorted = bubbleSort(parcels, fieldName);
  }

  return sorted.map(p => ({
    trackingNumber: p.trackingNumber,
    sender: p.senderName,
    destination: p.deliveryLocation,
    status: p.status,
    cost: p.cost
  }));
}
