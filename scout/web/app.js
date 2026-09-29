/* Scout review screen.
   Everything a run returns was written by a model that read the open web, so it is
   treated as untrusted: every value is escaped, and only http(s) links become links. */
(() => {
  'use strict';

  const T = {
    en: {
      title: 'Find the shops the platforms miss.',
      sub: 'Scout searches, reads each shop’s Impressum and brings back records with a source for every fact. A person decides. Nothing is published and nobody is contacted.',
      briefLabel: 'Brief', briefPlaceholder: 'Central Asian occasion wear in Berlin',
      find: 'Find shops', finding: 'Scout is working', recorded: 'Recorded runs', replay: 'Replay',
      sampleOption: 'Sample run (invented shops)',
      logLabel: 'What Scout is doing', queueLabel: 'Review queue',
      foot: 'Scout runs on NVIDIA Nemotron through Nebius Token Factory and searches with Tavily. It checks robots.txt before it reads a page and records business contact details only.',
      keysOk: 'Model: {model}. Search: Tavily.',
      keysMissing: 'Keys are missing: {names}. Put them in scout/.env and start Scout again. The sample run works without them.',
      contactMissing: 'Set CMX_BOT_CONTACT in scout/.env so shops can see who is reading their site.',
      stepsEmpty: 'No steps yet.', emptyH: 'No run yet.',
      emptyB: 'Write a brief, or replay the sample run to see how Scout works.',
      sampleBanner: 'Sample run · invented shops, for trying the screen',
      replayBanner: 'Replay of a recorded run · {date}',
      count: ['{n} shop. Accept {a}, reject {r}, for a person {p}.', '{n} shops. Accept {a}, reject {r}, for a person {p}.'],
      cost: '{searches} searches and {reads} pages read. {credits} Tavily credits, {tokens} tokens through Nemotron.',
      verdict: { accept: 'Accept', reject: 'Reject', revisit: 'For a person' },
      step: { search: 'Search', read: 'Read', blocked: 'Stayed out', read_failed: 'No answer', platform: 'Feed', submit_rejected: 'Sent back', submit: 'Done' },
      results: ['{n} result', '{n} results'], viaTavily: 'rendered through Tavily', viaOwn: 'read by our own fetcher',
      robots: 'robots.txt asks crawlers to stay out', feedYes: '{p} product feed', feedNo: 'no product feed',
      sentBack: ['{n} value outside the vocabulary', '{n} values outside the vocabulary'], submitted: ['{n} shop submitted', '{n} shops submitted'], chars: '{n} characters',
      facts: { website: 'Website', sells: 'Sells', address: 'Address', status: 'Status', contact: 'First contact', channels: 'Channels', languages: 'Languages' },
      status: { trading: 'Trading', closed: 'Closed', moved: 'Moved', unclear: 'Unclear' },
      berlin: { yes: 'In Berlin', no: 'Not in Berlin', unconfirmed: 'Berlin not confirmed' },
      contact: { in_person: 'In person', email: 'Email', instagram: 'Instagram', phone: 'Phone', contact_form: 'Contact form', unknown: 'Unknown' },
      feed: { shopify: 'Shopify feed', woocommerce: 'WooCommerce feed', html: 'No feed', none: 'No website shop', unknown: 'Feed not checked' },
      sourcesLabel: 'Sources', traced: 'Traced', notTraced: '[Not traced]', noSources: '[No source given]',
      untraced: '[{u} of {n} sources not traced]',
      crawlNo: '[robots.txt: do not crawl. Ask the shop directly.]',
      decide: { approve_outreach: 'Approve for outreach', visit: 'Visit in person', reject: 'Reject' },
      decided: 'Decided: {what}', change: 'Change',
      draftBtn: 'Draft the listing', drafting: 'Reading the shop’s feed',
      draftLabel: 'Draft listing · not published',
      draftSummary: '{read} products read from the shop’s own {platform} feed, {stock} in stock, {from} to {to}.',
      draftTagged: '{rules} tagged by rules, {model} by Nemotron. {low} left for a person.',
      draftCrafts: 'Craft terms found: {list}.', draftProposals: 'Proposed new tags: {list}.',
      draftPhotos: 'Photos and descriptions belong to the shop. They appear only after the shop agrees.',
      open: 'Open on the shop’s site', by: { rules: 'rules', nemotron: 'Nemotron', claude: 'Claude' },
      culture: { african: 'African', central_asian: 'Central Asian', south_asian: 'South Asian', middle_eastern: 'Middle Eastern', east_asian: 'East Asian', balkan: 'Balkan', latin_american: 'Latin American', modest: 'Modest', fusion: 'Fusion', not_culturally_specific: 'Not culturally specific', unknown: 'Culture unknown' },
      failed: 'Scout stopped. {why}', langLabel: 'Sprache wechseln', other: 'DE',
    },
    de: {
      title: 'Die Läden finden, die Plattformen übersehen.',
      sub: 'Scout sucht, liest das Impressum jedes Ladens und liefert Einträge mit einer Quelle für jede Angabe. Ein Mensch entscheidet. Nichts wird veröffentlicht, niemand wird kontaktiert.',
      briefLabel: 'Auftrag', briefPlaceholder: 'Zentralasiatische Festmode in Berlin',
      find: 'Läden finden', finding: 'Scout arbeitet', recorded: 'Aufgezeichnete Läufe', replay: 'Abspielen',
      sampleOption: 'Beispiellauf (erfundene Läden)',
      logLabel: 'Was Scout gerade tut', queueLabel: 'Zur Prüfung',
      foot: 'Scout läuft mit NVIDIA Nemotron über Nebius Token Factory und sucht mit Tavily. Vor dem Lesen einer Seite prüft Scout die robots.txt und erfasst nur geschäftliche Kontaktdaten.',
      keysOk: 'Modell: {model}. Suche: Tavily.',
      keysMissing: 'Es fehlen Schlüssel: {names}. Trage sie in scout/.env ein und starte Scout neu. Der Beispiellauf funktioniert ohne sie.',
      contactMissing: 'Trage CMX_BOT_CONTACT in scout/.env ein, damit Läden sehen, wer ihre Seite liest.',
      stepsEmpty: 'Noch keine Schritte.', emptyH: 'Noch kein Lauf.',
      emptyB: 'Schreibe einen Auftrag oder spiele den Beispiellauf ab, um zu sehen, wie Scout arbeitet.',
      sampleBanner: 'Beispiellauf · erfundene Läden, zum Ausprobieren',
      replayBanner: 'Aufgezeichneter Lauf · {date}',
      count: ['{n} Laden. Aufnehmen {a}, ablehnen {r}, für einen Menschen {p}.', '{n} Läden. Aufnehmen {a}, ablehnen {r}, für einen Menschen {p}.'],
      cost: '{searches} Suchen und {reads} gelesene Seiten. {credits} Tavily-Credits, {tokens} Tokens über Nemotron.',
      verdict: { accept: 'Aufnehmen', reject: 'Ablehnen', revisit: 'Mensch entscheidet' },
      step: { search: 'Suche', read: 'Gelesen', blocked: 'Draußen', read_failed: 'Keine Antwort', platform: 'Feed', submit_rejected: 'Zurück', submit: 'Fertig' },
      results: ['{n} Treffer', '{n} Treffer'], viaTavily: 'über Tavily gerendert', viaOwn: 'mit unserem eigenen Abruf gelesen',
      robots: 'robots.txt bittet Crawler, draußen zu bleiben', feedYes: 'Produkt-Feed von {p}', feedNo: 'kein Produkt-Feed',
      sentBack: ['{n} Wert außerhalb des Vokabulars', '{n} Werte außerhalb des Vokabulars'], submitted: ['{n} Laden übergeben', '{n} Läden übergeben'], chars: '{n} Zeichen',
      facts: { website: 'Website', sells: 'Sortiment', address: 'Adresse', status: 'Status', contact: 'Erster Kontakt', channels: 'Kanäle', languages: 'Sprachen' },
      status: { trading: 'In Betrieb', closed: 'Geschlossen', moved: 'Umgezogen', unclear: 'Unklar' },
      berlin: { yes: 'In Berlin', no: 'Nicht in Berlin', unconfirmed: 'Berlin nicht bestätigt' },
      contact: { in_person: 'Persönlich', email: 'E-Mail', instagram: 'Instagram', phone: 'Telefon', contact_form: 'Kontaktformular', unknown: 'Unbekannt' },
      feed: { shopify: 'Shopify-Feed', woocommerce: 'WooCommerce-Feed', html: 'Kein Feed', none: 'Kein Onlineshop', unknown: 'Feed nicht geprüft' },
      sourcesLabel: 'Quellen', traced: 'Nachvollzogen', notTraced: '[Nicht nachvollzogen]', noSources: '[Keine Quelle angegeben]',
      untraced: '[{u} von {n} Quellen nicht nachvollzogen]',
      crawlNo: '[robots.txt: nicht crawlen. Den Laden direkt fragen.]',
      decide: { approve_outreach: 'Für Kontakt freigeben', visit: 'Persönlich besuchen', reject: 'Ablehnen' },
      decided: 'Entschieden: {what}', change: 'Ändern',
      draftBtn: 'Eintrag entwerfen', drafting: 'Feed des Ladens wird gelesen',
      draftLabel: 'Entwurf · nicht veröffentlicht',
      draftSummary: '{read} Produkte aus dem eigenen {platform}-Feed des Ladens gelesen, {stock} vorrätig, {from} bis {to}.',
      draftTagged: '{rules} durch Regeln getaggt, {model} durch Nemotron. {low} bleiben für einen Menschen.',
      draftCrafts: 'Gefundene Handwerksbegriffe: {list}.', draftProposals: 'Vorgeschlagene neue Tags: {list}.',
      draftPhotos: 'Fotos und Beschreibungen gehören dem Laden. Sie erscheinen erst, wenn der Laden zustimmt.',
      open: 'Auf der Seite des Ladens öffnen', by: { rules: 'Regeln', nemotron: 'Nemotron', claude: 'Claude' },
      culture: { african: 'Afrikanisch', central_asian: 'Zentralasiatisch', south_asian: 'Südasiatisch', middle_eastern: 'Nahöstlich', east_asian: 'Ostasiatisch', balkan: 'Balkan', latin_american: 'Lateinamerikanisch', modest: 'Modest', fusion: 'Fusion', not_culturally_specific: 'Nicht kulturspezifisch', unknown: 'Kultur unbekannt' },
      failed: 'Scout hat angehalten. {why}', langLabel: 'Switch language', other: 'EN',
    },
  };
  const SHAPE = { african: 'circle', central_asian: 'square', south_asian: 'circle', middle_eastern: 'hexagon',
    east_asian: 'diamond', balkan: 'diamond', latin_american: 'triangle', modest: 'triangle', fusion: 'ring' };
  const PLATFORM = { shopify: 'Shopify', woocommerce: 'WooCommerce' };

  const $ = (id) => document.getElementById(id);
  const esc = (v) => String(v ?? '').replace(/[&<>"']/g,
    (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const fill = (text, vars = {}) => text.replace(/\{(\w+)\}/g, (_, k) => esc(vars[k] ?? ''));
  const many = (forms, vars) => fill(forms[Number(vars.n) === 1 ? 0 : 1], vars);

  const state = { lang: 'en', status: null, run: null, steps: [], shops: null, usage: null, decisions: {},
    drafts: {}, busy: false, problem: null };
  try { state.lang = localStorage.getItem('scout-lang') === 'de' ? 'de' : 'en'; } catch { /* private window */ }
  const t = () => T[state.lang];
  const locale = () => (state.lang === 'de' ? 'de-DE' : 'en-GB');
  const num = (n) => new Intl.NumberFormat(locale()).format(n ?? 0);
  const money = (n, currency = 'EUR') => (n == null ? '' : new Intl.NumberFormat(locale(),
    { style: 'currency', currency, maximumFractionDigits: 0 }).format(n));
  const word = (v) => esc(String(v ?? '').replace(/_/g, ' '));

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
  const dot = (verdict) => `<svg width="10" height="10" viewBox="0 0 10 10" aria-hidden="true"><circle class="dot${
    { accept: '', reject: ' ring', revisit: ' half' }[verdict] ?? ' ring'}" cx="5" cy="5" r="3.4"/></svg>`;

  // ---- the parts that change -------------------------------------------------------

  function renderStatic() {
    const s = t();
    document.documentElement.lang = state.lang;
    document.querySelectorAll('[data-t]').forEach((el) => { el.textContent = s[el.dataset.t]; });
    $('brief').placeholder = s.briefPlaceholder;
    $('lang').textContent = s.other;
    $('lang').setAttribute('aria-label', s.langLabel);
    $('find').textContent = state.busy && state.run && !state.run.replay ? s.finding : s.find;
  }

  function renderKeys() {
    const s = t(), st = state.status;
    if (!st) { $('keys').textContent = ''; return; }
    const missing = [!st.nebius_key && 'NEBIUS_API_KEY', !st.tavily_key && 'TAVILY_API_KEY'].filter(Boolean);
    let html = missing.length
      ? fill(s.keysMissing, { names: missing.join(', ') }).replace(/scout\/\.env/, '<code>scout/.env</code>')
      : fill(s.keysOk, { model: st.model });
    if (!st.bot_contact) html += ' ' + esc(s.contactMissing).replace(/scout\/\.env/, '<code>scout/.env</code>');
    $('keys').innerHTML = html;
    $('find').disabled = state.busy || missing.length > 0;
    $('replay').disabled = state.busy;
    $('runs').disabled = state.busy;
  }

  function renderRuns() {
    const s = t(), runs = state.status?.runs ?? [], keep = $('runs').value;
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
    if (e.step === 'search') value = `<q>${esc(e.query)}</q><small>${many(s.results, { n: e.results?.length ?? 0 })}</small>`;
    else if (e.step === 'read') value = `${short(e.url)}<small>${esc(e.via === 'tavily_extract' ? s.viaTavily : s.viaOwn)} · ${fill(s.chars, { n: num(e.chars) })}</small>`;
    else if (e.step === 'blocked') value = `${short(e.url)}<small>${esc(s.robots)}</small>`;
    else if (e.step === 'read_failed') value = short(e.url);
    else if (e.step === 'platform') value = `${short(e.website)}<small>${PLATFORM[e.platform] ? fill(s.feedYes, { p: PLATFORM[e.platform] }) : esc(s.feedNo)}</small>`;
    else if (e.step === 'submit_rejected') value = many(s.sentBack, { n: e.problems?.length ?? 0 });
    else if (e.step === 'submit') value = many(s.submitted, { n: e.shops });
    return `<li><span class="k">${esc(label)}</span><span class="v">${value}</span></li>`;
  }

  function renderSteps() {
    const s = t();
    $('steps').innerHTML = state.steps.length ? state.steps.map(stepRow).join('')
      : `<li class="empty">${esc(s.stepsEmpty)}</li>`;
    if (state.busy) $('steps').scrollTop = $('steps').scrollHeight;
    const u = state.usage;
    $('cost').innerHTML = u ? fill(s.cost, {
      searches: num(state.steps.filter((e) => e.step === 'search').length),
      reads: num(state.steps.filter((e) => e.step === 'read').length),
      credits: num(u.tavily_credits), tokens: num((u.prompt_tokens ?? 0) + (u.completion_tokens ?? 0)),
    }) : '';
  }

  function facts(shop) {
    const s = t();
    const channels = [shop.instagram && esc(shop.instagram), shop.business_email && esc(shop.business_email),
      shop.contact_page && link(shop.contact_page)].filter(Boolean).join('<br>');
    const rows = [
      [s.facts.website, shop.website ? link(shop.website) : ''],
      [s.facts.sells, esc(shop.sells)],
      [s.facts.address, shop.address_as_published ? esc(shop.address_as_published) : ''],
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
    return `<div class="eyebrow">${esc(s.sourcesLabel)}</div>`
      + `<ul class="sources">${list.map((src) => `<li>${link(src)}<span class="mark${unseen.has(src) ? ' warn' : ''}">${
        esc(unseen.has(src) ? s.notTraced : s.traced)}</span></li>`).join('')}</ul>`
      + (flags.length ? `<ul class="flags">${flags.map((f) => `<li>${f}</li>`).join('')}</ul>` : '');
  }

  function draft(shop, i) {
    const s = t(), d = state.drafts[shop.name];
    const canDraft = PLATFORM[shop.platform] && shop.crawl !== false && shop.verdict !== 'reject';
    if (!d) return canDraft ? `<div class="actions"><button class="btn outline" type="button" data-act="draft" data-i="${i}">${esc(s.draftBtn)}</button></div>` : '';
    if (d === 'loading') return `<div class="draft"><div class="eyebrow">${esc(s.drafting)}</div></div>`;
    if (d.error) return `<div class="draft"><div class="eyebrow">${esc(s.draftLabel)}</div><p>${esc(d.error)}</p></div>`;
    const by = d.tagged_by ?? {};
    const terms = (d.craft_terms ?? []).map(([term, n]) => `${word(term)} (${num(n)})`).join(', ');
    const wanted = (d.proposals ?? []).map((p) => `${word(p.term)} (${num(p.products)})`).join(', ');
    return `<div class="draft">
      <div class="eyebrow">${esc(s.draftLabel)}</div>
      <h3>${esc(d.shop)}</h3>
      <p>${fill(s.draftSummary, { read: num(d.read), platform: PLATFORM[d.platform] ?? d.platform, stock: num(d.in_stock), from: money(d.price_from), to: money(d.price_to) })}
         ${fill(s.draftTagged, { rules: num(by.rules), model: num(by.nemotron), low: num(d.tagged?.low) })}</p>
      ${terms ? `<p>${s.draftCrafts.replace('{list}', terms)}</p>` : ''}
      ${wanted ? `<p>${s.draftProposals.replace('{list}', wanted)}</p>` : ''}
      <ul class="items">${(d.sample ?? []).map((p) => `<li>
        <span class="t">${esc(p.title)}${p.title_original && p.title_original !== p.title ? `<span class="o" lang="">${esc(p.title_original)}</span>` : ''}</span>
        <span class="p">${esc(money(p.price, p.currency))}</span>
        <span class="m">${[word(p.category), ...(p.occasions ?? []).map(word), ...(p.craft_terms ?? []).map(word)].join(' · ')} · ${esc(s.by[p.tagged_by] ?? p.tagged_by)}</span>
        ${link(p.url, esc(s.open), 'link')}
      </li>`).join('')}</ul>
      <p>${esc(s.draftPhotos)}</p>
    </div>`;
  }

  function decision(shop, i) {
    const s = t(), d = state.decisions[shop.name];
    if (d) {
      return `<div class="decided"><p>${fill(s.decided, { what: '\u0000' }).replace('\u0000',
        `<strong>${esc(s.decide[d.decision] ?? d.decision)}</strong>`)}</p>
        <button class="link" type="button" data-act="change" data-i="${i}">${esc(s.change)}</button></div>`;
    }
    const primary = { accept: 'approve_outreach', revisit: 'visit', reject: 'reject' }[shop.verdict];
    return `<div class="actions">${['approve_outreach', 'visit', 'reject'].map((k) =>
      `<button class="btn ${k === primary ? 'primary' : 'outline'}" type="button" data-act="decide" data-what="${k}" data-i="${i}">${esc(s.decide[k])}</button>`).join('')}</div>`;
  }

  function card(shop, i) {
    const s = t();
    const meta = [shop.district, s.berlin[shop.in_berlin], s.feed[shop.platform]].filter(Boolean).map(esc).join(' · ');
    const culture = s.culture[shop.culture_guess] ?? shop.culture_guess;
    return `<article class="card">
      <div class="card-top">
        <div><h2 class="name">${esc(shop.name)}</h2><div class="meta">${meta}</div></div>
        <span class="tag verdict ${esc(shop.verdict)}">${dot(shop.verdict)}${esc(s.verdict[shop.verdict] ?? shop.verdict)}</span>
      </div>
      <div class="tags"><span class="tag c-${esc(shop.culture_guess)}">${shape(shop.culture_guess)}${esc(culture)}</span></div>
      <p class="reason">${esc(shop.verdict_reason)}</p>
      ${facts(shop)}
      <div class="src">${sources(shop)}</div>
      ${decision(shop, i)}
      ${draft(shop, i)}
    </article>`;
  }

  function renderQueue() {
    const s = t();
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
    const n = (v) => state.shops.filter((x) => x.verdict === v).length;
    $('count').innerHTML = many(s.count, { n: state.shops.length, a: n('accept'), r: n('reject'), p: n('revisit') });
    $('cards').innerHTML = state.shops.map(card).join('');
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

  async function post(url, body) {
    const res = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || res.statusText);
    return data;
  }

  async function loadStatus() {
    try { state.status = await (await fetch('/api/status')).json(); } catch { state.status = null; }
  }

  async function go(url, options) {
    if (state.busy) return;
    Object.assign(state, { busy: true, run: null, steps: [], shops: null, usage: null, decisions: {}, drafts: {}, problem: null });
    render();
    try {
      await stream(url, options, (kind, data) => {
        if (kind === 'start') { state.run = data; renderBanner(); renderStatic(); }
        else if (kind === 'step') { state.steps.push(data); renderSteps(); }
        else if (kind === 'failed') { state.problem = data.message; state.usage = data.usage; }
        else if (kind === 'done') {
          state.shops = data.shops ?? [];
          state.usage = data.usage ?? null;
          state.decisions = data.decisions ?? {};
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

  $('cards').addEventListener('click', async (event) => {
    const button = event.target.closest('[data-act]');
    if (!button || !state.shops || !state.run) return;
    const shop = state.shops[Number(button.dataset.i)];
    if (!shop) return;
    if (button.dataset.act === 'change') {
      delete state.decisions[shop.name];
    } else if (button.dataset.act === 'decide') {
      try {
        state.decisions[shop.name] = await post('/api/decision',
          { run: state.run.id, shop: shop.name, decision: button.dataset.what });
      } catch (e) { state.problem = e.message; }
    } else if (button.dataset.act === 'draft') {
      state.drafts[shop.name] = 'loading';
      renderQueue();
      try { state.drafts[shop.name] = await post('/api/listing', { run: state.run.id, shop: shop.name }); }
      catch (e) { state.drafts[shop.name] = { error: e.message }; }
    }
    renderQueue();
  });

  loadStatus().then(() => {
    render();
    if (location.hash === '#sample') go('/api/replay?run=sample');
  });
  render();
})();
