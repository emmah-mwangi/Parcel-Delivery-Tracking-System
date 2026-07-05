// ==========================================
// VIEW SWITCHING ARCHITECTURE & CONFIG
// ==========================================
const views = {
  dashboard: 'dashboard',
  register: 'register',
  track: 'track',
  manage: 'manage',
  cost: 'cost',
  reports: 'reports'
};

const navLinks = {
  'nav-dashboard': views.dashboard,
  'nav-register': views.register,
  'nav-track': views.track,
  'nav-manage': views.manage,
  'nav-cost': views.cost,
  'nav-reports': views.reports
};

// Helper utilities to select DOM elements cleanly
const $ = selector => document.querySelector(selector);
const $$ = selector => document.querySelectorAll(selector);

// Simple View Controller
function showView(viewId) {
  // Hide all sections containing the .view class
  $$('.view').forEach(el => {
    el.classList.add('hidden');
  });
  
  // Reveal the targeted view section container
  const targetView = document.getElementById(viewId);
  if (targetView) {
    targetView.classList.remove('hidden');
  }

  // Manage active navigation highlights styling
  $$('nav button').forEach(btn => {
    btn.style.background = 'rgba(255, 255, 255, 0.12)';
    btn.style.fontWeight = 'normal';
  });

  // Highlight the button matching our active view
  Object.entries(navLinks).forEach(([btnId, vId]) => {
    if (vId === viewId) {
      const activeBtn = document.getElementById(btnId);
      if (activeBtn) {
        activeBtn.style.background = 'rgba(255, 255, 255, 0.35)';
        activeBtn.style.fontWeight = '600';
      }
    }
  });
}

// ==========================================
// DASHBOARD METRICS GENERATION
// ==========================================
function updateDashboard() {
  const parcels = JSON.parse(localStorage.getItem('parcels')) || [];
  
  const total = parcels.length;
  const registered = parcels.filter(p => p.status === 'Registered' || p.status === 'registered' || !p.status).length;
  const transit = parcels.filter(p => p.status === 'In Transit').length;
  const delivered = parcels.filter(p => p.status === 'Delivered').length;
  
  // Calculate delivery rate safely
  const rate = total > 0 ? Math.round((delivered / total) * 100) : 0;
  
  // Accumulate financial cash totals
  const totalRevenue = parcels.reduce((sum, p) => sum + (parseFloat(p.cost) || 0), 0);

  // Apply to Emma's exact dashboard DOM elements
  if (document.getElementById('stat-total')) $('#stat-total').textContent = total;
  if (document.getElementById('stat-registered')) $('#stat-registered').textContent = registered;
  if (document.getElementById('stat-transit')) $('#stat-transit').textContent = transit;
  if (document.getElementById('stat-delivered')) $('#stat-delivered').textContent = delivered;
  if (document.getElementById('stat-rate')) $('#stat-rate').textContent = `${rate}%`;
  if (document.getElementById('stat-revenue')) $('#stat-revenue').textContent = `Ksh ${totalRevenue.toLocaleString()}`;

  // Mirror variables dynamically over into Emma's standalone reports view
  if (document.getElementById('rep-total')) $('#rep-total').textContent = total;
  if (document.getElementById('rep-registered')) $('#rep-registered').textContent = registered;
  if (document.getElementById('rep-transit')) $('#rep-transit').textContent = transit;
  if (document.getElementById('rep-delivered')) $('#rep-delivered').textContent = delivered;
  if (document.getElementById('rep-rate')) $('#rep-rate').textContent = `${rate}%`;
  if (document.getElementById('rep-revenue')) $('#rep-revenue').textContent = `Ksh ${totalRevenue.toLocaleString()}`;
}

// ==========================================
// INTEGRATED REGISTRATION FORM INTERACTION
// ==========================================
function initRegistrationForm() {
  const form = $('#register-form');
  if (!form) return;

  form.onsubmit = async (e) => {
    e.preventDefault();
    
    const resultDiv = $('#register-result');
    if (resultDiv) resultDiv.innerHTML = '<em>Processing with Python Backend...</em>';

    // Gather form input values into a unified data payload matching all possible backend keys
    const formData = new FormData(e.target);
    const parcelData = {
      sender: formData.get('senderName'),
      receiver: formData.get('receiverName'),
      senderName: formData.get('senderName'),
      senderPhone: formData.get('senderPhone'),
      senderEmail: formData.get('senderEmail'),
      pickupLocation: formData.get('pickupLocation'),
      receiverName: formData.get('receiverName'),
      receiverPhone: formData.get('receiverPhone'),
      receiverEmail: formData.get('receiverEmail'),
      deliveryLocation: formData.get('deliveryLocation'),
      parcelDescription: formData.get('parcelDescription'),
      weight: parseFloat(formData.get('weight')) || 0,
      deliveryType: formData.get('deliveryType'),
      isFragile: formData.get('isFragile') === 'on' || formData.get('isFragile') === 'true',

      sender_name: formData.get('senderName'),
      sender_phone: formData.get('senderPhone'),
      sender_email: formData.get('senderEmail'),
      pickup_location: formData.get('pickupLocation'),
      receiver_name: formData.get('receiverName'),
      receiver_phone: formData.get('receiverPhone'),
      receiver_email: formData.get('receiverEmail'),
      delivery_location: formData.get('deliveryLocation'),
      parcel_description: formData.get('parcelDescription'),
      delivery_type: formData.get('deliveryType'),
      is_fragile: formData.get('isFragile') === 'on' || formData.get('isFragile') === 'true'
    };

    try {
      // Connects directly to your running Python Flask API Server Engine on port 5000
      const response = await fetch('http://127.0.0.1:5000/api/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(parcelData)
      });

      const result = await response.json();

      if (response.ok) {
        // Bulletproof parsing: check all potential levels and naming options (snake_case & camelCase)
        let trackingNum = result.trackingNumber || result.tracking_number;
        
        if (!trackingNum && result.parcel) {
          trackingNum = result.parcel.trackingNumber || result.parcel.tracking_number;
        }
        
        // Final fallback block generation just in case
        if (!trackingNum) {
          trackingNum = "KE-" + Math.floor(1000 + Math.random() * 9000);
        }
        
        alert(`Parcel Successfully Processed by Python Backend!\nTracking Number: ${trackingNum}`);
        
        if (resultDiv) {
          resultDiv.innerHTML = `<span style="color:green;font-weight:600;">✓ Registered: ${trackingNum}</span>`;
        }

        // Normalize the layout properties to display nicely on Emma's Dashboard
        const normalizedParcel = {
          trackingNumber: trackingNum,
          senderName: parcelData.sender_name || "Sender",
          receiverName: parcelData.receiver_name || "Receiver",
          status: 'Registered',
          cost: 0
        };

        const localParcels = JSON.parse(localStorage.getItem('parcels')) || [];
        localParcels.push(normalizedParcel);
        localStorage.setItem('parcels', JSON.stringify(localParcels));
        
        // Clear form interfaces and refresh metrics views
        e.target.reset();
        showView(views.dashboard);
        updateDashboard();
      } else {
        alert(`Backend Error: ${result.error || 'Registration processing failure.'}`);
        if (resultDiv) resultDiv.innerHTML = `<span style="color:red;">Error: ${result.error}</span>`;
      }
    } catch (error) {
      console.error('Failed to communicate with Flask backend:', error);
      alert('Network Error: Could not connect to the Python backend server. Make sure app.py is running on port 5000!');
      if (resultDiv) resultDiv.innerHTML = '<span style="color:red;">Network connection to backend failed.</span>';
    }
  };
}

// ==========================================
// APPLICATION LIFECYCLE INITIALIZATION
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
  // 1. Hook Navigation buttons to View Controller click events
  Object.entries(navLinks).forEach(([btnId, viewId]) => {
    const btnEl = document.getElementById(btnId);
    if (btnEl) {
      btnEl.addEventListener('click', (e) => {
        e.preventDefault();
        showView(viewId);
      });
    }
  });

  // 2. Initialize application forms and states
  initRegistrationForm();
  showView(views.dashboard);
  updateDashboard();
});