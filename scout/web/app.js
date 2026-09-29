/* Scout: find fashion shops in Berlin that big platforms miss.
   Everything a run returns was written by a model that read the open web, so it is
   treated as untrusted: every value is escaped, and only http(s) links become links. */
(() => {
  'use strict';

  const T = {
    en: {
      title: 'Find the shops the platforms miss.',
      sub: 'Tell Scout what you are looking for. It searches OpenStreetMap and the web, in German and in the community’s own language, and checks every shop before it shows it to you. Every fact has a source.',
      briefLabel: 'What are you looking for?', briefPlaceholder: 'A hanbok for a wedding',
      find: 'Find shops', finding: 'Scout is searching', recorded: 'Recorded searches', replay: 'Replay',
      sampleOption: 'Sample search (invented shops)',
      logLabel: 'What Scout is doing', queueLabel: 'Shops',
      foot: 'Scout runs on NVIDIA Nemotron through Nebius Token Factory and searches with Tavily and OpenStreetMap, and with Google Maps when a key is set. It checks robots.txt before it reads a page and records business contact details only.',
      keysOk: 'Model: {model}. Search: {sources}.', searchTwo: 'Tavily and OpenStreetMap', searchThree: 'Tavily, OpenStreetMap and Google Maps',
      googleOff: 'Google Maps is set up but stays off until Zero Data Retention is on in Nebius and NEBIUS_ZERO_DATA_RETENTION=on is in scout/.env.',
      keysMissing: 'Keys are missing: {names}. Put them in scout/.env and start Scout again. The sample search works without them.',
      contactMissing: 'Set CMX_BOT_CONTACT in scout/.env so the sites and maps Scout reads can see who is asking.',
      stepsEmpty: 'No steps yet.', emptyH: 'No search yet.',
      emptyB: 'Write what you are looking for, or replay the sample search to see how Scout works.',
      sampleBanner: 'Sample search · invented shops, for trying the screen',
      replayBanner: 'Replay of a recorded search · {date}',
      count: ['{n} shop found. {a} confirmed, {p} not yet confirmed.', '{n} shops found. {a} confirmed, {p} not yet confirmed.'],
      noneFound: 'Scout found no shop for this yet.',
      hidden: ['{h} of {n} does not show up in a plain web search for this.', '{h} of {n} don’t show up in a plain web search for this.'],
      cost: '{searches} web searches, {maps} map searches and {reads} pages read. {credits} Tavily credits, {tokens} tokens through Nemotron.',
      verdict: { accept: 'Confirmed', revisit: 'Not yet confirmed', reject: 'Left out' },
      step: { baseline: 'Plain search', map: 'Map', map_failed: 'Map', google: 'Google Maps', google_failed: 'Google Maps', search: 'Search', read: 'Read', blocked: 'Stayed out', read_failed: 'No answer', platform: 'Online shop', submit_rejected: 'Sent back', submit: 'Done', located: 'On the map' },
      results: ['{n} result', '{n} results'], forComparison: 'for comparison',
      places: ['{n} place on OpenStreetMap', '{n} places on OpenStreetMap'], around: 'around {place}',
      allFashion: 'all fashion shops', mapFailed: 'the map servers were busy',
      viaTavily: 'rendered through Tavily', viaOwn: 'read by our own fetcher',
      robots: 'robots.txt asks crawlers to stay out', feedYes: 'online shop on {p}', feedNo: 'no online shop feed',
      sentBack: ['{n} value outside the vocabulary', '{n} values outside the vocabulary'], submitted: ['{n} shop checked', '{n} shops checked'], chars: '{n} characters',
      located: '{k} of {n} shops', locatedMap: '{m} from OpenStreetMap', locatedAddress: '{a} from their address', locatedGoogle: '{g} as a Google Maps link',
      googlePlaces: ['{n} place on Google Maps', '{n} places on Google Maps'], googleFailed: 'Google Maps did not answer',
      googleOnly: 'Found on Google Maps. Places from Google are not drawn on this map.',
      facts: { website: 'Website', sells: 'Sells', address: 'Address', hours: 'Opening hours', status: 'Status', contact: 'Best way in', channels: 'Channels', languages: 'Languages' },
      hoursNote: 'as mapped on OpenStreetMap',
      status: { trading: 'Trading', closed: 'Closed', moved: 'Moved', unclear: 'Unclear' },
      visit: { yes: 'Visit in person', no: 'Online only', unconfirmed: 'Visiting not confirmed' },
      contact: { in_person: 'In person', email: 'Email', instagram: 'Instagram', phone: 'Phone', contact_form: 'Contact form', unknown: 'Unknown' },
      seen: { missed: 'Not in a plain web search', rank: 'Plain web search: #{n}', noSite: 'No website' },
      sourcesLabel: 'Sources', traced: 'Traced', notTraced: '[Not traced]', noSources: '[No source given]',
      untraced: '[{u} of {n} sources not traced]', crawlNo: '[robots.txt: Scout did not read this site]',
      onMap: 'On OpenStreetMap',
      actions: { directions: 'Directions', show: 'Show on map', google: 'Open in Google Maps' },
      leftOut: ['Checked and left out: {n} shop', 'Checked and left out: {n} shops'],
      map: { label: 'Map of the shops found. Use the arrow keys to move it.', zoomIn: 'Zoom in', zoomOut: 'Zoom out', none: 'None of these shops has a confirmed place to visit yet.', credit: '© OpenStreetMap contributors' },
      culture: { african: 'African', central_asian: 'Central Asian', south_asian: 'South Asian', middle_eastern: 'Middle Eastern', east_asian: 'East Asian', balkan: 'Balkan', latin_american: 'Latin American', modest: 'Modest', fusion: 'Fusion' },
      failed: 'Scout stopped. {why}', langLabel: 'Sprache wechseln', other: 'DE',
    },
    de: {
      title: 'Die Läden finden, die Plattformen übersehen.',
      sub: 'Sag Scout, was du suchst. Scout sucht auf OpenStreetMap und im Web, auf Deutsch und in der Sprache der Community, und prüft jeden Laden, bevor er dir angezeigt wird. Jede Angabe hat eine Quelle.',
      briefLabel: 'Was suchst du?', briefPlaceholder: 'Einen Hanbok für eine Hochzeit',
      find: 'Läden finden', finding: 'Scout sucht', recorded: 'Aufgezeichnete Suchen', replay: 'Abspielen',
      sampleOption: 'Beispielsuche (erfundene Läden)',
      logLabel: 'Was Scout gerade tut', queueLabel: 'Läden',
      foot: 'Scout läuft mit NVIDIA Nemotron über Nebius Token Factory und sucht mit Tavily und OpenStreetMap, mit einem Schlüssel auch in Google Maps. Vor dem Lesen einer Seite prüft Scout die robots.txt und erfasst nur geschäftliche Kontaktdaten.',
      keysOk: 'Modell: {model}. Suche: {sources}.', searchTwo: 'Tavily und OpenStreetMap', searchThree: 'Tavily, OpenStreetMap und Google Maps',
      googleOff: 'Google Maps ist eingerichtet, bleibt aber aus, bis Zero Data Retention in Nebius eingeschaltet ist und NEBIUS_ZERO_DATA_RETENTION=on in scout/.env steht.',
      keysMissing: 'Es fehlen Schlüssel: {names}. Trage sie in scout/.env ein und starte Scout neu. Die Beispielsuche funktioniert ohne sie.',
      contactMissing: 'Trage CMX_BOT_CONTACT in scout/.env ein, damit die Seiten und Karten, die Scout liest, sehen, wer fragt.',
      stepsEmpty: 'Noch keine Schritte.', emptyH: 'Noch keine Suche.',
      emptyB: 'Schreib, was du suchst, oder spiel die Beispielsuche ab, um zu sehen, wie Scout arbeitet.',
      sampleBanner: 'Beispielsuche · erfundene Läden, zum Ausprobieren',
      replayBanner: 'Aufgezeichnete Suche · {date}',
      count: ['{n} Laden gefunden. {a} bestätigt, {p} noch nicht bestätigt.', '{n} Läden gefunden. {a} bestätigt, {p} noch nicht bestätigt.'],
      noneFound: 'Scout hat dafür noch keinen Laden gefunden.',
      hidden: ['{h} von {n} taucht in einer normalen Websuche danach nicht auf.', '{h} von {n} tauchen in einer normalen Websuche danach nicht auf.'],
      cost: '{searches} Websuchen, {maps} Kartensuchen und {reads} gelesene Seiten. {credits} Tavily-Credits, {tokens} Tokens über Nemotron.',
      verdict: { accept: 'Bestätigt', revisit: 'Noch nicht bestätigt', reject: 'Aussortiert' },
      step: { baseline: 'Normale Suche', map: 'Karte', map_failed: 'Karte', google: 'Google Maps', google_failed: 'Google Maps', search: 'Suche', read: 'Gelesen', blocked: 'Draußen', read_failed: 'Keine Antwort', platform: 'Onlineshop', submit_rejected: 'Zurück', submit: 'Fertig', located: 'Auf der Karte' },
      results: ['{n} Treffer', '{n} Treffer'], forComparison: 'zum Vergleich',
      places: ['{n} Ort auf OpenStreetMap', '{n} Orte auf OpenStreetMap'], around: 'rund um {place}',
      allFashion: 'alle Modeläden', mapFailed: 'die Kartenserver waren ausgelastet',
      viaTavily: 'über Tavily gerendert', viaOwn: 'mit unserem eigenen Abruf gelesen',
      robots: 'robots.txt bittet Crawler, draußen zu bleiben', feedYes: 'Onlineshop auf {p}', feedNo: 'kein Onlineshop-Feed',
      sentBack: ['{n} Wert außerhalb des Vokabulars', '{n} Werte außerhalb des Vokabulars'], submitted: ['{n} Laden geprüft', '{n} Läden geprüft'], chars: '{n} Zeichen',
      located: '{k} von {n} Läden', locatedMap: '{m} über OpenStreetMap', locatedAddress: '{a} über ihre Adresse', locatedGoogle: '{g} als Google-Maps-Link',
      googlePlaces: ['{n} Ort auf Google Maps', '{n} Orte auf Google Maps'], googleFailed: 'Google Maps hat nicht geantwortet',
      googleOnly: 'Auf Google Maps gefunden. Orte von Google erscheinen nicht auf dieser Karte.',
      facts: { website: 'Website', sells: 'Sortiment', address: 'Adresse', hours: 'Öffnungszeiten', status: 'Status', contact: 'Am besten', channels: 'Kanäle', languages: 'Sprachen' },
      hoursNote: 'laut OpenStreetMap',
      status: { trading: 'In Betrieb', closed: 'Geschlossen', moved: 'Umgezogen', unclear: 'Unklar' },
      visit: { yes: 'Vor Ort besuchen', no: 'Nur online', unconfirmed: 'Besuch nicht bestätigt' },
      contact: { in_person: 'Persönlich', email: 'E-Mail', instagram: 'Instagram', phone: 'Telefon', contact_form: 'Kontaktformular', unknown: 'Unbekannt' },
      seen: { missed: 'Nicht in einer normalen Websuche', rank: 'Normale Websuche: Platz {n}', noSite: 'Keine Website' },
      sourcesLabel: 'Quellen', traced: 'Nachvollzogen', notTraced: '[Nicht nachvollzogen]', noSources: '[Keine Quelle angegeben]',
      untraced: '[{u} von {n} Quellen nicht nachvollzogen]', crawlNo: '[robots.txt: Scout hat diese Seite nicht gelesen]',
      onMap: 'Auf OpenStreetMap',
      actions: { directions: 'Route', show: 'Auf der Karte zeigen', google: 'In Google Maps öffnen' },
      leftOut: ['Geprüft und aussortiert: {n} Laden', 'Geprüft und aussortiert: {n} Läden'],
      map: { label: 'Karte der gefundenen Läden. Mit den Pfeiltasten verschieben.', zoomIn: 'Vergrößern', zoomOut: 'Verkleinern', none: 'Für keinen dieser Läden ist schon ein Ort zum Besuchen bestätigt.', credit: '© OpenStreetMap-Mitwirkende' },
      culture: { african: 'Afrikanisch', central_asian: 'Zentralasiatisch', south_asian: 'Südasiatisch', middle_eastern: 'Nahöstlich', east_asian: 'Ostasiatisch', balkan: 'Balkan', latin_american: 'Lateinamerikanisch', modest: 'Modest', fusion: 'Fusion' },
      failed: 'Scout hat angehalten. {why}', langLabel: 'Switch language', other: 'EN',
    },
  };
  const SHAPE = { african: 'circle', central_asian: 'square', south_asian: 'circle', middle_eastern: 'hexagon',
    east_asian: 'diamond', balkan: 'diamond', latin_american: 'triangle', modest: 'triangle', fusion: 'ring' };
  const PLATFORM = { shopify: 'Shopify', woocommerce: 'WooCommerce' };
  const TILES = 'https://tile.openstreetmap.org';
  const TILE = 256, MIN_ZOOM = 10, MAX_ZOOM = 18;
  const BERLIN = { lat: 52.515, lon: 13.405, zoom: 11 };

  const $ = (id) => document.getElementById(id);
  const esc = (v) => String(v ?? '').replace(/[&<>"']/g,
    (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const fill = (text, vars = {}) => text.replace(/\{(\w+)\}/g, (_, k) => esc(vars[k] ?? ''));
  const plural = (forms, count, vars) => fill(forms[Number(count) === 1 ? 0 : 1], vars);

  const state = { lang: 'en', status: null, run: null, steps: [], shops: null, usage: null, busy: false,
    problem: null, picked: -1 };
  try { state.lang = localStorage.getItem('scout-lang') === 'de' ? 'de' : 'en'; } catch { /* private window */ }
  const t = () => T[state.lang];
  const locale = () => (state.lang === 'de' ? 'de-DE' : 'en-GB');
  const num = (n) => new Intl.NumberFormat(locale()).format(n ?? 0);

  function safeUrl(value) {
    try {
      const raw = String(value ?? '').trim();
      const u = new URL(/^[a-z][a-z0-9+.-]*:/i.test(raw) ? raw : 'https://' + raw);
      return u.protocol === 'http:' || u.protocol === 'https:' ? u : null;
    } catch { return null; }
  }
  function short(value) {
    const u = safeUrl(value);
    if (!u) return esc(value);
    const path = decodeURI(u.pathname).replace(/\/$/, '');
    return esc(u.hostname.replace(/^www\./, '') + (path.length > 44 ? path.slice(0, 42) + '…' : path));
  }
  function link(value, label, cls = '') {
    const u = safeUrl(value);
    const text = label ?? short(value);
    return u ? `<a${cls ? ` class="${cls}"` : ''} href="${esc(u.href)}" target="_blank" rel="noopener noreferrer">${text}</a>`
      : `<span>${text}</span>`;
  }
  const coord = (n) => Number(n).toFixed(5);
  const googleLink = (placeId, label) => 'https://www.google.com/maps/search/?api=1&query='
    + encodeURIComponent(label || 'Google') + '&query_place_id=' + encodeURIComponent(placeId);
  const isGoogle = (url) => { const u = safeUrl(url); return !!u && u.hostname.replace(/^www\./, '') === 'google.com'
    && u.pathname.startsWith('/maps') && u.searchParams.has('query_place_id'); };

  function shape(culture) {
    const s = SHAPE[culture];
    if (!s) return '';
    const body = {
      circle: '<circle class="shape" cx="5" cy="5" r="4"/>',
      square: '<rect class="shape" x="1.4" y="1.4" width="7.2" height="7.2"/>',
      diamond: '<path class="shape" d="M5 .4 9.6 5 5 9.6 .4 5z"/>',
      triangle: '<path class="shape" d="M5 1 9.6 9H.4z"/>',
      hexagon: '<path class="shape" d="M2.7 1h4.6L9.6 5 7.3 9H2.7L.4 5z"/>',
      ring: '<circle class="shape ring" cx="5" cy="5" r="3.3"/>',
    }[s];
    return `<svg width="10" height="10" viewBox="0 0 10 10" aria-hidden="true">${body}</svg>`;
  }

  // ---- the map: OpenStreetMap tiles, no library ----------------------------------

  function makeMap(root, onPick) {
    const view = { ...BERLIN };
    let pins = [], picked = -1, drag = null;
    root.innerHTML = '<div class="map-tiles"></div><div class="map-pins"></div>'
      + '<div class="map-zoom"><button type="button" data-zoom="1">+</button><button type="button" data-zoom="-1">−</button></div>'
      + '<p class="map-empty" hidden></p>';
    const tiles = root.querySelector('.map-tiles'), layer = root.querySelector('.map-pins');
    const empty = root.querySelector('.map-empty');
    const size = (z) => TILE * 2 ** z;
    const toPx = (lat, lon, z) => {
      const r = lat * Math.PI / 180;
      return [(lon + 180) / 360 * size(z), (1 - Math.log(Math.tan(r) + 1 / Math.cos(r)) / Math.PI) / 2 * size(z)];
    };
    const toLatLon = (x, y, z) => {
      const n = Math.PI - 2 * Math.PI * y / size(z);
      return { lat: 180 / Math.PI * Math.atan(Math.sinh(n)), lon: x / size(z) * 360 - 180 };
    };
    const zoomTo = (z) => { view.zoom = Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, z)); draw(); };
    const move = (dx, dy) => {
      const [x, y] = toPx(view.lat, view.lon, view.zoom);
      Object.assign(view, toLatLon(x + dx, y + dy, view.zoom));
    };

    // Positions go through element.style: the page's CSP rightly refuses inline style attributes.
    function draw() {
      const w = root.clientWidth, h = root.clientHeight;
      if (!w || !h) return;
      const z = view.zoom, n = 2 ** z, [cx, cy] = toPx(view.lat, view.lon, z);
      const left = cx - w / 2, top = cy - h / 2;
      const images = document.createDocumentFragment();
      for (let ty = Math.floor(top / TILE); ty <= Math.floor((top + h) / TILE); ty++) {
        if (ty < 0 || ty >= n) continue;
        for (let tx = Math.floor(left / TILE); tx <= Math.floor((left + w) / TILE); tx++) {
          const img = new Image();
          img.alt = '';
          img.draggable = false;
          img.referrerPolicy = 'strict-origin-when-cross-origin';   // the tile servers ask for a referrer
          img.style.left = `${Math.round(tx * TILE - left)}px`;
          img.style.top = `${Math.round(ty * TILE - top)}px`;
          img.src = `${TILES}/${z}/${((tx % n) + n) % n}/${ty}.png`;
          images.append(img);
        }
      }
      tiles.replaceChildren(images);
      const buttons = document.createDocumentFragment();
      pins.forEach((p, i) => {
        const [x, y] = toPx(p.lat, p.lon, z);
        const b = document.createElement('button');
        b.type = 'button';
        b.className = `pin${p.sure ? '' : ' unsure'}${i === picked ? ' on' : ''}`;
        b.dataset.pin = String(i);
        b.style.left = `${Math.round(x - left)}px`;
        b.style.top = `${Math.round(y - top)}px`;
        b.setAttribute('aria-label', p.label);
        b.setAttribute('aria-pressed', String(i === picked));
        const label = document.createElement('span');
        label.textContent = String(p.n);
        b.append(label);
        buttons.append(b);
      });
      layer.replaceChildren(buttons);
      tiles.style.transform = layer.style.transform = '';
    }

    function fit() {
      if (!pins.length) { Object.assign(view, BERLIN); return; }
      const lats = pins.map((p) => p.lat), lons = pins.map((p) => p.lon);
      const w = root.clientWidth || 600, h = root.clientHeight || 360;
      let z = 16;
      for (; z > MIN_ZOOM; z--) {
        const [x1, y1] = toPx(Math.max(...lats), Math.min(...lons), z);
        const [x2, y2] = toPx(Math.min(...lats), Math.max(...lons), z);
        if (x2 - x1 < w - 110 && y2 - y1 < h - 110) break;
      }
      Object.assign(view, { lat: (Math.min(...lats) + Math.max(...lats)) / 2,
        lon: (Math.min(...lons) + Math.max(...lons)) / 2, zoom: z });
    }

    root.addEventListener('pointerdown', (e) => {
      if (e.button !== 0 || e.target.closest('button')) return;
      drag = { x: e.clientX, y: e.clientY, dx: 0, dy: 0 };
      try { root.setPointerCapture(e.pointerId); } catch { /* the drag still works inside the map */ }
    });
    root.addEventListener('pointermove', (e) => {
      if (!drag) return;
      drag.dx = e.clientX - drag.x;
      drag.dy = e.clientY - drag.y;
      tiles.style.transform = layer.style.transform = `translate(${drag.dx}px,${drag.dy}px)`;
    });
    const release = () => {
      if (!drag) return;
      move(-drag.dx, -drag.dy);
      drag = null;
      draw();
    };
    root.addEventListener('pointerup', release);
    root.addEventListener('pointercancel', release);
    root.addEventListener('dblclick', (e) => {
      if (e.target.closest('button')) return;
      const r = root.getBoundingClientRect();
      move(e.clientX - r.left - r.width / 2, e.clientY - r.top - r.height / 2);
      zoomTo(view.zoom + 1);
    });
    root.addEventListener('keydown', (e) => {
      const step = { ArrowLeft: [-96, 0], ArrowRight: [96, 0], ArrowUp: [0, -96], ArrowDown: [0, 96] }[e.key];
      if (step) { e.preventDefault(); move(...step); draw(); }
      else if (e.key === '+' || e.key === '=') zoomTo(view.zoom + 1);
      else if (e.key === '-') zoomTo(view.zoom - 1);
    });
    root.querySelector('.map-zoom').addEventListener('click', (e) => {
      const b = e.target.closest('[data-zoom]');
      if (b) zoomTo(view.zoom + Number(b.dataset.zoom));
    });
    layer.addEventListener('click', (e) => {
      const b = e.target.closest('[data-pin]');
      if (b) onPick(pins[Number(b.dataset.pin)].card);
    });
    new ResizeObserver(() => draw()).observe(root);

    return {
      show(list, words) {
        pins = list;
        picked = -1;
        root.setAttribute('aria-label', words.label);
        const [zoomIn, zoomOut] = root.querySelectorAll('[data-zoom]');
        zoomIn.setAttribute('aria-label', words.zoomIn);
        zoomOut.setAttribute('aria-label', words.zoomOut);
        empty.hidden = pins.length > 0;
        empty.textContent = words.none;
        fit();
        draw();
      },
      pick(card, centre) {
        picked = pins.findIndex((p) => p.card === card);
        if (picked >= 0 && centre) {
          Object.assign(view, { lat: pins[picked].lat, lon: pins[picked].lon, zoom: Math.max(view.zoom, 15) });
        }
        draw();
      },
    };
  }
  let map = null;

  // ---- the parts that change -------------------------------------------------------

  function renderStatic() {
    const s = t();
    document.documentElement.lang = state.lang;
    document.querySelectorAll('[data-t]').forEach((el) => { el.textContent = s[el.dataset.t]; });
    $('brief').placeholder = s.briefPlaceholder;
    $('lang').textContent = s.other;
    $('lang').setAttribute('aria-label', s.langLabel);
    $('find').textContent = state.busy && state.run && !state.run.replay ? s.finding : s.find;
    $('credit').textContent = s.map.credit;
  }

  function renderKeys() {
    const s = t(), st = state.status;
    if (!st) { $('keys').textContent = ''; return; }
    const missing = [!st.nebius_key && 'NEBIUS_API_KEY', !st.tavily_key && 'TAVILY_API_KEY'].filter(Boolean);
    let html = missing.length
      ? fill(s.keysMissing, { names: missing.join(', ') }).replace(/scout\/\.env/, '<code>scout/.env</code>')
      : fill(s.keysOk, { model: st.model, sources: st.google ? s.searchThree : s.searchTwo });
    if (!missing.length && st.google_key && !st.google) html += ' ' + esc(s.googleOff).replace(/scout\/\.env/, '<code>scout/.env</code>');
    if (!st.bot_contact) html += ' ' + esc(s.contactMissing).replace(/scout\/\.env/, '<code>scout/.env</code>');
    $('keys').innerHTML = html;
    $('find').disabled = state.busy || missing.length > 0;
    $('replay').disabled = state.busy;
    $('runs').disabled = state.busy;
  }

  function renderRuns() {
    const s = t(), runs = (state.status?.runs ?? []).filter((r) => r.id.endsWith('-find')), keep = $('runs').value;
    $('runs').innerHTML = `<option value="sample">${esc(s.sampleOption)}</option>` + runs.map((r) => {
      const when = r.checked_at ? new Date(r.checked_at).toLocaleString(locale(),
        { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }) : r.id;
      return `<option value="${esc(r.id)}">${esc(when)} · ${esc((r.brief || '').slice(0, 48))}</option>`;
    }).join('');
    if ([...$('runs').options].some((o) => o.value === keep)) $('runs').value = keep;
  }

  function renderBanner() {
    const s = t(), run = state.run;
    const text = !run ? '' : run.sample ? s.sampleBanner
      : run.replay ? fill(s.replayBanner, { date: run.id.slice(0, 10) }) : '';
    $('banner').hidden = !text;
    $('banner').innerHTML = text;
  }

  function stepRow(e) {
    const s = t();
    const label = s.step[e.step] ?? e.step;
    let value = '';
    if (e.step === 'baseline') {
      value = `<q>${esc(e.query)}</q><small>${plural(s.results, e.results?.length, { n: e.results?.length ?? 0 })} · ${esc(s.forComparison)}</small>`;
    } else if (e.step === 'map') {
      const words = (e.words ?? []).length ? `<q>${esc(e.words.join(', '))}</q>` : esc(s.allFashion);
      const where = e.near ? fill(s.around, { place: e.near }) + ' · ' : '';
      value = `${words}<small>${where}${plural(s.places, e.found, { n: num(e.found) })}</small>`;
    } else if (e.step === 'map_failed') value = esc(s.mapFailed);
    else if (e.step === 'google') value = `<q>${esc(e.query)}</q><small>${plural(s.googlePlaces, e.found, { n: num(e.found) })}</small>`;
    else if (e.step === 'google_failed') value = esc(s.googleFailed);
    else if (e.step === 'search') value = `<q>${esc(e.query)}</q><small>${plural(s.results, e.results?.length, { n: e.results?.length ?? 0 })}</small>`;
    else if (e.step === 'read') value = `${short(e.url)}<small>${esc(e.via === 'tavily_extract' ? s.viaTavily : s.viaOwn)} · ${fill(s.chars, { n: num(e.chars) })}</small>`;
    else if (e.step === 'blocked') value = `${short(e.url)}<small>${esc(s.robots)}</small>`;
    else if (e.step === 'read_failed') value = short(e.url);
    else if (e.step === 'platform') value = `${short(e.website)}<small>${PLATFORM[e.platform] ? fill(s.feedYes, { p: PLATFORM[e.platform] }) : esc(s.feedNo)}</small>`;
    else if (e.step === 'submit_rejected') value = plural(s.sentBack, e.problems?.length, { n: e.problems?.length ?? 0 });
    else if (e.step === 'submit') value = plural(s.submitted, e.shops, { n: e.shops });
    else if (e.step === 'located') {
      const google = e.via_google || 0, address = e.shops - e.via_map - google;
      const via = [e.via_map && fill(s.locatedMap, { m: e.via_map }), address && fill(s.locatedAddress, { a: address }),
        google && fill(s.locatedGoogle, { g: google })].filter(Boolean).join(', ');
      value = `${fill(s.located, { k: e.shops, n: e.total })}${via ? `<small>${via}</small>` : ''}`;
    }
    return `<li><span class="k">${esc(label)}</span><span class="v">${value}</span></li>`;
  }

  function renderSteps() {
    const s = t();
    $('steps').innerHTML = state.steps.length ? state.steps.map(stepRow).join('')
      : `<li class="empty">${esc(s.stepsEmpty)}</li>`;
    if (state.busy) $('steps').scrollTop = $('steps').scrollHeight;
    const u = state.usage, count = (step) => num(state.steps.filter((e) => e.step === step).length);
    $('cost').innerHTML = u ? fill(s.cost, {
      searches: count('search'), maps: count('map'), reads: count('read'),
      credits: num(u.tavily_credits), tokens: num((u.prompt_tokens ?? 0) + (u.completion_tokens ?? 0)),
    }) : '';
  }

  function facts(shop) {
    const s = t(), hours = shop.location?.opening_hours;
    const channels = [shop.instagram && esc(shop.instagram), shop.business_email && esc(shop.business_email),
      shop.contact_page && link(shop.contact_page)].filter(Boolean).join('<br>');
    const rows = [
      [s.facts.website, shop.website ? link(shop.website) : ''],
      [s.facts.sells, esc(shop.sells)],
      // An address is shown only for a shop customers can visit: an online seller's may be a home.
      [s.facts.address, shop.storefront === 'yes' && shop.address_as_published ? esc(shop.address_as_published) : ''],
      [s.facts.hours, hours ? `${esc(hours)}<small>${esc(s.hoursNote)}</small>` : ''],
      [s.facts.status, `${esc(s.status[shop.status] ?? shop.status)}. ${esc(shop.status_evidence)}`],
      [s.facts.contact, esc(s.contact[shop.best_first_contact] ?? shop.best_first_contact)],
      [s.facts.channels, channels],
      [s.facts.languages, (shop.languages_seen ?? []).map(esc).join(', ')],
    ].filter(([, v]) => v);
    return `<dl class="facts">${rows.map(([k, v]) => `<div><dt>${esc(k)}</dt><dd>${v}</dd></div>`).join('')}</dl>`;
  }

  function sources(shop) {
    const s = t(), list = shop.sources ?? [], unseen = new Set(shop.unseen_sources ?? []);
    const flags = [];
    if (!list.length) flags.push(esc(s.noSources));
    else if (unseen.size) flags.push(fill(s.untraced, { u: unseen.size, n: list.length }));
    if (shop.crawl === false) flags.push(esc(s.crawlNo));
    const rows = list.map((src) => `<li>${isGoogle(src) ? link(googleLink(new URL(src).searchParams.get('query_place_id'), shop.name), 'Google Maps') : link(src)}<span class="mark${unseen.has(src) ? ' warn' : ''}">${
      esc(unseen.has(src) ? s.notTraced : s.traced)}</span></li>`);
    if (shop.location?.osm_url && !list.includes(shop.location.osm_url)) {
      rows.push(`<li>${link(shop.location.osm_url, esc(s.onMap))}<span class="mark">${esc(s.traced)}</span></li>`);
    }
    return `<div class="eyebrow">${esc(s.sourcesLabel)}</div><ul class="sources">${rows.join('')}</ul>`
      + (flags.length ? `<ul class="flags">${flags.map((f) => `<li>${f}</li>`).join('')}</ul>` : '');
  }

  function badges(shop) {
    const s = t(), v = shop.visibility, out = [];
    if (s.culture[shop.culture_guess]) {
      out.push(`<span class="tag c-${esc(shop.culture_guess)}">${shape(shop.culture_guess)}${esc(s.culture[shop.culture_guess])}</span>`);
    }
    if (v) {
      out.push(`<span class="tag seen${v.plain_search_rank ? '' : ' missed'}">${
        v.plain_search_rank ? fill(s.seen.rank, { n: v.plain_search_rank }) : esc(s.seen.missed)}</span>`);
      if (!v.has_website) out.push(`<span class="tag">${esc(s.seen.noSite)}</span>`);
    }
    return out.length ? `<div class="tags">${out.join('')}</div>` : '';
  }

  function card(shop, i) {
    const s = t(), loc = shop.location, sure = shop.verdict === 'accept';
    const meta = [shop.district, s.visit[shop.storefront]].filter(Boolean).map(esc).join(' · ');
    let actions = '';
    if (loc?.via === 'google' && loc.place_id) {
      // Google's rules for its content outside a Google map: credit "Google Maps" in the same box,
      // set the box apart from the rest, and link to Google Maps.
      actions = `<div class="gmaps">
        <p>${esc(s.googleOnly)}</p>
        <div class="actions">${link(googleLink(loc.place_id, shop.name), esc(s.actions.google), 'btn primary')}</div>
        <span class="gattr">Google Maps</span>
      </div>`;
    } else if (loc && loc.lat != null) {
      actions = `<div class="actions">
        <a class="btn primary" href="https://www.openstreetmap.org/directions?to=${coord(loc.lat)}%2C${coord(loc.lon)}" target="_blank" rel="noopener noreferrer">${esc(s.actions.directions)}</a>
        <button class="btn outline" type="button" data-show="${i}">${esc(s.actions.show)}</button>
      </div>`;
    }
    return `<article class="card${i === state.picked ? ' on' : ''}" id="shop-${i}">
      <div class="card-top">
        <h2 class="name"><span class="num${sure ? '' : ' unsure'}" aria-hidden="true">${i + 1}</span>${esc(shop.name)}</h2>
        <span class="tag verdict ${sure ? 'accept' : 'revisit'}">${esc(s.verdict[shop.verdict])}</span>
      </div>
      <div class="meta">${meta}</div>
      ${badges(shop)}
      <p class="reason">${esc(shop.verdict_reason)}</p>
      ${facts(shop)}
      <div class="src">${sources(shop)}</div>
      ${actions}
    </article>`;
  }

  function leftOut(shop) {
    return `<article class="card small">
      <h3 class="name">${esc(shop.name)}</h3>
      <p class="reason">${esc(shop.verdict_reason)}</p>
      <div class="src">${sources(shop)}</div>
    </article>`;
  }

  function found() {
    const rank = (shop) => (shop.verdict === 'accept' ? 0 : 1);
    return (state.shops ?? []).filter((shop) => shop.verdict !== 'reject').sort((a, b) => rank(a) - rank(b));
  }

  function renderQueue() {
    const s = t();
    $('map').hidden = $('credit-row').hidden = !state.shops;
    $('hidden').innerHTML = '';
    if (state.problem) {
      $('count').textContent = '';
      $('cards').innerHTML = `<div class="problem" role="alert">${fill(s.failed, { why: state.problem })}</div>`;
      return;
    }
    if (!state.shops) {
      $('count').textContent = '';
      $('cards').innerHTML = state.busy ? '' : `<div class="empty-state"><div class="h">${esc(s.emptyH)}</div><div class="b">${esc(s.emptyB)}</div></div>`;
      return;
    }
    const shops = found(), rest = state.shops.filter((shop) => shop.verdict === 'reject');
    const sure = shops.filter((shop) => shop.verdict === 'accept').length;
    $('count').innerHTML = shops.length
      ? plural(s.count, shops.length, { n: shops.length, a: sure, p: shops.length - sure }) : esc(s.noneFound);
    const compared = shops.filter((shop) => shop.visibility);
    const missed = compared.filter((shop) => !shop.visibility.plain_search_rank).length;
    if (compared.length) $('hidden').innerHTML = plural(s.hidden, missed, { h: missed, n: compared.length });
    $('cards').innerHTML = shops.map(card).join('') + (rest.length
      ? `<details class="left-out"><summary>${plural(s.leftOut, rest.length, { n: rest.length })}</summary>${rest.map(leftOut).join('')}</details>`
      : '');
    map = map || makeMap($('map'), (i) => pick(i, false));
    map.show(shops.map((shop, i) => shop.location && shop.location.lat != null && {
      card: i, n: i + 1, lat: shop.location.lat, lon: shop.location.lon, sure: shop.verdict === 'accept',
      label: `${i + 1}. ${shop.name}`,
    }).filter(Boolean), s.map);
    if (state.picked >= 0) map.pick(state.picked, false);
  }

  function pick(i, centre) {
    state.picked = i;
    document.querySelectorAll('#cards > .card').forEach((el, j) => el.classList.toggle('on', j === i));
    map?.pick(i, centre);
    if (!centre) $(`shop-${i}`)?.scrollIntoView({ block: 'nearest' });
  }

  function render() { renderStatic(); renderKeys(); renderRuns(); renderBanner(); renderSteps(); renderQueue(); }

  // ---- talking to the server -------------------------------------------------------

  async function stream(url, options, onEvent) {
    const res = await fetch(url, options);
    if (!res.ok) throw new Error((await res.json().catch(() => ({}))).error || res.statusText);
    const reader = res.body.getReader(), decoder = new TextDecoder();
    let buffer = '';
    for (;;) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      let cut;
      while ((cut = buffer.indexOf('\n\n')) !== -1) {
        const block = buffer.slice(0, cut);
        buffer = buffer.slice(cut + 2);
        let kind = 'message', data = '';
        for (const line of block.split('\n')) {
          if (line.startsWith('event: ')) kind = line.slice(7);
          else if (line.startsWith('data: ')) data += line.slice(6);
        }
        if (data) onEvent(kind, JSON.parse(data));
      }
    }
  }

  async function loadStatus() {
    try { state.status = await (await fetch('/api/status')).json(); } catch { state.status = null; }
  }

  async function go(url, options) {
    if (state.busy) return;
    Object.assign(state, { busy: true, run: null, steps: [], shops: null, usage: null, problem: null, picked: -1 });
    render();
    try {
      await stream(url, options, (kind, data) => {
        if (kind === 'start') { state.run = data; renderBanner(); renderStatic(); }
        else if (kind === 'step') { state.steps.push(data); renderSteps(); }
        else if (kind === 'failed') { state.problem = data.message; state.usage = data.usage; }
        else if (kind === 'done') {
          state.shops = data.shops ?? [];
          state.usage = data.usage ?? null;
        }
      });
    } catch (e) {
      state.problem = e.message;
    }
    state.busy = false;
    await loadStatus();
    render();
  }

  // ---- what the person does --------------------------------------------------------

  $('lang').addEventListener('click', () => {
    state.lang = state.lang === 'en' ? 'de' : 'en';
    try { localStorage.setItem('scout-lang', state.lang); } catch { /* private window */ }
    render();
  });
  $('find').addEventListener('click', () => {
    const brief = $('brief').value.trim() || $('brief').placeholder;
    go('/api/find', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ brief }) });
  });
  $('replay').addEventListener('click', () => go('/api/replay?run=' + encodeURIComponent($('runs').value)));
  $('cards').addEventListener('click', (event) => {
    const button = event.target.closest('[data-show]');
    if (!button) return;
    pick(Number(button.dataset.show), true);
    $('map').scrollIntoView({ block: 'nearest' });
  });

  loadStatus().then(() => {
    render();
    if (location.hash === '#sample') go('/api/replay?run=sample');
  });
  render();
})();
