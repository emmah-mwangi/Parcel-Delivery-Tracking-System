/**
 * COST CALCULATION MODULE
 * Calculates parcel delivery cost
 */

// ============================================
// COST CALCULATOR
// Formula:
// Base Fee: 300 KSh
// Weight Charge: Weight (kg) × 100
// Express Charge: +300 KSh (if Express)
// Fragile Charge: +200 KSh (if Fragile)
// Total = Base + Weight + Express + Fragile
// ============================================

function calculateDeliveryCost(weight, deliveryType = 'standard', isFragile = false) {
  const BASE_FEE = 300;
  const WEIGHT_CHARGE_PER_KG = 100;
  const EXPRESS_CHARGE = 300;
  const FRAGILE_CHARGE = 200;

  let cost = BASE_FEE;

  // Add weight charge
  cost += weight * WEIGHT_CHARGE_PER_KG;

  // Add express charge if applicable
  if (deliveryType === 'express') {
    cost += EXPRESS_CHARGE;
  }

  // Add fragile charge if applicable
  if (isFragile) {
    cost += FRAGILE_CHARGE;
  }

  return cost;
}

// Format cost as currency (KSh)
function formatCost(amount) {
  return 'Ksh ' + amount.toFixed(0);
}

// ============================================
// STATISTICS CALCULATION
// ============================================

function getStatistics(parcels) {
  let stats = {
    totalParcels: parcels.length,
    registered: 0,
    inTransit: 0,
    delivered: 0,
    deliveryRate: 0,
    totalRevenue: 0
  };

  // Count by status and sum revenue
  for (let parcel of parcels) {
    switch (parcel.status) {
      case 'Registered':
        stats.registered++;
        break;
      case 'In Transit':
        stats.inTransit++;
        break;
      case 'Delivered':
        stats.delivered++;
        break;
    }
    stats.totalRevenue += parcel.cost || 0;
  }

  // Calculate delivery rate
  if (stats.totalParcels > 0) {
    stats.deliveryRate = ((stats.delivered / stats.totalParcels) * 100).toFixed(1);
  }

  return stats;
}

// Get count of parcels by destination
function getDestinationCount(parcels) {
  let counts = {};
  for (let parcel of parcels) {
    let dest = parcel.deliveryLocation || 'Unknown';
    counts[dest] = (counts[dest] || 0) + 1;
  }

  // Find most common
  let maxDest = null;
  let maxCount = 0;
  for (let dest in counts) {
    if (counts[dest] > maxCount) {
      maxCount = counts[dest];
      maxDest = dest;
    }
  }

  return { counts, mostCommon: maxDest };
}
