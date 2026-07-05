/**
 * ALGORITHMS MODULE
 * Implements: Linear Search, Binary Search, Bubble Sort, Selection Sort, Merge Sort
 */

// ============================================
// LINEAR SEARCH
// Purpose: Find parcel by searching every parcel one by one
// Time Complexity: O(n)
// Space Complexity: O(1)
// ============================================
function linearSearch(parcels, fieldName, searchValue) {
  // Iterate through every parcel
  for (let i = 0; i < parcels.length; i++) {
    // Check if current parcel's field matches search value
    if (parcels[i][fieldName] === searchValue) {
      return parcels[i]; // Found - return immediately
    }
  }
  return null; // Not found
}

// ============================================
// BINARY SEARCH
// Purpose: Fast search on sorted parcels by tracking number
// Time Complexity: O(log n)
// Space Complexity: O(1)
// ============================================
function binarySearch(sortedParcels, trackingNumber) {
  let left = 0;
  let right = sortedParcels.length - 1;

  // Continue while search space exists
  while (left <= right) {
    let mid = Math.floor((left + right) / 2);
    let midValue = sortedParcels[mid].trackingNumber;

    // Check middle element
    if (midValue === trackingNumber) {
      return sortedParcels[mid]; // Found
    } else if (midValue < trackingNumber) {
      left = mid + 1; // Search right half
    } else {
      right = mid - 1; // Search left half
    }
  }
  return null; // Not found
}

// ============================================
// BUBBLE SORT
// Purpose: Simple sorting for educational demonstration
// Time Complexity: O(n²)
// Space Complexity: O(1)
// ============================================
function bubbleSort(parcels, fieldName) {
  let arr = [...parcels]; // Copy array
  let n = arr.length;

  // Outer loop: repeat n times
  for (let i = 0; i < n - 1; i++) {
    // Inner loop: compare adjacent elements
    for (let j = 0; j < n - i - 1; j++) {
      // Swap if current > next
      if (arr[j][fieldName] > arr[j + 1][fieldName]) {
        let temp = arr[j];
        arr[j] = arr[j + 1];
        arr[j + 1] = temp;
      }
    }
  }
  return arr;
}

// ============================================
// SELECTION SORT
// Purpose: Sorting for demonstration
// Time Complexity: O(n²)
// Space Complexity: O(1)
// ============================================
function selectionSort(parcels, fieldName) {
  let arr = [...parcels]; // Copy array
  let n = arr.length;

  // Outer loop: select minimum for each position
  for (let i = 0; i < n - 1; i++) {
    let minIndex = i;

    // Inner loop: find minimum element
    for (let j = i + 1; j < n; j++) {
      if (arr[j][fieldName] < arr[minIndex][fieldName]) {
        minIndex = j;
      }
    }

    // Swap minimum with current position
    if (minIndex !== i) {
      let temp = arr[i];
      arr[i] = arr[minIndex];
      arr[minIndex] = temp;
    }
  }
  return arr;
}

// ============================================
// MERGE SORT
// Purpose: Efficient sorting for larger datasets
// Time Complexity: O(n log n)
// Space Complexity: O(n)
// ============================================
function mergeSort(parcels, fieldName) {
  // Base case: array of 1 or 0 elements is sorted
  if (parcels.length <= 1) {
    return parcels;
  }

  // Divide: split array in half
  let mid = Math.floor(parcels.length / 2);
  let left = parcels.slice(0, mid);
  let right = parcels.slice(mid);

  // Conquer: recursively sort both halves
  left = mergeSort(left, fieldName);
  right = mergeSort(right, fieldName);

  // Combine: merge sorted halves
  return merge(left, right, fieldName);
}

// Helper function to merge two sorted arrays
function merge(left, right, fieldName) {
  let result = [];
  let i = 0, j = 0;

  // Compare elements from left and right, add smaller to result
  while (i < left.length && j < right.length) {
    if (left[i][fieldName] <= right[j][fieldName]) {
      result.push(left[i]);
      i++;
    } else {
      result.push(right[j]);
      j++;
    }
  }

  // Add remaining elements
  while (i < left.length) {
    result.push(left[i]);
    i++;
  }
  while (j < right.length) {
    result.push(right[j]);
    j++;
  }

  return result;
}
