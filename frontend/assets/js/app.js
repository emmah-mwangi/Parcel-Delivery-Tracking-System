// Simple JavaScript - no fancy frameworks

// Show/hide pages
function showPage(pageId) {
  // Hide all pages
  document.querySelectorAll('.page').forEach(page => {
    page.classList.add('hidden');
    page.classList.remove('active');
  });
  
  // Show selected page
  const selectedPage = document.getElementById(pageId);
  if (selectedPage) {
    selectedPage.classList.remove('hidden');
    selectedPage.classList.add('active');
  }
  
  // Update nav links
  document.querySelectorAll('.nav-link').forEach(link => {
    link.classList.remove('active');
  });
  document.querySelector(`[data-page="${pageId}"]`)?.classList.add('active');
}

// Navigation
document.querySelectorAll('.nav-link').forEach(link => {
  link.addEventListener('click', (e) => {
    e.preventDefault();
    const page = link.getAttribute('data-page');
    showPage(page);
  });
});

// API helper
async function api(url, options = {}) {
  const response = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options
  });
  return response.json();
}

// Load dashboard stats
async function loadStats() {
  try {
    const data = await api('/api/dashboard');
    
    document.getElementById('total-parcels').textContent = data.total || 0;
    document.getElementById('in-transit').textContent = data.in_transit || 0;
    document.getElementById('delivered').textContent = data.delivered || 0;
    document.getElementById('delivery-rate').textContent = (data.delivery_rate || 0) + '%';
  } catch (error) {
    console.error('Failed to load stats:', error);
  }
}

// Register parcel form
document.getElementById('register-form')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const sender = document.getElementById('sender').value.trim();
  const receiver = document.getElementById('receiver').value.trim();
  const destination = document.getElementById('destination').value;
  const weight = parseFloat(document.getElementById('weight').value);
  const description = document.getElementById('description').value.trim();
  const resultDiv = document.getElementById('register-result');
  
  try {
    const data = await api('/api/register', {
      method: 'POST',
      body: JSON.stringify({ sender, receiver, destination, weight, description })
    });
    
    if (data.success) {
      resultDiv.className = 'success';
      resultDiv.innerHTML = `
        <strong>✓ Parcel Registered Successfully!</strong><br><br>
        <strong>Tracking ID:</strong> ${data.tracking_id}<br>
        <strong>From:</strong> ${data.sender}<br>
        <strong>To:</strong> ${data.receiver}<br>
        <strong>Destination:</strong> ${data.destination || 'N/A'}<br>
        <strong>Weight:</strong> ${data.weight} kg<br>
        <strong>Status:</strong> ${data.status}
      `;
      e.target.reset();
      loadStats();
      loadParcels();
    } else {
      throw new Error(data.error);
    }
  } catch (error) {
    resultDiv.className = 'error';
    resultDiv.textContent = '✗ Error: ' + error.message;
  }
});

// Track parcel form
document.getElementById('track-form')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const trackingId = document.getElementById('track-id').value.trim();
  const resultDiv = document.getElementById('track-result');
  
  try {
    const data = await api('/api/track/' + encodeURIComponent(trackingId));
    
    if (data.error) {
      resultDiv.className = 'error';
      resultDiv.textContent = '✗ ' + data.error;
    } else {
      resultDiv.className = 'success';
      resultDiv.innerHTML = `
        <div style="background: #f8f9fa; padding: 15px; border-radius: 4px; margin-bottom: 15px;">
          <h3 style="margin-top: 0; color: #2c3e50;">Parcel Details</h3>
          <p><strong>Tracking Number:</strong> ${data.tracking_id}</p>
          <p><strong>Status:</strong> <span class="status status-${data.status.toLowerCase().replace(' ', '-')}">${data.status}</span></p>
          <p><strong>From:</strong> ${data.sender}</p>
          <p><strong>To:</strong> ${data.receiver}</p>
        </div>
        <div style="background: #e8f5e9; padding: 15px; border-radius: 4px;">
          <h3 style="margin-top: 0; color: #2c3e50;">Delivery History</h3>
          ${data.history.map(h => `<p style="margin: 5px 0;"><small>${h.timestamp}</small><br><strong>${h.status}</strong></p>`).join('')}
        </div>
      `;
    }
  } catch (error) {
    resultDiv.className = 'error';
    resultDiv.textContent = '✗ Error: ' + error.message;
  }
});

// Load parcels table
async function loadParcels() {
  try {
    const data = await api('/api/reports/parcels');
    const tbody = document.getElementById('parcels-tbody');
    
    tbody.innerHTML = '';
    
    data.parcels.forEach(parcel => {
      const row = tbody.insertRow();
      row.innerHTML = `
        <td>${parcel.tracking_id}</td>
        <td>${parcel.sender}</td>
        <td>${parcel.receiver}</td>
        <td>${parcel.destination || '-'}</td>
        <td>${parcel.weight || '-'}</td>
        <td><span class="status status-${parcel.status.toLowerCase().replace(' ', '-')}">${parcel.status}</span></td>
      `;
    });
  } catch (error) {
    console.error('Failed to load parcels:', error);
  }
}

// Cost calculator form
document.getElementById('calc-form')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const weight = parseFloat(document.getElementById('weight').value);
  const destination = document.getElementById('destination').value;
  const deliveryType = document.getElementById('delivery-type').value;
  const resultDiv = document.getElementById('calc-result');
  
  try {
    const data = await api('/api/cost/calculate', {
      method: 'POST',
      body: JSON.stringify({ weight, destination, delivery_type: deliveryType })
    });
    
    if (data.success) {
      resultDiv.className = 'success';
      resultDiv.innerHTML = `
        <strong>Total Cost: KES ${data.total_cost.toFixed(2)}</strong><br><br>
        <small>
          Base: KES ${data.breakdown.base_cost}<br>
          Weight: KES ${data.breakdown.weight_cost.toFixed(2)}<br>
          Subtotal: KES ${data.breakdown.subtotal.toFixed(2)}<br>
          Destination (${data.breakdown.destination_multiplier}x): KES ${data.breakdown.subtotal_with_destination.toFixed(2)}<br>
          Tax (16%): KES ${data.breakdown.tax_16_percent.toFixed(2)}
        </small>
      `;
    } else {
      throw new Error(data.error);
    }
  } catch (error) {
    resultDiv.className = 'error';
    resultDiv.textContent = '✗ Error: ' + error.message;
  }
});

// Load reports
async function loadReports() {
  try {
    const data = await api('/api/reports/statistics');
    const tbody = document.getElementById('report-tbody');
    const statsDiv = document.getElementById('report-stats');
    
    // Show stats
    if (data) {
      statsDiv.innerHTML = `
        <div class="stat-card">
          <h3>Total Parcels</h3>
          <p>${data.total || 0}</p>
        </div>
        <div class="stat-card">
          <h3>Delivered</h3>
          <p>${data.delivered || 0}</p>
        </div>
        <div class="stat-card">
          <h3>Pending</h3>
          <p>${data.registered + data.picked_up + data.in_transit + data.out_for_delivery || 0}</p>
        </div>
        <div class="stat-card">
          <h3>Delivery Rate</h3>
          <p>${(data.delivery_rate || 0).toFixed(1)}%</p>
        </div>
      `;
    }
    
    // Load parcels
    const parcelsData = await api('/api/reports/parcels');
    tbody.innerHTML = '';
    
    parcelsData.parcels.forEach(parcel => {
      const row = tbody.insertRow();
      row.innerHTML = `
        <td>${parcel.tracking_id}</td>
        <td>${parcel.sender}</td>
        <td>${parcel.receiver}</td>
        <td>${parcel.destination || '-'}</td>
        <td>${parcel.weight ? parcel.weight + ' kg' : '-'}</td>
        <td><span class="status status-${parcel.status.toLowerCase().replace(' ', '-')}">${parcel.status}</span></td>
      `;
    });
  } catch (error) {
    console.error('Failed to load reports:', error);
  }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  loadStats();
  loadParcels();
  loadReports();
});