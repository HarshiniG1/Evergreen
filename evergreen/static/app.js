'use strict';

const $ = id => document.getElementById(id);

const esc = value => String(value).replace(
  /[&<>"']/g,
  character => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  }[character])
);

const minutes = seconds => `${(seconds / 60).toFixed(1)} min`;

let data;
let lastPlan = null;
let busy = false;

// Fixed calculation settings: no unnecessary controls on screen.
function params() {
  const cart = Number($('cart').value);

  if (!Number.isInteger(cart) || cart < 1 || cart > 20) {
    throw new Error('Enter a cart capacity between 1 and 20 computers.');
  }

  return new URLSearchParams({
    accessible: '1',
    metric: 'seconds',
    speed: '0.8',
    wait: '1',
    cart: String(cart),
    handling: '120'
  });
}

async function api(path) {
  const response = await fetch(path);
  const result = await response.json();

  if (!response.ok) {
    throw new Error(
      'Unable to calculate the result. Check the CSV data and selected rooms.'
    );
  }

  return result;
}

async function safe(action) {
  if (busy) return;

  busy = true;
  $('error').textContent = '';

  for (const id of ['reload', 'route', 'plan', 'cart', 'source', 'target']) {
    $(id).disabled = true;
  }

  $('export').disabled = true;

  try {
    await action();
  } catch (error) {
    $('error').textContent = error.message;
  } finally {
    busy = false;

    for (const id of ['reload', 'route', 'plan', 'cart', 'source', 'target']) {
      $(id).disabled = false;
    }

    $('export').disabled = !lastPlan;
  }
}

function table(headers, rows) {
  return `
    <div class="table-wrap">
      <table>
        <thead>
          <tr>${headers.map(h => `<th>${esc(h)}</th>`).join('')}</tr>
        </thead>
        <tbody>
          ${rows.map(row => `
            <tr>${row.map(cell => `<td>${esc(cell)}</td>`).join('')}</tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;
}

function buildingFor(node) {
  const room = data.rooms.find(room => room.id === node);

  if (room) return room.building;

  return node.split(':')[0];
}

function draw(path = null) {
  const buildings = Object.fromEntries(
    data.buildings.map(building => [building.id, building])
  );

  let svg = `
    <defs>
      <pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse">
        <circle cx="1" cy="1" r="1" fill="#dae3d6"/>
      </pattern>
    </defs>
    <rect width="900" height="450" fill="url(#grid)"/>
    <text x="28" y="34" font-size="12" fill="#7a8a79">
      CAMPUS DIAGRAM • SAMPLE POSITIONS AND DISTANCES
    </text>
  `;

  for (const link of data.links) {
    if (link.kind !== 'walk') continue;

    const from = buildings[buildingFor(link.source)];
    const to = buildings[buildingFor(link.target)];

    if (!from || !to || from.id === to.id) continue;

    const accessible = link.accessible === '1';
    const enabled = link.enabled === '1';
    const offset = accessible ? 0 : -22;

    svg += `
      <path
        d="M${from.x},${from.y + offset} L${to.x},${to.y + offset}"
        stroke="${accessible ? '#b7cdbb' : '#abb9a8'}"
        stroke-width="4"
        fill="none"
        opacity="${enabled ? 1 : 0.3}"
        ${accessible ? '' : 'stroke-dasharray="7 5"'}
      />
      <text
        x="${(from.x + to.x) / 2}"
        y="${(from.y + to.y) / 2 + offset - 10}"
        font-size="12"
        fill="#64776b">
        ${link.meters} m${enabled ? '' : ' (closed)'}
      </text>
    `;
  }

  if (path) {
    for (const step of path.steps) {
      const from = buildings[buildingFor(step.source)];
      const to = buildings[buildingFor(step.target)];

      if (!from || !to || from.id === to.id) continue;

      svg += `
        <path
          d="M${from.x},${from.y} L${to.x},${to.y}"
          stroke="#e58a28"
          stroke-width="7"
          opacity=".85"
          fill="none"
        />
      `;
    }
  }

  for (const building of data.buildings) {
    svg += `
      <g>
        <circle
          cx="${building.x}" cy="${building.y}"
          r="35" fill="#176c50"/>
        <text
          x="${building.x}" y="${building.y + 5}"
          text-anchor="middle"
          font-size="14" font-weight="700" fill="white">
          ${esc(building.id)}
        </text>
        <text
          x="${building.x}" y="${building.y + 60}"
          text-anchor="middle"
          font-size="17" font-weight="650" fill="#17382c">
          ${esc(building.name)}
        </text>
        <text
          x="${building.x}" y="${building.y + 80}"
          text-anchor="middle"
          font-size="12" fill="#64776b">
          Target: ${esc(building.target_model)}
        </text>
      </g>
    `;
  }

  $('map').innerHTML = svg;
}

function clearRoute() {
  $('route-result').innerHTML = '';
  if (data) draw();
}

function invalidatePlan() {
  lastPlan = null;
  $('export').disabled = true;
  $('moved').textContent = '—';
  $('effort').textContent = '—';

  $('plan-result').innerHTML = `
    <p class="empty">
      Generate a plan to see proposed transfers and quantities.
    </p>
  `;
}

async function load() {
  data = await api('/api/data');

  for (const id of ['source', 'target']) {
    $(id).innerHTML = data.rooms.map(room => `
      <option value="${esc(room.id)}">
        ${esc(room.id)} · Floor ${room.floor}
      </option>
    `).join('');
  }

  if (data.rooms.some(room => room.id === 'MOR-BUREAU')) {
    $('source').value = 'MOR-BUREAU';
  }

  if (data.rooms.some(room => room.id === 'MRN-302')) {
    $('target').value = 'MRN-302';
  } else if (data.rooms.length > 1) {
    $('target').selectedIndex = 1;
  }

  $('total').textContent = data.inventory.reduce(
    (total, item) => total + item.quantity,
    0
  );

  const inventoryByRoom = new Map();

for (const item of data.inventory) {
  if (!inventoryByRoom.has(item.room)) {
    inventoryByRoom.set(item.room, {
      category5: 0,
      nonCategory5: 0
    });
  }

  const counts = inventoryByRoom.get(item.room);

  if (item.model === 'CAT-5') {
    counts.category5 += Number(item.quantity);
  } else {
    counts.nonCategory5 += Number(item.quantity);
  }
}

$('inventory').innerHTML = table(
  ['Room', 'Category 5 computers', 'Non-category 5 computers', 'Total'],
  [...inventoryByRoom.entries()].map(([room, counts]) => [
    room,
    counts.category5,
    counts.nonCategory5,
    counts.category5 + counts.nonCategory5
  ])
);

  $('building-info').textContent = data.buildings.map(building => {
    const rooms = data.rooms.filter(
      room => room.building === building.id
    );

    const floors = [...new Set(rooms.map(room => room.floor))]
      .sort((a, b) => a - b);

    return `${building.name}: ${rooms.length} rooms/access points`
      + ` · Recorded floors: ${floors.join(', ') || 'none'}`;
  }).join(' | ');

  invalidatePlan();
  clearRoute();
}

function stepLabel(step) {
  if (step.kind === 'elevator') return 'Elevator';

  if (step.kind === 'stairs') return 'Stairs';

  return buildingFor(step.source) === buildingFor(step.target)
    ? 'Corridor'
    : 'Outdoor path';
}

async function getRoute() {
  clearRoute();

  const query = params();
  query.set('source', $('source').value);
  query.set('target', $('target').value);

  const path = await api(`/api/route?${query}`);
  draw(path);

  if (!path) {
    $('route-result').innerHTML = `
      <div class="warning">
        No cart-accessible route is available between these rooms.
      </div>
    `;
    return;
  }

  $('route-result').innerHTML = `
    <p>
      <b>${Math.round(path.meters)} m · ${minutes(path.seconds)}</b>
      <br>
      <small>Estimated one-way journey</small>
    </p>
    ${path.steps.length ? `
      <ol>
        ${path.steps.map(step => `
          <li>
            ${esc(step.source)} → ${esc(step.target)}
            <br>
            ${stepLabel(step)} · ${minutes(step.seconds)}
          </li>
        `).join('')}
      </ol>
    ` : '<p>The starting room and destination are the same.</p>'}
  `;
}

// Generate English stock/capacity warnings from the assignment results.
function planWarnings(result) {
  const models = new Set([
    ...data.inventory.map(item => item.model),
    ...data.buildings.map(building => building.target_model)
  ]);

  const targets = Object.fromEntries(
    data.buildings.map(building => [
      building.id,
      building.target_model
    ])
  );

  const warnings = [];

  for (const model of models) {
    const available = data.inventory
      .filter(item => item.model === model)
      .reduce((sum, item) => sum + item.quantity, 0);

    const required = data.rooms
      .filter(room => targets[room.building] === model)
      .reduce((sum, room) => sum + room.capacity, 0);

    const assigned = result.assignments
      .filter(item => item.model === model)
      .reduce((sum, item) => sum + item.quantity, 0);

    if (available > assigned) {
      warnings.push(
        `${model}: ${available - assigned} computer(s) remain unassigned. `
        + 'Keep them in their current rooms or arrange temporary storage.'
      );
    }

    if (required > assigned) {
      warnings.push(
        `${model}: ${required - assigned} target position(s) remain unfilled. `
        + 'Stock may be insufficient or routes unavailable.'
      );
    }
  }

  return warnings;
}

async function getPlan() {
  const query = params();

  invalidatePlan();

  const result = await api(`/api/plan?${query}`);
  lastPlan = result;

  $('moved').textContent = result.moved;
  $('effort').textContent =
    `${(result.estimated_seconds / 3600).toFixed(1)} h`;

  let html = `
    <div class="success">
      ${result.retained} computers stay in place.
      ${result.moved} computers are proposed for transfer.
    </div>
  `;

  html += planWarnings(result).map(warning => `
    <div class="warning">${esc(warning)}</div>
  `).join('');

  if (result.moves.length) {
    html += `
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Category</th>
              <th>From → To</th>
              <th>Computers</th>
              <th>Cart trips</th>
              <th>One-way distance</th>
              <th>Transfer time</th>
              <th>Route</th>
            </tr>
          </thead>
          <tbody>
            ${result.moves.map((move, index) => `
              <tr>
                <td>${esc(move.model)}</td>
                <td>${esc(move.source)} → ${esc(move.target)}</td>
                <td>${move.quantity}</td>
                <td>${move.trips}</td>
                <td>${Math.round(move.route.meters)} m</td>
                <td>${minutes(move.estimated_seconds)}</td>
                <td>
                  <button data-move="${index}">View</button>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
  } else {
    html += '<p>No computer transfers were assigned.</p>';
  }

  html += `
    <p class="hint">
      Destinations minimize total journey time per computer.
      Cart trip estimates are calculated after assignment.
      This is not an optimized team tour.
    </p>
  `;

  if (result.moves.length) {
    html += `
      <div class="warning">
        Coordinate transfers or reserve temporary storage before execution.
        This table does not specify transfer order.
        A full room must release computers before receiving replacements.
      </div>
    `;
  }

  $('plan-result').innerHTML = html;

  for (const button of $('plan-result').querySelectorAll('[data-move]')) {
    button.onclick = () => {
      if (busy || !lastPlan) return;

      const move = lastPlan.moves[Number(button.dataset.move)];
      $('source').value = move.source;
      $('target').value = move.target;

      safe(getRoute);
    };
  }
}

$('reload').onclick = () => safe(load);
$('route').onclick = () => safe(getRoute);
$('plan').onclick = () => safe(getPlan);

$('cart').addEventListener('input', invalidatePlan);
$('source').addEventListener('change', clearRoute);
$('target').addEventListener('change', clearRoute);

$('export').onclick = () => {
  if (!lastPlan || busy) return;

  const rows = [
    [
      'category',
      'source',
      'destination',
      'computers',
      'cart_trips',
      'one_way_meters',
      'one_way_seconds',
      'estimated_transfer_seconds'
    ],
    ...lastPlan.moves.map(move => [
      move.model,
      move.source,
      move.target,
      move.quantity,
      move.trips,
      move.route.meters,
      move.route.seconds,
      move.estimated_seconds
    ])
  ];

  // Prevent spreadsheet programs from interpreting text as formulas.
  const quote = value => {
    let text = String(value);

    if (/^[=+\-@\t\r]/.test(text)) {
      text = "'" + text;
    }

    return '"' + text.replace(/"/g, '""') + '"';
  };

  const csv = '\ufeff' + rows
    .map(row => row.map(quote).join(','))
    .join('\r\n');

  const blob = new Blob(
    [csv],
    { type: 'text/csv;charset=utf-8' }
  );``

  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');

  link.href = url;
  link.download = 'evergreen_transfers.csv';
  link.click();

  setTimeout(() => URL.revokeObjectURL(url), 1000);
};

safe(load);