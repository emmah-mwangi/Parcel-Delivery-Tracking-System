const $ = sel => document.querySelector(sel);
const views = {
  dashboard: $('#dashboard'),
  register: $('#register'),
  track: $('#track'),
  manage: $('#manage'),
  cost: $('#cost')
}

function show(view){
  Object.values(views).forEach(v=>v.classList.add('hidden'))
  view.classList.remove('hidden')
}

$('#nav-dashboard').onclick = () => show(views.dashboard)
$('#nav-register').onclick = () => show(views.register)
$('#nav-track').onclick = () => show(views.track)
$('#nav-manage').onclick = () => show(views.manage)
$('#nav-cost').onclick = () => show(views.cost)

// fetch and render stats
async function loadStats(){
  const res = await fetch('/api/reports')
  const data = await res.json()
  $('#total-parcels').textContent = data.total_parcels || 0
  $('#avg-weight').textContent = data.average_weight_kg || 0
  $('#by-status').textContent = JSON.stringify(data.by_status || {}, null, 2)
}

// register form
$('#register-form').onsubmit = async e => {
  e.preventDefault()
  const form = e.target
  const body = Object.fromEntries(new FormData(form).entries())
  body.weight_kg = parseFloat(body.weight_kg) || 0
  const res = await fetch('/api/parcels',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)})
  const json = await res.json()
  $('#register-result').textContent = 'Registered: ' + (json.tracking_number || JSON.stringify(json))
  form.reset()
  await reloadParcels()
  await loadStats()
}

// track form
$('#track-form').onsubmit = async e => {
  e.preventDefault()
  const t = new FormData(e.target).get('tracking')
  const res = await fetch('/api/parcels/'+encodeURIComponent(t))
  const json = await res.json()
  $('#track-result').textContent = JSON.stringify(json, null, 2)
}

// cost form
$('#cost-form').onsubmit = async e => {
  e.preventDefault()
  const body = Object.fromEntries(new FormData(e.target).entries())
  body.weight_kg = parseFloat(body.weight_kg) || 0
  body.distance_km = parseFloat(body.distance_km) || 0
  const res = await fetch('/api/calculate_cost',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)})
  const json = await res.json()
  $('#cost-result').textContent = 'Estimated cost: ' + (json.cost !== undefined ? json.cost : JSON.stringify(json))
}

// manage table
async function reloadParcels(){
  const res = await fetch('/api/parcels')
  const list = await res.json()
  const tbody = $('#parcels-table tbody')
  tbody.innerHTML = ''
  for(const p of list){
    const tr = document.createElement('tr')
    tr.innerHTML = `<td>${p.tracking_number||''}</td><td>${p.sender_name||''}</td><td>${p.receiver_name||''}</td><td>${p.destination||''}</td><td>${p.weight_kg||''}</td><td>${p.status||''}</td><td></td>`
    const actions = tr.querySelector('td:last-child')
    const up = document.createElement('button')
    up.textContent = 'Mark Delivered'
    up.onclick = async ()=>{
      await fetch('/api/parcels/'+encodeURIComponent(p.tracking_number)+'/status',{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({status:'delivered',location:'destination'})})
      await reloadParcels()
      await loadStats()
    }
    actions.appendChild(up)
    tbody.appendChild(tr)
  }
}

// initial load
show(views.dashboard)
reloadParcels()
loadStats()
