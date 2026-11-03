// ECOES Franchise – header, menu, language and the profit meter on Home.
(function () {
  var root = document.documentElement;

  // ---- header shadow once the page scrolls under it ----
  function scrolled() { root.classList.toggle('is-scrolled', window.scrollY > 4); }
  scrolled();
  window.addEventListener('scroll', scrolled, { passive: true });

  // ---- menu (below 1200px, or when the row of links does not fit) ----
  var button = document.querySelector('.menu-button');
  var panel = document.getElementById('menu-panel');
  function setMenu(open) {
    if (!button || !panel) return;
    button.setAttribute('aria-expanded', String(open));
    panel.hidden = !open;
    root.classList.toggle('menu-open', open);
    var label = button.querySelector('.menu-label');
    if (label) label.textContent = open ? (button.getAttribute('data-close') || 'Close') : (button.getAttribute('data-open') || 'Menu');
    if (open) { var first = panel.querySelector('a'); if (first) first.focus(); }
  }
  if (button && panel) {
    button.setAttribute('data-open', button.querySelector('.menu-label').textContent);
    button.addEventListener('click', function () { setMenu(button.getAttribute('aria-expanded') !== 'true'); });
    panel.addEventListener('click', function (e) { if (e.target.closest('a')) setMenu(false); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && button.getAttribute('aria-expanded') === 'true') { setMenu(false); button.focus(); }
    });
    window.addEventListener('resize', function () {
      if (window.getComputedStyle(button).display === 'none') setMenu(false);
    });
  }

  // ---- the row of links stays on one line: if it does not fit (e.g. a long translation),
  //      only the menu button remains ----
  var nav = document.querySelector('.main-nav');
  var wide = window.matchMedia('(min-width: 1200px)');
  function fit() {
    if (!nav) return;
    root.classList.remove('nav-collapsed');
    if (!wide.matches) return;
    var list = nav.querySelector('ul');
    if (list.scrollWidth > nav.clientWidth + 1) root.classList.add('nav-collapsed');
  }
  fit();
  window.addEventListener('resize', fit);
  if (document.fonts) {
    if (document.fonts.ready) document.fonts.ready.then(fit);
    if (document.fonts.addEventListener) document.fonts.addEventListener('loadingdone', fit);
  }
  if (nav) new MutationObserver(fit).observe(nav, { subtree: true, childList: true, characterData: true });
  new MutationObserver(fit).observe(root, { attributes: true, attributeFilter: ['lang'] });
})();

// Language. The EN/BG switch links each page to the same page in the other language. When the
// browser translates a page into a language the site has itself (it sets <html lang>, e.g. Chrome
// translating English into Bulgarian), the visitor is taken to our own version of that page. A
// language picked with the switch is kept for the session; its pages are then marked
// translate="no", so the browser does not translate them again.
(function () {
  var root = document.documentElement;
  var box = document.querySelector('.lang-switch');
  var current = box && box.querySelector('[aria-current]');
  if (!current) return;
  var KEY = 'ecoes-franchise-lang';
  var pageLang = current.getAttribute('hreflang');
  var versions = {};
  Array.prototype.forEach.call(box.querySelectorAll('a[hreflang]'), function (a) {
    versions[a.getAttribute('hreflang')] = a;
  });
  function chosen() {
    try { return window.sessionStorage.getItem(KEY); } catch (e) { return null; }
  }
  // switching keeps the query and the anchor (e.g. contact-us/?topic=multicharger#contact-form)
  function target(a) { return a.href.split(/[?#]/)[0] + window.location.search + window.location.hash; }
  box.addEventListener('click', function (e) {
    var a = e.target.closest('a[hreflang]');
    if (!a || a === current) return;
    try { window.sessionStorage.setItem(KEY, a.getAttribute('hreflang')); } catch (err) { /* storage blocked */ }
    a.href = target(a);
  });
  if (chosen() === pageLang) root.setAttribute('translate', 'no');
  function follow() {
    var to = (root.getAttribute('lang') || '').toLowerCase().split('-')[0];
    if (to === pageLang || !versions[to] || chosen() === pageLang) return;
    window.location.replace(target(versions[to]));
  }
  follow();
  new MutationObserver(follow).observe(root, { attributes: true, attributeFilter: ['lang'] });
})();

// Profit meter (Home): choose a load and read the gross profit per day, month and year.
// The figures come from the table beside it (the client's table); without JavaScript the
// table alone is shown.
(function () {
  var plate = document.querySelector('[data-meter]');
  if (!plate) return;
  var meter = plate.querySelector('.meter');
  var readout = plate.querySelector('.meter-readout');
  var bar = plate.querySelector('.meter-bar span');
  var rows = {};
  Array.prototype.forEach.call(plate.querySelectorAll('tbody tr[data-load]'), function (tr) {
    rows[tr.getAttribute('data-load')] = tr;
  });
  var sep = plate.getAttribute('data-thousands') || ',';
  function fmt(n) { return String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, sep); }
  function out(key, value) {
    var el = readout.querySelector('[data-out="' + key + '"]');
    if (el) el.textContent = fmt(value);
  }
  function show(load) {
    var tr = rows[load];
    if (!tr) return;
    var dc = +tr.getAttribute('data-dc');
    var service = +tr.getAttribute('data-service');
    var day = dc + service;
    out('day', day); out('month', day * 30); out('year', day * 30 * 12); out('dc', dc); out('service', service);
    bar.style.setProperty('--load', load + '%');
    bar.style.setProperty('--load-n', load);
    Object.keys(rows).forEach(function (k) { rows[k].classList.toggle('is-on', k === String(load)); });
  }
  meter.hidden = false;
  readout.hidden = false;
  meter.addEventListener('change', function (e) { if (e.target.name === 'load') show(e.target.value); });
  var checked = meter.querySelector('input:checked');
  show(checked ? checked.value : '50');
})();
