const API  = '';   // same origin
const WS   = `ws://${location.host}/ws`;
const MAX_POINTS = 50;

// ── Chart ─────────────────────────────────────────────────────────────────────
const ctx   = document.getElementById('chart-moisture').getContext('2d');
const chart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: [],
    datasets: [{
      label: 'Soil Moisture (%)',
      data: [],
      borderColor: '#22c55e',
      backgroundColor: 'rgba(34,197,94,0.1)',
      tension: 0.3,
      fill: true,
      pointRadius: 2,
    }],
  },
  options: {
    animation: false,
    scales: {
      x: { ticks: { color: '#94a3b8', maxTicksLimit: 8 }, grid: { color: '#1e293b' } },
      y: { min: 0, max: 100, ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
    },
    plugins: { legend: { labels: { color: '#e2e8f0' } } },
  },
});

function pushPoint(ts, value) {
  const label = new Date(ts).toLocaleTimeString();
  chart.data.labels.push(label);
  chart.data.datasets[0].data.push(value);
  if (chart.data.labels.length > MAX_POINTS) {
    chart.data.labels.shift();
    chart.data.datasets[0].data.shift();
  }
  chart.update();
}

// ── UI update ─────────────────────────────────────────────────────────────────
function updateCards(data) {
  document.getElementById('val-moisture').textContent = data.soil_moisture?.toFixed(1) ?? '--';
  document.getElementById('val-temp').textContent     = data.temperature?.toFixed(1)   ?? '--';
  document.getElementById('val-humidity').textContent = data.humidity?.toFixed(1)      ?? '--';
  document.getElementById('val-pump').textContent     = data.pump_on ? '🟢 ON' : '🔴 OFF';
  pushPoint(data.timestamp ?? Date.now(), data.soil_moisture);
}

// ── WebSocket ─────────────────────────────────────────────────────────────────
function connect() {
  const ws  = new WebSocket(WS);
  const dot = document.getElementById('status-dot');

  ws.onopen  = () => dot.classList.add('connected');
  ws.onclose = () => { dot.classList.remove('connected'); setTimeout(connect, 3000); };
  ws.onmessage = (e) => { try { updateCards(JSON.parse(e.data)); } catch {} };
}

connect();

// ── Pump control ───────────────────────────────────────────────────────────────
async function controlPump(action) {
  const msg = document.getElementById('pump-status-msg');
  msg.textContent = `Sending ${action}…`;
  try {
    const res = await fetch(`${API}/api/pump/control`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action }),
    });
    const data = await res.json();
    msg.textContent = `Pump ${data.action} command sent`;
  } catch (err) {
    msg.textContent = 'Error: ' + err.message;
  }
}

// ── Load historical data on startup ───────────────────────────────────────────
(async () => {
  try {
    const res      = await fetch(`${API}/api/readings?limit=50`);
    const readings = await res.json();
    readings.reverse().forEach(r => {
      pushPoint(r.timestamp, r.soil_moisture);
    });
    if (readings.length) updateCards(readings[0]);
  } catch {}
})();
