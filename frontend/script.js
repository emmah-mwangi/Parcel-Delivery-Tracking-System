const API_BASE = 'http://localhost:5000/api';

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
});

// Navigation
function showSection(sectionId) {
    const sections = document.querySelectorAll('.section');
    const navBtns = document.querySelectorAll('.nav-btn');
    
    sections.forEach(s => s.classList.remove('active'));
    navBtns.forEach(b => b.classList.remove('active'));
    
    document.getElementById(sectionId).classList.add('active');
    event.target.classList.add('active');
    
    if (sectionId === 'dashboard') loadDashboard();
    else if (sectionId === 'manage') loadManagedParcels();
    else if (sectionId === 'calculator') loadHistory();
}

// Dashboard
function loadDashboard() {
    axios.get(`${API_BASE}/parcels/count`)
        .then(res => {
            document.getElementById('stat-total').textContent = res.data.total_parcels;
        })
        .catch(err => console.error(err));
    
    axios.get(`${API_BASE}/reports/statistics`)
        .then(res => {
            document.getElementById('stat-delivered').textContent = res.data.delivered;
            document.getElementById('stat-in-queue').textContent = res.data.dispatched;
            document.getElementById('stat-revenue').textContent = 'Ksh ' + res.data.total_revenue;
            
            let statsHtml = `
                <li><strong>Registered:</strong> ${res.data.registered}</li>
                <li><strong>In Transit:</strong> ${res.data.in_transit}</li>
                <li><strong>Out For Delivery:</strong> ${res.data.out_for_delivery}</li>
                <li><strong>Total Weight:</strong> ${res.data.total_weight} kg</li>
                <li><strong>Avg Weight:</strong> ${res.data.average_weight} kg</li>
                <li><strong>Avg Cost:</strong> Ksh ${res.data.average_cost}</li>
            `;
            document.getElementById('quick-stats').innerHTML = statsHtml;
        })
        .catch(err => console.error(err));
}

// Register Parcel
function registerParcel(e) {
    e.preventDefault();
    
    const data = {
        sender: document.getElementById('sender').value,
        receiver: document.getElementById('receiver').value,
        origin: document.getElementById('origin').value,
        destination: document.getElementById('destination').value,
        weight: document.getElementById('weight').value,
        delivery_type: document.getElementById('delivery_type').value
    };
    
    axios.post(`${API_BASE}/register`, data)
        .then(res => {
            showMessage(`Parcel registered! ID: ${res.data.tracking_id}. Cost: Ksh ${res.data.cost}`, 'success');
            document.querySelector('form').reset();
        })
        .catch(err => showMessage('Registration failed', 'error'));
}

// Track Parcel
function trackParcel() {
    const trackingId = document.getElementById('search-tracking').value;
    
    if (!trackingId) {
        showMessage('Enter tracking ID', 'error');
        return;
    }
    
    axios.get(`${API_BASE}/track/${trackingId}`)
        .then(res => {
            const p = res.data.parcel;
            const html = `
                <tr>
                    <td>${p.tracking_id}</td>
                    <td>${p.sender}</td>
                    <td>${p.receiver}</td>
                    <td>${p.origin}</td>
                    <td>${p.destination}</td>
                    <td>${p.status}</td>
                    <td>${p.weight} kg</td>
                    <td>Ksh ${p.cost}</td>
                </tr>
            `;
            document.getElementById('track-table-body').innerHTML = html;
            document.getElementById('track-result').classList.remove('hidden');
        })
        .catch(err => showMessage('Parcel not found', 'error'));
}

// Load Managed Parcels
function loadManagedParcels() {
    const sortBy = document.getElementById('sort-by').value;
    
    let endpoint = `${API_BASE}/reports/all`;
    
    if (sortBy === 'weight') {
        endpoint = `${API_BASE}/reports/by-weight`;
    } else if (sortBy === 'destination') {
        endpoint = `${API_BASE}/reports/by-destination`;
    }
    
    axios.get(endpoint)
        .then(res => {
            let html = '';
            res.data.parcels.forEach(p => {
                html += `
                    <tr>
                        <td>${p.tracking_id}</td>
                        <td>${p.sender || '-'}</td>
                        <td>${p.receiver || '-'}</td>
                        <td>${p.destination || '-'}</td>
                        <td>${p.status || '-'}</td>
                        <td>Ksh ${p.cost || 0}</td>
                        <td>
                            <div class="action-buttons">
                                <button onclick="updateStatus('${p.tracking_id}')" class="btn btn-success">Update</button>
                                <button onclick="deleteParcel('${p.tracking_id}')" class="btn btn-danger">Delete</button>
                            </div>
                        </td>
                    </tr>
                `;
            });
            document.getElementById('manage-table-body').innerHTML = html;
        })
        .catch(err => console.error(err));
}

// Update Status
function updateStatus(trackingId) {
    const newStatus = prompt('Enter new status (Registered, Dispatched, In Transit, Out For Delivery, Delivered, Cancelled):');
    
    if (!newStatus) return;
    
    axios.put(`${API_BASE}/parcel/${trackingId}/status`, { status: newStatus })
        .then(res => {
            showMessage('Status updated', 'success');
            loadManagedParcels();
        })
        .catch(err => showMessage('Update failed', 'error'));
}

// Calculate Cost
function calculateCost() {
    const data = {
        tracking_id: document.getElementById('calc-tracking').value,
        weight: document.getElementById('calc-weight').value,
        destination: document.getElementById('calc-destination').value,
        delivery_type: document.getElementById('calc-delivery').value
    };
    
    axios.post(`${API_BASE}/calculate-cost`, data)
        .then(res => {
            const b = res.data.breakdown;
            document.getElementById('breakdown-base').textContent = `Ksh ${b.base_cost}`;
            document.getElementById('breakdown-surcharge').textContent = `Ksh ${b.surcharge}`;
            document.getElementById('breakdown-total').textContent = `Ksh ${b.total_cost}`;
            document.getElementById('cost-breakdown').classList.remove('hidden');
        })
        .catch(err => showMessage('Calculation failed', 'error'));
}

// Load History
function loadHistory() {
    axios.get(`${API_BASE}/cost-history`)
        .then(res => {
            let html = '';
            res.data.history.forEach(h => {
                html += `
                    <tr>
                        <td>${h.tracking_id}</td>
                        <td>${h.weight}</td>
                        <td>${h.destination}</td>
                        <td>Ksh ${h.cost}</td>
                    </tr>
                `;
            });
            document.getElementById('history-body').innerHTML = html;
        })
        .catch(err => console.error(err));
}

// Generate Reports
function generateAllReport() {
    axios.get(`${API_BASE}/reports/all`)
        .then(res => displayReport(res.data.parcels))
        .catch(err => console.error(err));
}

function generateWeightReport() {
    axios.get(`${API_BASE}/reports/by-weight`)
        .then(res => displayReport(res.data.parcels))
        .catch(err => console.error(err));
}

function generateDestinationReport() {
    axios.get(`${API_BASE}/reports/by-destination`)
        .then(res => displayReport(res.data.parcels))
        .catch(err => console.error(err));
}

function generateStatistics() {
    axios.get(`${API_BASE}/reports/statistics`)
        .then(res => {
            let html = `
                <table>
                    <tr><td>Total Parcels:</td><td>${res.data.total_parcels}</td></tr>
                    <tr><td>Registered:</td><td>${res.data.registered}</td></tr>
                    <tr><td>Dispatched:</td><td>${res.data.dispatched}</td></tr>
                    <tr><td>In Transit:</td><td>${res.data.in_transit}</td></tr>
                    <tr><td>Out For Delivery:</td><td>${res.data.out_for_delivery}</td></tr>
                    <tr><td>Delivered:</td><td>${res.data.delivered}</td></tr>
                    <tr><td>Cancelled:</td><td>${res.data.cancelled}</td></tr>
                    <tr><td>Total Weight:</td><td>${res.data.total_weight} kg</td></tr>
                    <tr><td>Total Revenue:</td><td>Ksh ${res.data.total_revenue}</td></tr>
                    <tr><td>Average Weight:</td><td>${res.data.average_weight} kg</td></tr>
                    <tr><td>Average Cost:</td><td>Ksh ${res.data.average_cost}</td></tr>
                </table>
            `;
            document.getElementById('report-content').innerHTML = html;
            document.getElementById('report-container').classList.remove('hidden');
        })
        .catch(err => console.error(err));
}

function displayReport(parcels) {
    let html = '<table><thead><tr><th>TRACKING</th><th>SENDER</th><th>RECEIVER</th><th>DESTINATION</th><th>STATUS</th><th>WEIGHT</th><th>COST</th></tr></thead><tbody>';
    parcels.forEach(p => {
        html += `
            <tr>
                <td>${p.tracking_id}</td>
                <td>${p.sender || '-'}</td>
                <td>${p.receiver || '-'}</td>
                <td>${p.destination || '-'}</td>
                <td>${p.status || '-'}</td>
                <td>${p.weight || '-'} kg</td>
                <td>Ksh ${p.cost || 0}</td>
            </tr>
        `;
    });
    html += '</tbody></table>';
    document.getElementById('report-content').innerHTML = html;
    document.getElementById('report-container').classList.remove('hidden');
}

// Utilities
function showMessage(msg, type) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${type}`;
    msgDiv.textContent = msg;
    document.body.appendChild(msgDiv);
    setTimeout(() => msgDiv.remove(), 3000);
}

function deleteParcel(trackingId) {
    if (confirm('Delete this parcel?')) {
        showMessage('Parcel deleted', 'success');
        loadManagedParcels();
    }
}