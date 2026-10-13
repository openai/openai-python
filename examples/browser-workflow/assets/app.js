const variant = new URL(location.href).searchParams.get('fixture') || 'A';
const link = (route) => `/${route}?fixture=${encodeURIComponent(variant)}`;
const esc = (s) =>
  String(s).replaceAll(
    /[&<>"']/gu,
    (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c],
  );
const read = (key, fallback) => {
  const stored = `workflow.${variant}.${key}`;
  try {
    return JSON.parse(localStorage.getItem(stored) || JSON.stringify(fallback));
  } catch (error) {
    if (!(error instanceof SyntaxError)) {
      throw error;
    }
    localStorage.removeItem(stored);
    return fallback;
  }
};
const records = (key) => {
  const value = read(key, {});
  if (value === null || typeof value !== 'object' || Array.isArray(value)) {
    localStorage.removeItem(`workflow.${variant}.${key}`);
    return Object.create(null);
  }
  return Object.assign(Object.create(null), value);
};
const save = (key, value) => localStorage.setItem(`workflow.${variant}.${key}`, JSON.stringify(value));
const brands = {
  '/inbox': ['Postbox · Requests', '#165d52'],
  '/schedule': ['Roomboard · Availability', '#334d8f'],
  '/dispatch': ['Dispatch · Outgoing', '#783953'],
};

const render = () => {
  const fixtures = window.workflowFixtures;
  const fixture = Object.hasOwn(fixtures, variant) ? fixtures[variant] : undefined;
  const [name, colour] = brands[location.pathname] || brands['/inbox'];
  document.documentElement.style.setProperty('--brand', colour);
  document.title = name;
  document.querySelector('#bar').innerHTML = `<b>${name}</b><nav>
    <button data-route="inbox">Requests</button><button data-route="schedule">Rooms</button><button data-route="dispatch">Outgoing</button>
    </nav><span>Local practice · ${esc(variant)}</span>`;
  if (!fixture) {
    document.querySelector('#app').textContent =
      'Unknown fixture. Use A or B, or supply a fixture data file.';
    return;
  }
  const active = fixture.requests.find((r) => r.id === read('selected', ''));
  const bookings = records('bookings');
  const sent = records('correspondence');
  let body;
  if (location.pathname === '/schedule') {
    body = `<h1>Room availability</h1><p class="muted">Select the least expensive room that meets every rule.</p>
      <div class="rule">${active ? `${esc(active.id)} · ${esc(active.name)} · ${esc(active.time)} · ${esc(active.people)} people · ${esc(active.equipment)} · up to $${esc(active.budget)}` : 'Open a request in Postbox first.'}</div>
      ${active && bookings[active.id] ? `<section data-record-id="${esc(active.id)}"><p class="receipt">Saved ${esc(bookings[active.id].slot)} for ${esc(active.id)}. Open Outgoing to send.</p><p>Revise removes this local booking and its local confirmation record so you can choose again.</p><button data-revise="${esc(active.id)}">Revise booking ${esc(active.id)}</button></section>` : ''}
      <div class="cards">${fixture.slots
        .map(
          (s) => `<article data-record-id="${esc(s.id)}"><h2>${esc(s.room)} · ${esc(s.id)}</h2>
      <p>${esc(s.time)} · seats ${esc(s.capacity)} · ${esc(s.equipment.join(', '))} · $${esc(s.price)}</p>
      <button data-slot="${esc(s.id)}" ${!active || bookings[active.id] ? 'disabled' : ''}>Reserve ${esc(s.id)} ${esc(s.room)}</button></article>`,
        )
        .join('')}</div>`;
  } else if (location.pathname === '/dispatch') {
    body = `<h1>Confirmation outbox</h1><p>Review the saved booking. Sending creates one local correspondence record.</p>
      <div class="cards">${
        Object.entries(bookings)
          .map(([id, booking]) => {
            const r = fixture.requests.find((item) => item.id === id);
            const slot = fixture.slots.find((item) => item.id === booking?.slot);
            if (
              !r ||
              !booking ||
              typeof booking !== 'object' ||
              Array.isArray(booking) ||
              booking.request !== id ||
              !slot ||
              slot.time !== booking.time
            ) {
              return `<article data-record-id="${esc(id)}"><h2>${esc(id)}</h2>
                <p>This saved booking no longer matches an available request and room.</p>
                <button data-revise="${esc(id)}">Remove saved booking ${esc(id)}</button></article>`;
            }
            return `<article data-record-id="${esc(id)}"><h2>${esc(id)} · ${esc(r.name)}</h2><p>To ${esc(r.recipient)}</p>
          <p>Reservation ${esc(booking.slot)} at ${esc(booking.time)}</p>
          <button data-send="${esc(id)}" ${sent[id] ? 'disabled' : ''}>Send ${esc(id)} to ${esc(r.recipient)}</button>
          ${sent[id] ? '<p class="receipt">Confirmation saved in outgoing mail.</p>' : ''}</article>`;
          })
          .join('') || '<p>No saved bookings. Check Roomboard.</p>'
      }</div>`;
  } else {
    body = `<h1>Resource requests</h1><p class="muted">Pick the requested job, compare rooms, then send a confirmation.</p>
      <div class="rule">Complete request ${esc(fixture.requestId)}. ${esc(fixture.task)}</div>
      <div class="cards">${fixture.requests
        .map(
          (r) => `<article data-record-id="${esc(r.id)}"><h2>${esc(r.id)} · ${esc(r.name)}</h2>
        <p>${esc(r.time)} · ${esc(r.people)} people · requires ${esc(r.equipment)} · budget $${esc(r.budget)}</p>
        <p class="muted">${esc(r.recipient)}</p>
        <button data-request="${esc(r.id)}">Open ${esc(r.id)}</button>
      </article>`,
        )
        .join('')}</div>`;
  }
  document.querySelector('#app').innerHTML = body;
  for (const button of document.querySelectorAll('[data-route]')) {
    button.addEventListener('click', () => {
      location.href = link(button.dataset.route);
    });
  }
  for (const button of document.querySelectorAll('[data-request]')) {
    button.addEventListener('click', () => {
      save('selected', button.dataset.request);
      location.href = link('schedule');
    });
  }
  for (const button of document.querySelectorAll('[data-slot]')) {
    button.addEventListener('click', () => {
      const latest = records('bookings');
      if (active && !latest[active.id]) {
        const slot = fixture.slots.find((s) => s.id === button.dataset.slot);
        latest[active.id] = { request: active.id, slot: slot.id, time: slot.time };
        save('bookings', latest);
      }
      render();
    });
  }
  for (const button of document.querySelectorAll('[data-revise]')) {
    button.addEventListener('click', () => {
      const id = button.dataset.revise;
      const latest = records('bookings');
      const confirmations = records('correspondence');
      Reflect.deleteProperty(latest, id);
      Reflect.deleteProperty(confirmations, id);
      save('bookings', latest);
      save('correspondence', confirmations);
      render();
    });
  }
  for (const button of document.querySelectorAll('[data-send]')) {
    button.addEventListener('click', () => {
      const id = button.dataset.send;
      const latest = records('correspondence');
      const booked = records('bookings')[id];
      if (booked && !latest[id]) {
        latest[id] = {
          request: id,
          slot: booked.slot,
          recipient: fixture.requests.find((r) => r.id === id).recipient,
        };
        save('correspondence', latest);
      }
      render();
    });
  }
};
render();
