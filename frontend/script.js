// Parcel Delivery Tracking System - Frontend JavaScript

const API_BASE = 'http://localhost:5000/api';

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeNavigation();
    loadDashboard();
});

// Navigation
function initializeNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    const menuToggle = document.querySelector('.menu-toggle');
    const sidebar = document.querySelector('.sidebar');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const section = link.dataset.section;
            showSection(section);
            
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            
            if (sidebar.classList.contains('active')) {
                sidebar.classList.remove('active');
            }
        });
    });

    menuToggle.addEventListener('click', () => {
        sidebar.classList.toggle('active');
    });
}

function showSection(sectionId) {
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => section.classList.remove('active'));
    
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.add('active');
        
        // Load data based on section
        if (sectionId === 'dashboard') loadDashboard();
        else if (sectionId === 'parcels') loadParcels();
        else if (sectionId === 'queue') loadDeliveryQueue();
        else if (sectionId === 'analytics') loadComplexityAnalysis();
    }
}

// DASHBOARD
function loadDashboard() {
    axios.get(`${API_BASE}/system-stats`)
        .then(response => {
            const stats = response.data;
            
            // Update stat cards
            document.getElementById('stat-pending').textContent = stats.status_distribution.pending || 0;
            document.getElementById('stat-transit').textContent = stats.status_distribution.in_transit || 0;
            document.getElementById('stat-delivery').textContent = stats.status_distribution.out_for_delivery || 0;
            document.getElementById('stat-delivered').textContent = stats.status_distribution.delivered || 0;
            
            // Update system stats
            const statsHtml = `
                <ul class="stats-list">
                    <li><strong>Total Parcels:</strong> <span>${stats.total_parcels}</span></li>
                    <li><strong>Queue Size:</strong> <span>${stats.queue_size}</span></li>
                    <li><strong>Data Structures:</strong> <span>${stats.data_structures_used.length}</span></li>
                    <li><strong>Algorithms:</strong> <span>${stats.algorithms_used.length}</span></li>
                </ul>
            `;
            document.getElementById('system-stats').innerHTML = statsHtml;
        })
        .catch(error => showMessage('Error loading dashboard', 'error'));
}

// TRACK PARCEL
function searchParcel() {
    const trackingId = document.getElementById('tracking-id').value.trim();
    
    if (!trackingId) {
        showMessage('Please enter a tracking ID', 'error');
        return;
    }
    
    axios.get(`${API_BASE}/parcels/${trackingId}`)
        .then(response => {
            const parcel = response.data;
            
            let detailsHtml = `
                <div class="tracking-details">
                    <h3>Tracking ID: ${parcel.tracking_id}</h3>
                    <div class="details-grid">
                        <div>
                            <strong>Sender:</strong> ${parcel.sender}
                        </div>
                        <div>
                            <strong>Recipient:</strong> ${parcel.recipient}
                        </div>
                        <div>
                            <strong>Origin:</strong> ${parcel.origin}
                        </div>
                        <div>
                            <strong>Destination:</strong> ${parcel.destination}
                        </div>
                        <div>
                            <strong>Status:</strong> <span class="badge ${parcel.status}">${parcel.status}</span>
                        </div>
                        <div>
                            <strong>Weight:</strong> ${parcel.weight} kg
                        </div>
                        <div>
                            <strong>Priority:</strong> ${parcel.priority}/10
                        </div>
                        <div>
                            <strong>Created:</strong> ${new Date(parcel.created_at).toLocaleString()}
                        </div>
                    </div>
                </div>
            `;
            
            document.getElementById('tracking-details').innerHTML = detailsHtml;
            
            // Build timeline
            let timelineHtml = '<h4 style="margin-top: 30px; margin-bottom: 20px;">Location History:</h4>';
            if (parcel.location_history.length > 0) {
                timelineHtml += parcel.location_history.map((location, index) => `
                    <div class="timeline-item">
                        <div class="timeline-item-content">
                            <strong>Location ${index + 1}:</strong> ${location}
                            <small>Update #${index + 1}</small>
                        </div>
                    </div>
                `).join('');
            } else {
                timelineHtml += '<p style="color: var(--text-secondary);">No location updates yet</p>';
            }
            
            document.getElementById('location-history').innerHTML = timelineHtml;
            document.getElementById('track-result').classList.remove('hidden');
        })
        .catch(error => {
            showMessage('Parcel not found', 'error');
            document.getElementById('track-result').classList.add('hidden');
        });
}

// CREATE PARCEL
function createParcel(event) {
    event.preventDefault();
    
    const formData = {
        sender: document.querySelector('input[name="sender"]').value,
        recipient: document.querySelector('input[name="recipient"]').value,
        origin: document.querySelector('input[name="origin"]').value,
        destination: document.querySelector('input[name="destination"]').value,
        weight: document.querySelector('input[name="weight"]').value,
        priority: document.querySelector('input[name="priority"]').value
    };
    
    axios.post(`${API_BASE}/parcels`, formData)
        .then(response => {
            showMessage(`Parcel created! Tracking ID: ${response.data.tracking_id}`, 'success');
            document.getElementById('create-form').reset();
        })
        .catch(error => showMessage('Error creating parcel', 'error'));
}

// LIST PARCELS
function loadParcels() {
    const sortBy = document.getElementById('sort-by').value || 'priority';
    
    axios.get(`${API_BASE}/parcels?sort_by=${sortBy}`)
        .then(response => {
            const parcels = response.data.parcels;
            
            let tableHtml = `
                <table>
                    <thead>
                        <tr>
                            <th>Tracking ID</th>
                            <th>Sender</th>
                            <th>Recipient</th>
                            <th>Origin</th>
                            <th>Destination</th>
                            <th>Status</th>
                            <th>Priority</th>
                        </tr>
                    </thead>
                    <tbody>
            `;
            
            parcels.forEach(parcel => {
                tableHtml += `
                    <tr>
                        <td><strong>${parcel.tracking_id}</strong></td>
                        <td>${parcel.sender}</td>
                        <td>${parcel.recipient}</td>
                        <td>${parcel.origin}</td>
                        <td>${parcel.destination}</td>
                        <td><span class="badge ${parcel.status}">${parcel.status}</span></td>
                        <td>${parcel.priority}/10</td>
                    </tr>
                `;
            });
            
            tableHtml += `
                    </tbody>
                </table>
            `;
            
            document.getElementById('parcels-table').innerHTML = tableHtml;
        })
        .catch(error => showMessage('Error loading parcels', 'error'));
}

// DELIVERY QUEUE
function loadDeliveryQueue() {
    axios.get(`${API_BASE}/delivery-queue`)
        .then(response => {
            const data = response.data;
            
            let queueHtml = `
                <h3>Delivery Queue Status</h3>
                <div style="margin: 20px 0;">
                    <p><strong>Total in Queue:</strong> ${data.queue_size} parcels</p>
                </div>
            `;
            
            if (data.next_to_deliver) {
                queueHtml += `
                    <div class="card" style="background: rgba(16, 185, 129, 0.1); border-left: 4px solid var(--success);">
                        <h4>🎯 Next Parcel for Delivery</h4>
                        <p><strong>Tracking ID:</strong> ${data.next_to_deliver.tracking_id}</p>
                        <p><strong>Recipient:</strong> ${data.next_to_deliver.recipient}</p>
                        <p><strong>Destination:</strong> ${data.next_to_deliver.destination}</p>
                        <p><strong>Priority:</strong> ${data.next_to_deliver.priority}/10</p>
                    </div>
                `;
            } else {
                queueHtml += '<p style="color: var(--text-secondary);">No parcels in delivery queue</p>';
            }
            
            document.getElementById('queue-info').innerHTML = queueHtml;
        })
        .catch(error => showMessage('Error loading delivery queue', 'error'));
}

// ROUTE OPTIMIZATION
function optimizeRoute() {
    const start = document.getElementById('route-start').value.trim();
    const end = document.getElementById('route-end').value.trim();
    
    if (!start || !end) {
        showMessage('Please enter both start and end locations', 'error');
        return;
    }
    
    axios.post(`${API_BASE}/route-optimization`, { start, end })
        .then(response => {
            const route = response.data;
            
            let routeHtml = `
                <h3>🗺️ Optimal Route</h3>
                <div style="margin: 20px 0;">
                    <p><strong>From:</strong> ${route.start}</p>
                    <p><strong>To:</strong> ${route.end}</p>
                    <p><strong>Optimal Distance:</strong> ${route.optimal_distance.toFixed(2)} km</p>
                    <p><strong>Algorithm:</strong> ${route.algorithm}</p>
                </div>
                <div>
                    <h4>Route Path:</h4>
                    <p>${route.optimal_path.join(' → ')}</p>
                </div>
            `;
            
            document.getElementById('route-details').innerHTML = routeHtml;
            document.getElementById('route-result').classList.remove('hidden');
        })
        .catch(error => showMessage('Error optimizing route', 'error'));
}

// COMPLEXITY ANALYSIS
function loadComplexityAnalysis() {
    axios.get(`${API_BASE}/algorithm-analysis`)
        .then(response => {
            const algorithms = response.data.algorithms;
            
            let analysisHtml = '<h3>Algorithm Complexity Analysis</h3><table><thead><tr><th>Algorithm</th><th>Time Complexity</th><th>Space Complexity</th></tr></thead><tbody>';
            
            for (const [algo, complexity] of Object.entries(algorithms)) {
                analysisHtml += `
                    <tr>
                        <td><strong>${algo.replace(/_/g, ' ').toUpperCase()}</strong></td>
                        <td>${complexity.time}</td>
                        <td>${complexity.space}</td>
                    </tr>
                `;
            }
            
            analysisHtml += '</tbody></table>';
            
            document.getElementById('complexity-analysis').innerHTML = analysisHtml;
        })
        .catch(error => showMessage('Error loading complexity analysis', 'error'));
}

// UTILITIES
function showMessage(message, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.innerHTML = `<i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i> ${message}`;
    
    const section = document.querySelector('.section.active');
    section.insertBefore(messageDiv, section.firstChild);
    
    setTimeout(() => messageDiv.remove(), 4000);
}
