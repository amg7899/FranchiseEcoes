// Profit calculator (2026-11-27, after an outside review of the site asked for "individual financial modelling").
// The model is the product pages' own (section V. of ECOES MultiCharger Mobile, "Брутна печалба" of the Box):
// 120 kW for 24 hours at the chosen load; a kWh costs 0,3 L × the diesel price from the generator, or the grid
// price in stationary mode; it sells at the selling price (1,20 / 0,90 EUR/kWh); the MultiCharger Mobile in mobile
// mode adds the forecast customer-service income (200 EUR a day at 100% load, in proportion: 20 EUR at 10%);
// a month is 30 days and a year 12 months, as in the tables. On top come the visitor's own other costs and the
// financing: own funds, the 50% instalments over 12–24 months of the Financing page, or a lease on the lessor's
// terms. Out come the gross profit, the payment, what is left each month, the payback, the payment cover, the
// cumulative cash flow (drawn to the real pixel width, so its labels stay 14px) and one month as a statement.
// The scenario goes to the contact form as a ready message (?topic=finance&calc=…).
(function () {
  var root = document.querySelector('[data-calc]');
  if (!root) return;
  var form = root.querySelector('form');
  var BG = root.getAttribute('data-lang') === 'bg';
  var TH = BG ? '.' : ',', DEC = BG ? ',' : '.';
  var KW = 120, HOURS = 24, DAYS = 30, MONTHS = 12;
  var PRICE = { box: 100000, mobile: null };          // the Box as on the Investors page; the Mobile by offer
  var SALE = { generator: 1.2, grid: 0.9 };
  var T = BG ? {
    month1: 'месец', months: 'месеца', mo: 'мес.', none: 'няма', enterPrice: 'въведете цена',
    enterTerms: 'въведете условията', never: 'не се изплаща при тези условия', firstMonth: 'от първия месец',
    cover: function (v) { return 'покритие ' + v + ' пъти'; }, hours: function (h, kwh) { return 'Около ' + h + ' ' + (h === '1' ? 'час' : 'часа') + ' зареждане на ден при 120 kW (' + kwh + ' kWh).'; },
    paid: 'изплатено след около ', kwhCharged: 'Заредена енергия', revenue: 'Приходи от зареждане', diesel: 'Дизел',
    gridPower: 'Ток от мрежата', service: 'Обслужване на клиенти', forecast: 'прогноза', gross: 'Брутна печалба',
    costs: 'Други разходи', payment: 'Вноска', left: 'Остава', chartLabel: function (p) { return p; },
    chartFig: function (h) { return 'Натрупан паричен поток за първите ' + h + ' месеца: вложеното в началото, после остатъкът всеки месец.'; },
    chartAria: function (s) { return 'Натрупан паричен поток. ' + s; },
    protect: function (v) { return 'Защита на инвестицията: обратно изкупуване за ' + v + ' EUR – 50% от покупната цена, между 1-вата и 3-тата година от покупката, след като цената е изплатена изцяло.'; },
    summaryHead: 'Разчет от калкулатора на печалбата:', product: 'Продукт', mode: 'Режим', load: 'Натовареност',
    modeGen: 'мобилен (ток от генератора)', modeGrid: 'стационарен (ток от мрежата)', energy: 'Енергия',
    energyGrid: 'ток от мрежата ', energyDiesel: 'дизел ', saleLine: 'Продажна цена на DC тока',
    serviceLine: function (v) { return 'Обслужване на клиенти: ' + v + ' EUR/ден при 100% натовареност (прогноза)'; },
    stationPrice: 'Цена на станцията', byOffer: 'по оферта', financing: 'Финансиране', own: 'собствени средства',
    split: function (n, r) { return 'разсрочено плащане на 50% за ' + n + ' месеца' + (r ? ', лихва ' + r + '% годишно' : ''); },
    lease: function (d, r, t) { return 'лизинг, самоучастие ' + d + '%, лихва ' + r + '% годишно, ' + t + ' месеца'; },
    perMonth: ' на месец', grossLine: 'Брутна печалба', paymentLine: 'Месечна вноска', leftLine: 'Остава на месец',
    paybackLine: 'Изплащане', ask: 'Моля, изгответе финансов анализ за моя случай.', where: 'Държава и място на работа: ',
    perDay: ' EUR на ден', perMonthPeek: 'брутна печалба на месец', paybackPeek: 'изплащане '
  } : {
    month1: 'month', months: 'months', mo: 'mo', none: 'none', enterPrice: 'enter a price',
    enterTerms: 'enter the terms', never: 'does not pay back on these terms', firstMonth: 'from the first month',
    cover: function (v) { return 'covered ' + v + ' times'; }, hours: function (h, kwh) { return 'About ' + h + ' ' + (h === '1' ? 'hour' : 'hours') + ' of charging a day at 120 kW (' + kwh + ' kWh).'; },
    paid: 'paid back after about ', kwhCharged: 'Energy charged', revenue: 'Charging revenue', diesel: 'Diesel',
    gridPower: 'Grid power', service: 'Customer service', forecast: 'forecast', gross: 'Gross profit',
    costs: 'Other costs', payment: 'Payment', left: 'Left', chartLabel: function (p) { return p; },
    chartFig: function (h) { return 'Cumulative cash flow over the first ' + h + ' months: the money put in at the start, then what is left each month.'; },
    chartAria: function (s) { return 'Cumulative cash flow. ' + s; },
    protect: function (v) { return 'Investment protection: buy-back for ' + v + ' EUR – 50% of the purchase price, between the 1st and the 3rd year after purchase, once the price has been paid in full.'; },
    summaryHead: 'Calculation from the profit calculator:', product: 'Product', mode: 'Mode', load: 'Load',
    modeGen: 'mobile (power from the generator)', modeGrid: 'stationary (power from the grid)', energy: 'Energy',
    energyGrid: 'grid power ', energyDiesel: 'diesel ', saleLine: 'Selling price of DC power',
    serviceLine: function (v) { return 'Customer service: ' + v + ' EUR a day at 100% load (forecast)'; },
    stationPrice: 'Price of the station', byOffer: 'by offer', financing: 'Financing', own: 'own funds',
    split: function (n, r) { return 'instalments on 50% over ' + n + ' months' + (r ? ', interest ' + r + '% a year' : ''); },
    lease: function (d, r, t) { return 'lease, ' + d + '% down, interest ' + r + '% a year, ' + t + ' months'; },
    perMonth: ' a month', grossLine: 'Gross profit', paymentLine: 'Monthly payment', leftLine: 'Left each month',
    paybackLine: 'Payback', ask: 'Please prepare a financial analysis for my case.', where: 'Country and place of operation: ',
    perDay: ' EUR a day', perMonthPeek: 'gross profit a month', paybackPeek: 'payback '
  };

  // numbers: 28.920 / 2,00 in Bulgarian, 28,920 / 2.00 in English
  function fmt(n, d) {
    d = d || 0;
    var neg = n < 0 && Math.abs(n) >= 0.5 * Math.pow(10, -d);
    var s = Math.abs(n).toFixed(d).split('.');
    return (neg ? '−' : '') + s[0].replace(/\B(?=(\d{3})+(?!\d))/g, TH) + (d ? DEC + s[1] : '');
  }
  function eur(n) { return fmt(Math.round(n)) + ' EUR'; }
  function trim1(n) { return fmt(n, Math.round(n * 10) % 10 ? 1 : 0); }
  // what the visitor typed: money fields take 100.000 or 100 000 (and a decimal part of one or two digits),
  // the others 2,00 or 2.00
  function read(el) {
    var v = (el.value || '').replace(/[\s ]/g, '');
    if (v === '') return null;
    if (el.getAttribute('data-kind') === 'money') {
      var m = v.match(/^(.*?)[.,](\d{1,2})$/);
      v = m ? m[1].replace(/[.,]/g, '') + '.' + m[2] : v.replace(/[.,]/g, '');
    } else v = v.replace(',', '.');
    var x = parseFloat(v);
    return isFinite(x) && x >= 0 ? x : null;
  }
  function field(name) { return form.elements[name]; }
  function value(name) { return read(field(name)); }
  function choice(name) { var c = form.querySelector('input[name="' + name + '"]:checked'); return c ? c.value : null; }
  function setField(name, v, d) {
    var el = field(name);
    if (el && !el.hasAttribute('data-touched')) el.value = v == null ? '' : fmt(v, d || 0);
  }
  // the unit beside each number: read with the field, and a click on it puts the cursor in the field
  Array.prototype.forEach.call(form.querySelectorAll('.calc-num'), function (box) {
    var input = box.querySelector('input'), unit = box.querySelector('span');
    if (!input) return;
    if (unit) { unit.id = input.id + '-unit'; input.setAttribute('aria-describedby', unit.id); }
    box.addEventListener('mousedown', function (e) { if (e.target !== input) { e.preventDefault(); input.focus(); } });
  });
  Array.prototype.forEach.call(form.querySelectorAll('input[type="text"]'), function (el) {
    el.addEventListener('input', function () { el.setAttribute('data-touched', ''); });
  });
  form.addEventListener('submit', function (e) { e.preventDefault(); });

  // ?product=mobile|box, ?load=10…100 and ?fin=own|split|lease from the links on the product and Financing pages
  var params = new URLSearchParams(window.location.search);
  function pick(name, v) { var el = form.querySelector('input[name="' + name + '"][value="' + v + '"]'); if (el) el.checked = true; }
  if (params.get('product')) pick('product', params.get('product'));
  if (params.get('load')) pick('load', params.get('load'));
  if (params.get('fin')) pick('fin', params.get('fin'));

  // the region prices of the diesel (the product pages' averages)
  var presets = form.querySelectorAll('[data-diesel]');
  function markPreset() {
    var d = value('diesel');
    Array.prototype.forEach.call(presets, function (b) { b.setAttribute('aria-pressed', String(d != null && Math.abs(parseFloat(b.getAttribute('data-diesel')) - d) < 1e-9)); });
  }
  Array.prototype.forEach.call(presets, function (b) {
    b.addEventListener('click', function () {
      field('diesel').value = fmt(parseFloat(b.getAttribute('data-diesel')), 2);
      field('diesel').setAttribute('data-touched', '');
      update();
    });
  });

  function annuity(p, r, n) { return n > 0 ? (r > 0 ? p * r / (1 - Math.pow(1 + r, -n)) : p / n) : 0; }

  var out = {};
  Array.prototype.forEach.call(root.querySelectorAll('[data-out]'), function (el) { out[el.getAttribute('data-out')] = el; });
  function show(key, text) { if (out[key] && out[key].textContent !== text) out[key].textContent = text; }
  // a readout: the figure in the display face with its unit small beside it, or a short sentence
  function figure(key, num, unit) {
    var e = out[key];
    if (!e) return;
    e.classList.remove('is-text');
    var v = document.createElement('span'), u = document.createElement('span');
    v.className = 'v'; v.textContent = num; u.className = 'u'; u.textContent = unit;
    e.textContent = '';
    e.appendChild(v); e.appendChild(document.createTextNode(' ')); e.appendChild(u);
  }
  function words(key, text) { if (out[key]) { out[key].classList.add('is-text'); show(key, text); } }
  function when() {
    var product = choice('product'), mode = choice('mode'), fin = choice('fin');
    Array.prototype.forEach.call(root.querySelectorAll('[data-when]'), function (el) {
      var ok = el.getAttribute('data-when').split(' ').every(function (w) {
        return w === product || w === mode || w === fin || (w === 'financed' && fin !== 'own') ||
          (w === 'mobile-generator' && product === 'mobile' && mode === 'generator') ||
          (w === 'mobile-grid' && product === 'mobile' && mode === 'grid') ||
          (w === 'mobile-noprice' && product === 'mobile' && value('price') == null);
      });
      el.hidden = !ok;
    });
  }

  var lastProduct = null, lastMode = null, state = null, typed = {};
  function update() {
    var product = choice('product'), mode = choice('mode'), fin = choice('fin');
    if (product !== lastProduct) {
      // a price typed for one product stays with that product
      var pf = field('price');
      if (lastProduct && pf.hasAttribute('data-touched')) typed[lastProduct] = pf.value;
      if (typed[product] != null) { pf.value = typed[product]; pf.setAttribute('data-touched', ''); }
      else { pf.removeAttribute('data-touched'); setField('price', PRICE[product]); }
      lastProduct = product;
    }
    if (mode !== lastMode) { setField('sale', SALE[mode], 2); lastMode = mode; }
    var load = parseFloat(choice('load')) / 100;
    var diesel = value('diesel') || 0, use = value('use') || 0, grid = value('grid') || 0, sale = value('sale') || 0;
    var unitCost = mode === 'grid' ? grid : use * diesel;
    var kwhDay = KW * HOURS * load;
    var serviceDay = product === 'mobile' && mode === 'generator' ? (value('service') || 0) * load : 0;
    var grossDay = kwhDay * (sale - unitCost) + serviceDay;
    var grossMonth = grossDay * DAYS;
    var costs = value('costs') || 0;
    var op = grossMonth - costs;
    var price = value('price');
    var priced = price != null && price > 0;

    var outlay = 0, payment = 0, n = 0, terms = true;
    if (priced) {
      if (fin === 'own') outlay = price;
      else if (fin === 'split') {
        n = parseInt(choice('split'), 10);
        outlay = price / 2;
        payment = annuity(price / 2, (value('splitRate') || 0) / 1200, n);
      } else {
        var down = value('down'), rate = value('rate'), term = value('term');
        if (down == null || rate == null || !term) terms = false;
        else {
          n = Math.round(term);
          outlay = price * Math.min(down, 100) / 100;
          payment = annuity(price - outlay, rate / 1200, n);
        }
      }
    }
    // cumulative cash: the money put in at month 0, then each month's remainder (up to 10 years for the payback)
    var cum = [-outlay], payback = null;
    for (var m = 1; m <= 120; m++) {
      cum[m] = cum[m - 1] + op - (m <= n ? payment : 0);
      if (payback == null && cum[m] >= 0 && priced && terms) payback = cum[m - 1] >= 0 ? 0 : m - 1 + (-cum[m - 1]) / (cum[m] - cum[m - 1]);
    }
    var ready = priced && terms;
    var horizon = Math.min(60, Math.max(12, Math.ceil(((payback != null ? payback : 0) + 3) / 3) * 3, n ? n + 3 : 0));

    when();
    markPreset();
    var hours = HOURS * load;
    show('hours', T.hours(trim1(hours), fmt(kwhDay)));
    show('month', fmt(Math.round(grossMonth)));
    figure('day', fmt(Math.round(grossDay)), 'EUR');
    figure('year', fmt(Math.round(grossMonth * MONTHS)), 'EUR');
    figure('kwh', fmt(kwhDay * DAYS), 'kWh');
    if (!ready) words('payment', priced ? T.enterTerms : T.enterPrice);
    else if (payment) figure('payment', fmt(Math.round(payment)), 'EUR');
    else words('payment', T.none);
    figure('left', fmt(Math.round(op - payment)), 'EUR');
    if (!priced) words('payback', T.enterPrice);
    else if (!terms) words('payback', T.enterTerms);
    else if (payback == null) words('payback', T.never);
    else if (payback < 0.05) words('payback', T.firstMonth);
    else figure('payback', '≈ ' + trim1(payback), Math.abs(payback - 1) < 0.05 ? T.month1 : T.months);
    show('cover', ready && payment && op > 0 ? T.cover(fmt(op / payment, 1)) : '');
    if (out.cover && !(ready && payment && op > 0)) out.cover.hidden = true;
    show('protect', priced ? T.protect(fmt(Math.round(price / 2))) : '');
    if (out.protect) out.protect.hidden = !priced;

    // one month as a statement
    var kwhMonth = kwhDay * DAYS;
    // [label, what it is made of (small, beside it or under it on phones), amount, row class]
    var rows = [
      [T.kwhCharged, '', fmt(kwhMonth) + ' kWh', ''],
      [T.revenue, fmt(sale, 2) + ' EUR/kWh', eur(kwhMonth * sale), ''],
      mode === 'grid' ? [T.gridPower, fmt(grid, 2) + ' EUR/kWh', eur(-kwhMonth * unitCost), '']
        : [T.diesel, fmt(use, 2) + ' L/kWh × ' + fmt(diesel, 2) + ' EUR/L', eur(-kwhMonth * unitCost), '']
    ];
    if (product === 'mobile' && mode === 'generator') rows.push([T.service, T.forecast, eur(serviceDay * DAYS), '']);
    rows.push([T.gross, '', eur(grossMonth), 'is-sub']);
    if (costs) rows.push([T.costs, '', eur(-costs), '']);
    if (ready && payment) rows.push([T.payment, '', eur(-payment), '']);
    rows.push([T.left, '', eur(op - (ready ? payment : 0)), 'is-total']);
    if (out.ledger) {
      out.ledger.innerHTML = '';
      rows.forEach(function (r) {
        var tr = document.createElement('tr');
        if (r[3]) tr.className = r[3];
        var th = document.createElement('th'); th.scope = 'row'; th.textContent = r[0];
        if (r[1]) { var sm = document.createElement('small'); sm.textContent = r[1]; th.appendChild(document.createTextNode(' ')); th.appendChild(sm); }
        var td = document.createElement('td'); td.textContent = r[2];
        tr.appendChild(th); tr.appendChild(td);
        out.ledger.appendChild(tr);
      });
    }

    state = { cum: cum.slice(0, horizon + 1), payback: ready ? payback : null, horizon: horizon };
    draw();
    show('chartcap', T.chartFig(horizon));
    peek(grossMonth, ready ? payback : null);
    send({ product: product, mode: mode, load: load, diesel: diesel, use: use, grid: grid, sale: sale, costs: costs, price: price,
      fin: fin, n: n, grossMonth: grossMonth, payment: ready ? payment : null, left: op - (ready ? payment : 0), payback: out.payback ? out.payback.textContent : '' });
  }

  // the cumulative cash flow, drawn to the chart's real width
  var svgNS = 'http://www.w3.org/2000/svg';
  var holder = root.querySelector('.calc-chart-draw');
  function el(tag, attrs, parent) {
    var e = document.createElementNS(svgNS, tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  function nice(range) {
    var rough = range / 4, mag = Math.pow(10, Math.floor(Math.log10(rough || 1)));
    var steps = [1, 2, 2.5, 5, 10];
    for (var i = 0; i < steps.length; i++) if (steps[i] * mag >= rough) return steps[i] * mag;
    return 10 * mag;
  }
  function draw() {
    if (!holder || !state) return;
    var W = Math.max(260, Math.round(holder.clientWidth)), H = Math.round(Math.min(260, Math.max(200, W * 0.4)));
    var cum = state.cum, last = cum.length - 1;
    var lo = Math.min(0, Math.min.apply(null, cum)), hi = Math.max(0, Math.max.apply(null, cum));
    if (hi - lo < 1) hi = lo + 1000;
    var step = nice(hi - lo);
    var y0 = Math.floor(lo / step) * step, y1 = Math.ceil(hi / step) * step;
    var ticks = [];
    for (var v = y0; v <= y1 + step / 2; v += step) ticks.push(v);
    var labelW = Math.max.apply(null, ticks.map(function (t) { return fmt(t).length; })) * 8.6 + 10;
    var pad = { l: labelW, r: 14, t: 26, b: 30 };
    var pw = W - pad.l - pad.r, ph = H - pad.t - pad.b;
    function X(m) { return pad.l + (m / last) * pw; }
    function Y(v) { return pad.t + (1 - (v - y0) / (y1 - y0)) * ph; }
    var svg = el('svg', { width: W, height: H, viewBox: '0 0 ' + W + ' ' + H, role: 'img', 'aria-label': T.chartAria(out.payback ? T.paybackLine + ': ' + out.payback.textContent + '.' : '') });
    holder.innerHTML = '';
    holder.appendChild(svg);   // in the page first, so the payback label can be measured
    var defs = el('defs', {}, svg);
    var id = 'g' + Math.random().toString(36).slice(2, 8);
    var grad = el('linearGradient', { id: id + 'p', x1: 0, x2: 0, y1: 0, y2: 1 }, defs);
    el('stop', { offset: '0', 'stop-color': '#a6f4d2', 'stop-opacity': '.34' }, grad);
    el('stop', { offset: '1', 'stop-color': '#a6f4d2', 'stop-opacity': '.03' }, grad);
    var zy = Y(0);
    el('rect', { x: pad.l, y: pad.t - 4, width: pw, height: Math.max(0, zy - pad.t + 4) }, el('clipPath', { id: id + 'a' }, defs));
    el('rect', { x: pad.l, y: zy, width: pw, height: Math.max(0, pad.t + ph - zy + 4) }, el('clipPath', { id: id + 'b' }, defs));
    ticks.forEach(function (t) {
      el('line', { x1: pad.l, x2: pad.l + pw, y1: Y(t), y2: Y(t), stroke: t === 0 ? 'rgba(244,250,247,.5)' : 'rgba(166,244,210,.12)', 'stroke-width': 1, 'stroke-dasharray': t === 0 ? '5 5' : '' }, svg);
      var tx = el('text', { x: pad.l - 10, y: Y(t) + 5, 'text-anchor': 'end', fill: '#c3dad1', 'font-size': 14 }, svg);
      tx.textContent = fmt(t);
    });
    var perMonth = pw / last, every = [1, 2, 3, 6, 12].filter(function (s) { return s * perMonth >= 30; })[0] || 12;
    var unitX = el('text', { x: pad.l + pw, y: pad.t + ph + 22, 'text-anchor': 'end', fill: '#c3dad1', 'font-size': 14 }, svg);
    unitX.textContent = T.mo;
    for (var mm = 0; mm <= last; mm += every) {
      if (X(mm) > pad.l + pw - 44) continue;   // the month unit stands at the right end
      var lx = el('text', { x: X(mm), y: pad.t + ph + 22, 'text-anchor': 'middle', fill: '#c3dad1', 'font-size': 14 }, svg);
      lx.textContent = mm;
    }
    var unitY = el('text', { x: pad.l - 10, y: pad.t - 10, 'text-anchor': 'end', fill: '#c3dad1', 'font-size': 14 }, svg);
    unitY.textContent = 'EUR';
    var pts = cum.map(function (v, i) { return X(i).toFixed(1) + ',' + Y(v).toFixed(1); });
    var area = 'M' + X(0) + ',' + zy + ' L' + pts.join(' L') + ' L' + X(last) + ',' + zy + ' Z';
    el('path', { d: area, fill: 'url(#' + id + 'p)', 'clip-path': 'url(#' + id + 'a)' }, svg);
    el('path', { d: area, fill: 'rgba(255,196,170,.16)', 'clip-path': 'url(#' + id + 'b)' }, svg);
    el('polyline', { points: pts.join(' '), fill: 'none', stroke: '#a6f4d2', 'stroke-width': 2.5, 'stroke-linejoin': 'round', 'stroke-linecap': 'round' }, svg);
    if (state.payback != null && state.payback > 0.05 && state.payback <= last) {
      var px = X(state.payback);
      el('circle', { cx: px, cy: zy, r: 6, fill: '#a6f4d2', stroke: '#062925', 'stroke-width': 3 }, svg);
      // above the zero line left of the point (the line is still below zero there) or below it to the right
      // (the line is above zero there); the short form where the long one has no room
      var lab = el('text', { fill: '#f4faf7', 'font-size': 14, 'font-weight': 600 }, svg);
      var roomL = px - pad.l - 12, roomR = pad.l + pw - px - 12;
      var texts = [T.paid + trim1(state.payback) + ' ' + T.mo, '≈ ' + trim1(state.payback) + ' ' + T.mo], left = true;
      for (var ti = 0; ti < texts.length; ti++) {
        lab.textContent = texts[ti];
        var tw = lab.getComputedTextLength();
        if (tw <= roomL) { left = true; break; }
        if (tw <= roomR) { left = false; break; }
        left = roomL >= roomR;
      }
      lab.setAttribute('x', left ? px - 12 : px + 12);
      lab.setAttribute('y', left ? zy - 12 : zy + 22);
      lab.setAttribute('text-anchor', left ? 'end' : 'start');
    }
  }
  if ('ResizeObserver' in window && holder) new ResizeObserver(function () { draw(); }).observe(holder);

  // the scenario to the contact form
  var sendLink = root.querySelector('[data-send]');
  function send(s) {
    if (!sendLink) return;
    var lines = [T.summaryHead,
      T.product + ': ECOES MultiCharger ' + (s.product === 'box' ? 'Box' : 'Mobile'),
      T.mode + ': ' + (s.mode === 'grid' ? T.modeGrid : T.modeGen),
      T.load + ': ' + Math.round(s.load * 100) + '%',
      T.energy + ': ' + (s.mode === 'grid' ? T.energyGrid + fmt(s.grid, 2) + ' EUR/kWh' : T.energyDiesel + fmt(s.diesel, 2) + ' EUR/L × ' + fmt(s.use, 2) + ' L/kWh'),
      T.saleLine + ': ' + fmt(s.sale, 2) + ' EUR/kWh'];
    if (s.product === 'mobile' && s.mode === 'generator') lines.push(T.serviceLine(fmt(value('service') || 0)));
    lines.push(T.costs + ': ' + eur(s.costs) + T.perMonth,
      T.stationPrice + ': ' + (s.price ? eur(s.price) : T.byOffer),
      T.financing + ': ' + (s.fin === 'own' ? T.own : s.fin === 'split' ? T.split(s.n, value('splitRate') ? fmt(value('splitRate'), 1) : '') :
        T.lease(value('down') != null ? fmt(value('down'), 0) : '–', value('rate') != null ? fmt(value('rate'), 1) : '–', value('term') || '–')),
      T.grossLine + ': ' + eur(s.grossMonth) + T.perMonth);
    if (s.payment) lines.push(T.paymentLine + ': ' + eur(s.payment));
    lines.push(T.leftLine + ': ' + eur(s.left), T.paybackLine + ': ' + s.payback, '', T.ask, T.where);
    sendLink.href = sendLink.getAttribute('data-base') + '?topic=finance&calc=' + encodeURIComponent(lines.join('\n')) + '#contact-form';
  }

  // on phones: the result in a bar at the bottom while the figures are out of sight
  var peekBar = root.querySelector('.calc-peek');
  var screen = root.querySelector('.calc-screen');
  function peek(gross, pb) {
    if (!peekBar) return;
    peekBar.querySelector('[data-peek="month"]').textContent = eur(gross);
    peekBar.querySelector('[data-peek="sub"]').textContent = T.perMonthPeek + (pb != null && pb > 0.05 ? ', ' + T.paybackPeek + '≈ ' + trim1(pb) + ' ' + T.mo : '');
  }
  if (peekBar && screen && 'IntersectionObserver' in window) {
    var inputsSeen = false, screenSeen = false;
    var inputs = root.querySelector('.calc-inputs');
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.target === screen) screenSeen = e.isIntersecting; else inputsSeen = e.isIntersecting; });
      peekBar.classList.toggle('is-on', inputsSeen && !screenSeen);
    }, { threshold: 0 });
    io.observe(screen); io.observe(inputs);
  }

  form.addEventListener('input', update);
  form.addEventListener('change', update);
  update();
  root.classList.add('is-ready');
})();
