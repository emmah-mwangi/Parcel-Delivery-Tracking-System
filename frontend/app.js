/**
 * UPDATED APP.JS
 * Main application logic - handles all UI interactions
 */

const $ = sel => document.querySelector(sel);
const $$ = sel => document.querySelectorAll(sel);

const views = {
  dashboard: $('#dashboard'),
  register: $('#register'),
  track: $('#track'),
  manage: $('#manage'),
  cost: $('#cost'),
  reports: $('#reports')
};

// ============================================
// NAVIGATION
// ============================================
function showView(view) {
  Object.values(views).forEach(v => v.classList.add('hidden'));
  view.classList.remove('hidden');
}

$('#nav-dashboard').onclick = () => {
  showView(views.dashboard);
  updateDashboard();
};
$('#nav-register').onclick = () => showView(views.register);
$('#nav-track').onclick = () => showView(views.track);
$('#nav-manage').onclick = () => {
  showView(views.manage);
  loadParcelsTable();
};
$('#nav-cost').onclick = () => showView(views.cost);
$('#nav-reports').onclick = () => {
  showView(views.reports);
  loadReport();
};

// ============================================
// DASHBOARD
// ============================================
function updateDashboard() {
  let parcels = getAllParcels();
  let stats = getStatistics(parcels);

  $('#stat-total').textContent = stats.totalParcels;
  $('#stat-registered').textContent = stats.registered;
  $('#stat-transit').textContent = stats.inTransit;
  $('#stat-delivered').textContent = stats.delivered;
  $('#stat-rate').textContent = stats.deliveryRate + '%';
  $('#stat-revenue').textContent = formatCost(stats.totalRevenue);

  // Display recently registered parcels (last 5)
  displayRecentParcels(parcels);
  
  // Display recent status updates
  displayStatusUpdates(parcels);
}

function displayRecentParcels(parcels) {
  let recentContainer = $('#recent-parcels');
  
  if (parcels.length === 0) {
    recentContainer.innerHTML = '<p style="color: #64748b;">No parcels registered yet.</p>';
    return;
  }

  // Get last 5 parcels (most recent first)
  let recentParcels = parcels.slice(-5).reverse();

  let html = '<div style="overflow-x: auto;"><table style="width: 100%; border-collapse: collapse;">';
  html += '<thead><tr style="background: #f1f5f9;">';
  html += '<th style="padding: 10px; text-align: left; font-size: 13px; color: #334155;">Tracking</th>';
  html += '<th style="padding: 10px; text-align: left; font-size: 13px; color: #334155;">Sender</th>';
  html += '<th style="padding: 10px; text-align: left; font-size: 13px; color: #334155;">Receiver</th>';
  html += '<th style="padding: 10px; text-align: left; font-size: 13px; color: #334155;">Destination</th>';
  html += '<th style="padding: 10px; text-align: left; font-size: 13px; color: #334155;">Status</th>';
  html += '<th style="padding: 10px; text-align: left; font-size: 13px; color: #334155;">Cost</th>';
  html += '</tr></thead><tbody>';

  recentParcels.forEach(p => {
    html += '<tr style="border-bottom: 1px solid #e2e8f0;">';
    html += `<td style="padding: 10px; font-weight: 500;">${p.trackingNumber}</td>`;
    html += `<td style="padding: 10px;">${p.senderName}</td>`;
    html += `<td style="padding: 10px;">${p.receiverName}</td>`;
    html += `<td style="padding: 10px;">${p.deliveryLocation}</td>`;
    html += `<td style="padding: 10px;"><span class="status-badge">${p.status}</span></td>`;
    html += `<td style="padding: 10px; font-weight: 500;">${formatCost(p.cost)}</td>`;
    html += '</tr>';
  });

  html += '</tbody></table></div>';
  html += '<p style="margin-top: 1rem; font-size: 12px; color: #64748b;">Showing last 5 registered parcels</p>';

  recentContainer.innerHTML = html;
}

function displayStatusUpdates(parcels) {
  let updatesContainer = $('#status-updates');
  
  if (parcels.length === 0) {
    updatesContainer.innerHTML = '<p class="no-parcels-message">No status updates yet.</p>';
    return;
  }

  // Collect all status updates from all parcels
  let allUpdates = [];
  parcels.forEach(p => {
    if (p.statusHistory && p.statusHistory.length > 0) {
      p.statusHistory.forEach(h => {
        allUpdates.push({
          tracking: p.trackingNumber,
          status: h.status,
          timestamp: h.timestamp,
          sender: p.senderName,
          receiver: p.receiverName
        });
      });
    }
  });

  // Sort by timestamp (most recent first) and get last 10
  allUpdates.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  let recentUpdates = allUpdates.slice(0, 10);

  if (recentUpdates.length === 0) {
    updatesContainer.innerHTML = '<p class="no-parcels-message">No status updates yet.</p>';
    return;
  }

  let html = '<div class="status-updates-list">';
  
  recentUpdates.forEach(update => {
    let date = new Date(update.timestamp);
    let timeStr = date.toLocaleString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      hour: '2-digit', 
      minute: '2-digit' 
    });
    
    html += '<div class="status-update-item">';
    html += '<div class="status-update-header">';
    html += `<span class="status-update-tracking">${update.tracking}</span>`;
    html += `<span class="status-update-time">${timeStr}</span>`;
    html += '</div>';
    html += '<div class="status-update-details">';
    html += `${update.sender} → ${update.receiver}`;
    html += `<span class="status-update-status">${update.status}</span>`;
    html += '</div>';
    html += '</div>';
  });
  
  html += '</div>';
  html += '<p style="margin-top: 1rem; font-size: 12px; color: #64748b;">Showing last 10 status updates</p>';

  updatesContainer.innerHTML = html;
}

// ============================================
// REGISTER PARCEL
// ============================================
$('#register-form').onsubmit = e => {
  e.preventDefault();

  let formData = new FormData(e.target);
  let data = Object.fromEntries(formData.entries());

  // Validate
  if (!data.senderName || !data.receiverName || !data.weight || !data.deliveryLocation) {
    $('#register-result').innerHTML = '<p style="color:red;">Error: Fill all required fields</p>';
    return;
  }

  // Create parcel
  let result = createParcel(data);

  if (result.error) {
    $('#register-result').innerHTML = `<p style="color:red;">Error: ${result.error}</p>`;
  } else {
    $('#register-result').innerHTML = `
      <div style="background:#d1fae5; padding:12px; border-radius:6px; color:green;">
        Success: <strong>Parcel Registered!</strong><br>
        Tracking: <strong>${result.trackingNumber}</strong><br>
        Cost: <strong>${formatCost(result.cost)}</strong>
      </div>
    `;
    e.target.reset();
    updateDashboard();
  }
};

// ============================================
// TRACK PARCEL
// ============================================
$('#track-form').onsubmit = e => {
  e.preventDefault();

  let searchType = $('#track-type').value;
  let searchValue = $('#track-value').value;

  let result = trackParcel(searchValue, searchType);

  if (result.error) {
    $('#track-result').innerHTML = `<p style="color:red;">Error: ${result.error}</p>`;
    return;
  }

  // Display parcel info
  let historyHtml = result.statusHistory
    .map(h => `<li>${h.status} - ${new Date(h.timestamp).toLocaleString()}</li>`)
    .reverse()
    .join('');

  $('#track-result').innerHTML = `
    <div style="background:#f0f9ff; padding:16px; border-radius:6px;">
      <p><strong>Tracking:</strong> ${result.trackingNumber}</p>
      <p><strong>Sender:</strong> ${result.sender}</p>
      <p><strong>Receiver:</strong> ${result.receiver}</p>
      <p><strong>Destination:</strong> ${result.deliveryLocation}</p>
      <p><strong>Status:</strong> <span style="color:blue;font-weight:bold;">${result.currentStatus}</span></p>
      <p><strong>Cost:</strong> ${result.cost}</p>
      <p><strong>Registered:</strong> ${result.registrationDate}</p>
      <p><strong>Status History:</strong></p>
      <ul>${historyHtml}</ul>
    </div>
  `;
};

// ============================================
// MANAGE PARCELS
// ============================================
function loadParcelsTable() {
  let parcels = getAllParcels();
  let tbody = $('#parcels-table tbody');
  tbody.innerHTML = '';

  if (parcels.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;">No parcels registered</td></tr>';
    return;
  }

  parcels.forEach(p => {
    let tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${p.trackingNumber}</td>
      <td>${p.senderName}</td>
      <td>${p.receiverName}</td>
      <td>${p.deliveryLocation}</td>
      <td><span class="status-badge">${p.status}</span></td>
      <td>${formatCost(p.cost)}</td>
      <td>
        <button class="action-btn" onclick="viewParcel('${p.trackingNumber}')">View</button>
        <button class="action-btn" onclick="editStatus('${p.trackingNumber}')">Update</button>
        <button class="action-btn delete" onclick="if(confirm('Delete?')) deleteParcelAction('${p.trackingNumber}')">Delete</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function viewParcel(trackingNumber) {
  let parcel = findParcel(trackingNumber);
  if (parcel) {
    let history = parcel.statusHistory
      .map(h => `${h.status}`)
      .reverse()
      .join(' → ');
    alert(`Tracking: ${parcel.trackingNumber}\nSender: ${parcel.senderName}\nReceiver: ${parcel.receiverName}\nStatus: ${parcel.status}\nHistory: ${history}`);
  }
}

function editStatus(trackingNumber) {
  let parcel = findParcel(trackingNumber);
  if (!parcel) return;

  let statusOptions = ['Registered', 'Dispatched', 'In Transit', 'Out For Delivery', 'Delivered', 'Cancelled', 'Returned'];
  
  // Create modal dialog
  let modal = document.createElement('div');
  modal.id = 'status-modal';
  modal.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.7);display:flex;align-items:center;justify-content:center;z-index:1000;';
  
  let modalContent = document.createElement('div');
  modalContent.style.cssText = 'background:#fff;padding:2rem;border-radius:8px;max-width:500px;width:90%;box-shadow:0 4px 20px rgba(0,0,0,0.3);';
  
  modalContent.innerHTML = `
    <h3 style="color: #0D3B66; margin-top: 0; margin-bottom: 1rem;">Update Parcel Status</h3>
    <p style="margin-bottom: 0.5rem;"><strong>Tracking:</strong> ${parcel.trackingNumber}</p>
    <p style="margin-bottom: 1rem;"><strong>Current Status:</strong> <span class="status-badge">${parcel.status}</span></p>
    <label style="margin-bottom: 1rem; font-weight: 500;">New Status:</label>
    <select id="new-status-select" style="width: 100%; padding: 0.6rem; border: 1px solid #cbd5e1; border-radius: 6px; margin-bottom: 1.5rem; font-size: 14px;">
      ${statusOptions.map(status => `<option value="${status}" ${status === parcel.status ? 'selected' : ''}>${status}</option>`).join('')}
    </select>
    <div style="display: flex; gap: 0.75rem; justify-content: flex-end;">
      <button class="action-btn" id="cancel-status-btn" style="background: #64748b; margin: 0;">Cancel</button>
      <button class="action-btn" id="save-status-btn" style="margin: 0;">Update Status</button>
    </div>
  `;
  
  modal.appendChild(modalContent);
  document.body.appendChild(modal);
  
  // Handle cancel
  document.getElementById('cancel-status-btn').onclick = () => {
    document.body.removeChild(modal);
  };
  
  // Handle save
  document.getElementById('save-status-btn').onclick = () => {
    let newStatus = document.getElementById('new-status-select').value;
    updateParcelStatus(trackingNumber, newStatus);
    loadParcelsTable();
    updateDashboard();
    document.body.removeChild(modal);
    alert('Status updated successfully!');
  };
  
  // Close on background click
  modal.onclick = (e) => {
    if (e.target === modal) {
      document.body.removeChild(modal);
    }
  };
}

function deleteParcelAction(trackingNumber) {
  removeParcel(trackingNumber);
  loadParcelsTable();
  updateDashboard();
}

// ============================================
// SORTING
// ============================================
$('#sort-btn').onclick = () => {
  let algorithm = $('#sort-algo').value;
  let field = $('#sort-field').value;
  let sorted = sortParcels(algorithm, field);

  let tbody = $('#parcels-table tbody');
  tbody.innerHTML = '';

  if (sorted.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7">No parcels</td></tr>';
    return;
  }

  sorted.forEach(p => {
    let tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${p.trackingNumber}</td>
      <td colspan="2"></td>
      <td>${p.destination}</td>
      <td>${p.status}</td>
      <td>${formatCost(p.cost)}</td>
      <td></td>
    `;
    tbody.appendChild(tr);
  });

  alert(`Sorted by ${field} using ${algorithm} sort`);
};

// ============================================
// COST CALCULATOR
// ============================================
$('#cost-form').onsubmit = e => {
  e.preventDefault();

  let weight = parseFloat($('#calc-weight').value) || 0;
  let type = $('#calc-type').value;
  let fragile = $('#calc-fragile').checked;

  let cost = calculateDeliveryCost(weight, type, fragile);

  let breakdown = `
    Base: 300 KSh<br>
    Weight (${weight}kg × 100): ${weight * 100} KSh<br>
    ${type === 'express' ? 'Express: 300 KSh<br>' : ''}
    ${fragile ? 'Fragile: 200 KSh<br>' : ''}
    <strong>Total: ${formatCost(cost)}</strong>
  `;

  $('#cost-result').innerHTML = `<div style="background:#fef3c7; padding:12px; border-radius:6px;">${breakdown}</div>`;
};

// ============================================
// REPORTS
// ============================================
function loadReport() {
  let parcels = getAllParcels();
  let stats = getStatistics(parcels);
  let { counts, mostCommon } = getDestinationCount(parcels);
  let queue = getQueue();

  let reportHtml = `
    <div style="background:#fff; padding:16px; border-radius:8px;">
      <h3>Parcel Statistics</h3>
      <p>Total Parcels: <strong>${stats.totalParcels}</strong></p>
      <p>Registered: <strong>${stats.registered}</strong></p>
      <p>In Transit: <strong>${stats.inTransit}</strong></p>
      <p>Delivered: <strong>${stats.delivered}</strong></p>
      <p>Delivery Rate: <strong>${stats.deliveryRate}%</strong></p>
      <p>Total Revenue: <strong>${formatCost(stats.totalRevenue)}</strong></p>
      
      <h3>Most Common Destination</h3>
      <p>${mostCommon || 'N/A'}</p>
      
      <h3>Processing Queue (FIFO)</h3>
      <p>Parcels waiting: ${queue.length}</p>
      <p>Next to process: ${queue[0] || 'None'}</p>
    </div>
  `;

  $('#report-content').innerHTML = reportHtml;
}

$('#print-btn').onclick = () => window.print();

$('#export-csv-btn').onclick = () => {
  let parcels = getAllParcels();
  let csv = 'Tracking,Sender,Receiver,Destination,Status,Cost\n';
  parcels.forEach(p => {
    csv += `${p.trackingNumber},${p.senderName},${p.receiverName},${p.deliveryLocation},${p.status},${p.cost}\n`;
  });

  let link = document.createElement('a');
  link.href = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv);
  link.download = 'parcels_report.csv';
  link.click();
};

// ============================================
// INITIALIZATION
// ============================================
window.onload = () => {
  initStorage();
  showView(views.dashboard);
  updateDashboard();
};
