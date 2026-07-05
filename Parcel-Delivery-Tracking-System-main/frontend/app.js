// ==========================================
// VIEW SWITCHING ARCHITECTURE & CONFIG
// ==========================================
const views = {
  dashboard: 'dashboard-view',
  registration: 'registration-view',
  tracking: 'tracking-view',
  reports: 'reports-view'
};

const navLinks = {
  'nav-dashboard': views.dashboard,
  'nav-registration': views.registration,
  'nav-tracking': views.tracking,
  'nav-reports': views.reports
};

// Helper utility to select DOM elements cleanly
const $ = selector => document.querySelector(selector);
const $$ = selector => document.querySelectorAll(selector);

// Simple View Controller
function showView(viewId) {
  Object.values(views).forEach(id => {
    const el = document.getElementById(id);
    if (el) el.classList.add('hidden');
  });
  
  const targetView = document.getElementById(viewId);
  if (targetView) targetView.classList.remove('hidden');

  // Update navbar active state highlights
  $$('nav a').forEach(link => {
    link.classList.remove('bg-indigo-700', 'text-white');
    link.classList.add('text-indigo-100', 'hover:bg-indigo-500');
  });

  Object.entries(navLinks).forEach(([linkId, vId]) => {
    if (vId === viewId) {
      const activeLink = document.getElementById(linkId);
      if (activeLink) {
        activeLink.classList.remove('text-indigo-100', 'hover:bg-indigo-500');
        activeLink.classList.add('bg-indigo-700', 'text-white');
      }
    }
  });
}

// ==========================================
// DASHBOARD METRICS GENERATION
// ==========================================
function updateDashboard() {
  // Pull existing client-side cache for displaying statistics metrics
  const parcels = JSON.parse(localStorage.getItem('parcels')) || [];
  
  const total = parcels.length;
  const transit = parcels.filter(p => p.status === 'In Transit').length;
  const delivered = parcels.filter(p => p.status === 'Delivered').length;

  if (document.getElementById('total-parcels')) $('#total-parcels').textContent = total;
  if (document.getElementById('parcels-transit')) $('#parcels-transit').textContent = transit;
  if (document.getElementById('parcels-delivered')) $('#parcels-delivered').textContent = delivered;

  // Refresh data tables in dashboard if present
  renderRecentParcelsTable(parcels);
}

function renderRecentParcelsTable(parcels) {
  const tbody = $('#recent-parcels-tbody');
  if (!tbody) return;

  tbody.innerHTML = '';
  
  if (parcels.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" class="px-6 py-4 text-center text-sm text-gray-500">No parcels registered yet.</td></tr>`;
    return;
  }

  // Display top 5 most recent records
  parcels.slice(-5).reverse().forEach(parcel => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${parcel.trackingNumber || 'N/A'}</td>
      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${parcel.senderName || 'N/A'}</td>
      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${parcel.receiverName || 'N/A'}</td>
      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${parcel.deliveryLocation || 'N/A'}</td>
      <td class="px-6 py-4 whitespace-nowrap text-sm">
        <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">${parcel.status || 'Registered'}</span>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

// ==========================================
// INTEGRATED REGISTRATION FORM INTERACTION
// ==========================================
function initRegistrationForm() {
  const form = $('#register-form');
  if (!form) return;

  form.onsubmit = async (e) => {
    e.preventDefault();

    // Gather form input values into a data object payload
    const formData = new FormData(e.target);
    const parcelData = {
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
      isFragile: formData.get('isFragile') === 'on'
    };

    try {
      // Direct connection hook straight to your custom Python Flask Backend Engine
      const response = await fetch('http://127.0.0.1:5000/api/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(parcelData)
      });

      const result = await response.json();

      if (result.success) {
        alert(`Parcel Successfully Processed by Python Backend!\nTracking Number: ${result.parcel.trackingNumber}`);
        
        // Feed backend tracking record back into local browser list for global frontend rendering compatibility
        const localParcels = JSON.parse(localStorage.getItem('parcels')) || [];
        localParcels.push(result.parcel);
        localStorage.setItem('parcels', JSON.stringify(localParcels));
        
        // Reset form interface and change view
        e.target.reset();
        showView(views.dashboard);
        updateDashboard();
      } else {
        alert(`Backend Rejection Error: ${result.error}`);
      }
    } catch (error) {
      console.error('Failed to communicate with Flask backend:', error);
      alert('Network Error: Could not connect to the Python backend server. Make sure app.py is running on port 5000!');
    }
  };
}

// ==========================================
// APPLICATION LIFECYCLE INITIALIZATION
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
  // 1. Hook Navigation event links up to View Controller
  Object.entries(navLinks).forEach(([linkId, viewId]) => {
    const linkEl = document.getElementById(linkId);
    if (linkEl) {
      linkEl.addEventListener('click', (e) => {
        e.preventDefault();
        showView(viewId);
      });
    }
  });

  // 2. Initialize Dark Mode Switcher (if UI theme toggler layout element exists)
  const themeToggleBtn = $('#theme-toggle');
  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', () => {
      document.body.classList.toggle('dark');
      const isDark = document.body.classList.contains('dark');
      localStorage.setItem('theme', isDark ? 'dark' : 'light');
    });
    // Check saved theme configuration preference layout
    if (localStorage.getItem('theme') === 'dark') {
      document.body.classList.add('dark');
    }
  }

  // 3. Kickoff form handlers and dashboards statistics layout metrics
  initRegistrationForm();
  showView(views.dashboard);
  updateDashboard();
});