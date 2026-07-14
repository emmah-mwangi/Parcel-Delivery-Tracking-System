/**
 * APP.JS — thin API client
 * Every data structure and algorithm lives on the backend (see
 * backend/*.py). This file only calls the REST API and renders
 * the result — it holds no parcel data of its own.
 */

const $ = sel => document.querySelector(sel);
const $$ = sel => document.querySelectorAll(sel);

const API = 'http://127.0.0.1:5000/api';

const views = {
  dashboard: $('#dashboard'),
  register: $('#register'),
  track: $('#track'),
  manage: $('#manage'),
  queue: $('#queue'),
  cost: $('#cost'),
  reports: $('#reports')
};

const navButtons = {
  dashboard: $('#nav-dashboard'),
  register: $('#nav-register'),
  track: $('#nav-track'),
  manage: $('#nav-manage'),
  queue: $('#nav-queue'),
  cost: $('#nav-cost'),
  reports: $('#nav-reports')
};

function showView(name) {
  Object.entries(views).forEach(([key, el]) => {
    el.classList.toggle('hidden', key !== name);
    navButtons[key].classList.toggle('active', key === name);
  });
}

navButtons.dashboard.onclick = () => { showView('dashboard'); loadDashboard(); };
navButtons.register.onclick = () => showView('register');
navButtons.track.onclick = () => showView('track');
navButtons.manage.onclick = () => { showView('manage'); loadParcelsTable(); };
navButtons.queue.onclick = () => { showView('queue'); loadQueueView(); };
navButtons.cost.onclick = () => showView('cost');
navButtons.reports.onclick = () => { showView('reports'); loadReport(); };

// ============================================================
// HELPERS
// ============================================================
function formatCost(amount) {
  return 'Ksh ' + Number(amount).toLocaleString(undefined, { maximumFractionDigits: 2 });
}

function statusClass(status) {
  const s = (status || '').toLowerCase();
  if (s === 'delivered') return 'delivered';
  if (s === 'cancelled' || s === 'returned') return 'cancelled';
  if (s === 'dispatched' || s === 'in transit' || s === 'out for delivery') return 'dispatched';
  return '';
}

async function api(path, options = {}) {
  const res = await fetch(API + path, {
    headers: { 'Content-Type': 'application/json' },
    ...options
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `Request failed (${res.status})`);
  return data;
}

function renderRouteStrip(path, distanceKm) {
  if (!path || !path.length) return '';
  const chain = path.map((town, i) =>
    `<span class="route-node">${town}</span>` +
    (i < path.length - 1 ? `<span class="route-link"></span>` : '')
  ).join('');
  return `<div class="route-strip">${chain}</div>
    <p style="color:var(--text-muted);font-size:12px;margin:6px 0 0;">Shortest route found by Dijkstra's algorithm — ${distanceKm} km total.</p>`;
}

// ============================================================
// DASHBOARD
// ============================================================
async function loadDashboard() {
  const data = await api('/reports');
  const s = data.summary;
  $('#stat-total').textContent = s.total_parcels;
  $('#stat-registered').textContent = s.by_status['Registered'] || 0;
  $('#stat-transit').textContent = (s.by_status['Dispatched'] || 0) + (s.by_status['In Transit'] || 0) + (s.by_status['Out For Delivery'] || 0);
  $('#stat-delivered').textContent = s.by_status['Delivered'] || 0;
  const rate = s.total_parcels ? Math.round(((s.by_status['Delivered'] || 0) / s.total_parcels) * 100) : 0;
  $('#stat-rate').textContent = rate + '%';
  $('#stat-revenue').textContent = formatCost(s.total_revenue);

  const log = await api('/status-log');
  const list = $('#dashboard-log');
  if (!log.length) {
    list.innerHTML = '<li class="empty-state">No activity yet.</li>';
  } else {
    list.innerHTML = log.slice(0, 6).map((entry, i) => `
      <li><span class="structure-index">${i === 0 ? 'TOP' : i}</span>
        <span class="tracking-code">${entry.tracking_number}</span>
        <span>${entry.from || '—'} → ${entry.to}</span></li>
    `).join('');
  }
}

// ============================================================
// REGISTER
// ============================================================
$('#register-form').onsubmit = async e => {
  e.preventDefault();
  const form = e.target;
  const data = Object.fromEntries(new FormData(form).entries());
  data.is_fragile = form.is_fragile.checked;

  const resultEl = $('#register-result');
  try {
    const parcel = await api('/parcels', { method: 'POST', body: JSON.stringify(data) });
    resultEl.innerHTML = `
      <div class="result-block success">
        <strong>Parcel registered.</strong><br>
        Tracking number: <span class="tracking-code">${parcel.tracking_number}</span><br>
        Cost: <strong>${formatCost(parcel.cost)}</strong>
        ${renderRouteStrip(parcel.route_path, parcel.distance_km)}
      </div>`;
    form.reset();
  } catch (err) {
    resultEl.innerHTML = `<div class="result-block error">${err.message}</div>`;
  }
};

// ============================================================
// TRACK  (hash table lookup, or search fallback)
// ============================================================
$('#track-form').onsubmit = async e => {
  e.preventDefault();
  const type = $('#track-type').value;
  const value = $('#track-value').value;
  const resultEl = $('#track-result');

  try {
    let parcel;
    if (type === 'tracking_number') {
      parcel = await api(`/parcels/${encodeURIComponent(value)}`);
    } else {
      const res = await api(`/search?field=${type}&value=${encodeURIComponent(value)}&algorithm=linear`);
      parcel = res.result;
    }

    const history = (parcel.status_history || []).slice().reverse()
      .map(h => `<li>${h.status} — ${new Date(h.timestamp).toLocaleString()} ${h.location ? '(' + h.location + ')' : ''}</li>`).join('');

    resultEl.innerHTML = `
      <div class="panel">
        <p><strong>Tracking:</strong> <span class="tracking-code">${parcel.tracking_number}</span></p>
        <p><strong>Sender:</strong> ${parcel.sender_name} ${parcel.sender_phone ? '(' + parcel.sender_phone + ')' : ''}</p>
        <p><strong>Receiver:</strong> ${parcel.receiver_name} ${parcel.receiver_phone ? '(' + parcel.receiver_phone + ')' : ''}</p>
        <p><strong>Status:</strong> <span class="status-badge ${statusClass(parcel.status)}">${parcel.status}</span></p>
        <p><strong>Cost:</strong> ${formatCost(parcel.cost)}</p>
        ${renderRouteStrip(parcel.route_path, parcel.distance_km)}
        <p><strong>Status history</strong></p>
        <ul class="structure-list">${history}</ul>
      </div>`;
  } catch (err) {
    resultEl.innerHTML = `<div class="result-block error">${err.message}</div>`;
  }
};

// ============================================================
// MANAGE — table, search, sort, row actions
// ============================================================
function renderParcelsTable(parcels) {
  const tbody = $('#parcels-table tbody');
  if (!parcels.length) {
    tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;color:var(--text-muted);">No parcels registered yet.</td></tr>';
    return;
  }
  tbody.innerHTML = parcels.map(p => `
    <tr>
      <td class="tracking-cell">${p.tracking_number}</td>
      <td>${p.sender_name}</td>
      <td>${p.receiver_name}</td>
      <td>${p.distance_km} km</td>
      <td>${p.weight_kg} kg</td>
      <td><span class="status-badge ${statusClass(p.status)}">${p.status}</span></td>
      <td>${formatCost(p.cost)}</td>
      <td>
        <button class="action-btn" onclick="viewParcel('${p.tracking_number}')">View</button>
        <button class="action-btn" onclick="editStatus('${p.tracking_number}')">Update</button>
        <button class="action-btn delete" onclick="deleteParcelAction('${p.tracking_number}')">Delete</button>
      </td>
    </tr>
  `).join('');
}

async function loadParcelsTable() {
  const parcels = await api('/parcels');
  renderParcelsTable(parcels);
}

window.viewParcel = async trackingNumber => {
  const p = await api(`/parcels/${trackingNumber}`);
  const history = (p.status_history || []).map(h => h.status).join(' → ');
  alert(`Tracking: ${p.tracking_number}\nSender: ${p.sender_name}\nReceiver: ${p.receiver_name}\nDistance: ${p.distance_km} km\nStatus: ${p.status}\nHistory: ${history}`);
};

window.editStatus = async trackingNumber => {
  const p = await api(`/parcels/${trackingNumber}`);
  const options = ['Registered', 'Dispatched', 'In Transit', 'Out For Delivery', 'Delivered', 'Cancelled', 'Returned'];
  const newStatus = prompt(`Current status: ${p.status}\n\nEnter new status:\n${options.join(', ')}`, p.status);
  if (newStatus && options.includes(newStatus)) {
    await api(`/parcels/${trackingNumber}/status`, { method: 'PUT', body: JSON.stringify({ status: newStatus }) });
    loadParcelsTable();
    loadDashboard();
  }
};

window.deleteParcelAction = async trackingNumber => {
  if (!confirm(`Delete parcel ${trackingNumber}? This cannot be undone.`)) return;
  await api(`/parcels/${trackingNumber}`, { method: 'DELETE' });
  loadParcelsTable();
  loadDashboard();
};

$('#search-btn').onclick = async () => {
  const field = $('#search-field').value;
  const algorithm = $('#search-algo').value;
  const value = $('#search-value').value;
  const resultEl = $('#search-result');
  try {
    const res = await api(`/search?field=${field}&value=${encodeURIComponent(value)}&algorithm=${algorithm}`);
    renderParcelsTable([res.result]);
    resultEl.innerHTML = `<div class="result-block info">Found via <strong>${algorithm === 'binary' ? 'Binary Search — O(log n)' : 'Linear Search — O(n)'}</strong>.</div>`;
  } catch (err) {
    resultEl.innerHTML = `<div class="result-block error">${err.message}</div>`;
    renderParcelsTable([]);
  }
};

$('#search-clear-btn').onclick = () => { $('#search-result').innerHTML = ''; loadParcelsTable(); };

$('#sort-btn').onclick = async () => {
  const field = $('#sort-field').value;
  const algorithm = $('#sort-algo').value;
  const order = $('#sort-order').value;
  const res = await api(`/sort?field=${field}&algorithm=${algorithm}&order=${order}`);
  renderParcelsTable(res.result);
};

// ============================================================
// DISPATCH QUEUE  (Priority Queue + Stack)
// ============================================================
async function loadQueueView() {
  const queue = await api('/queue');
  const queueList = $('#queue-list');
  queueList.innerHTML = queue.length
    ? queue.map((p, i) => `
        <li><span class="structure-index">${i === 0 ? 'NEXT' : i + 1}</span>
          <span class="tracking-code">${p.tracking_number}</span>
          <span class="status-badge">${p.delivery_type}</span></li>`).join('')
    : '<li class="empty-state">Queue is empty.</li>';

  const log = await api('/status-log');
  const logList = $('#status-stack-list');
  logList.innerHTML = log.length
    ? log.map((entry, i) => `
        <li><span class="structure-index">${i === 0 ? 'TOP' : i}</span>
          <span class="tracking-code">${entry.tracking_number}</span>
          <span>${entry.from || '—'} → ${entry.to}</span>
          <span style="color:var(--text-muted);font-size:11px;">${new Date(entry.timestamp).toLocaleTimeString()}</span></li>`).join('')
    : '<li class="empty-state">No changes logged yet.</li>';
}

$('#process-next-btn').onclick = async () => {
  try {
    await api('/queue/process-next', { method: 'POST' });
    loadQueueView();
    loadDashboard();
  } catch (err) {
    alert(err.message);
  }
};

$('#undo-btn').onclick = async () => {
  try {
    await api('/undo-last-status', { method: 'POST' });
    loadQueueView();
    loadDashboard();
  } catch (err) {
    alert(err.message);
  }
};

// ============================================================
// COST CALCULATOR
// ============================================================
$('#cost-form').onsubmit = async e => {
  e.preventDefault();
  const body = {
    weight_kg: parseFloat($('#calc-weight').value) || 0,
    delivery_type: $('#calc-type').value,
    is_fragile: $('#calc-fragile').checked
  };
  const resultEl = $('#cost-result');
  try {
    const res = await api('/calculate-cost', { method: 'POST', body: JSON.stringify(body) });
    const b = res.breakdown;
    resultEl.innerHTML = `
      <div class="result-block success">
        Base: ${formatCost(b.base_fee)}<br>
        Weight (${body.weight_kg}kg × 40): ${formatCost(b.weight_charge)}<br>
        Distance (${res.distance_km}km × 5): ${formatCost(b.distance_charge)}<br>
        ${b.speed_surcharge ? `Speed surcharge: ${formatCost(b.speed_surcharge)}<br>` : ''}
        ${b.fragile_surcharge ? `Fragile surcharge: ${formatCost(b.fragile_surcharge)}<br>` : ''}
        <strong>Total: ${formatCost(b.total)}</strong>
        ${renderRouteStrip(res.path, res.distance_km)}
      </div>`;
  } catch (err) {
    resultEl.innerHTML = `<div class="result-block error">${err.message}</div>`;
  }
};

// ============================================================
// REPORTS
// ============================================================
async function loadReport() {
  const data = await api('/reports');
  const s = data.summary;

  const destRows = data.top_destinations.length
    ? data.top_destinations.map(d => `<li>${d.destination} — <strong>${d.count}</strong></li>`).join('')
    : '<li class="empty-state">No parcels yet.</li>';

  const weightRows = Object.entries(data.weight_distribution)
    .map(([bin, count]) => `<li>${bin} — <strong>${count}</strong></li>`).join('');

  $('#report-content').innerHTML = `
    <div class="panel">
      <h3>Parcel statistics</h3>
      <p>Total parcels: <strong>${s.total_parcels}</strong></p>
      <p>Average weight: <strong>${s.average_weight_kg} kg</strong></p>
      <p>Total revenue: <strong>${formatCost(s.total_revenue)}</strong></p>
      <p>Dispatch queue waiting: <strong>${data.queue_status.waiting}</strong> (next: ${data.queue_status.next_tracking_number || 'none'})</p>
    </div>
    <div class="panel">
      <h3>Top destinations</h3>
      <ul class="structure-list">${destRows}</ul>
    </div>
    <div class="panel">
      <h3>Weight distribution</h3>
      <ul class="structure-list">${weightRows}</ul>
    </div>`;
}

$('#print-btn').onclick = () => window.print();

$('#export-csv-btn').onclick = async () => {
  const parcels = await api('/parcels');
  let csv = 'Tracking,Sender,Receiver,Distance,Weight,Status,Cost\n';
  parcels.forEach(p => {
    csv += `${p.tracking_number},${p.sender_name},${p.receiver_name},${p.distance_km},${p.weight_kg},${p.status},${p.cost}\n`;
  });
  const link = document.createElement('a');
  link.href = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv);
  link.download = 'parcels_report.csv';
  link.click();
};

// ============================================================
// INIT
// ============================================================
window.onload = () => {
  loadDashboard();
};
