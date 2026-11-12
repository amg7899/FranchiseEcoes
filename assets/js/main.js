// ECOES Franchise – header, menu, language and the profit meter on Home.
(function () {
  var root = document.documentElement;
  root.classList.add('js');

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

  // ---- the Products dropdown in the row of links: hover opens it (CSS); its button opens it for touch and keyboard;
  //      Escape, a click elsewhere or focus leaving closes it ----
  Array.prototype.forEach.call(document.querySelectorAll('.main-nav .has-sub'), function (item) {
    var toggle = item.querySelector('.sub-toggle');
    if (!toggle) return;
    function set(open) {
      toggle.setAttribute('aria-expanded', String(open));
      item.classList.toggle('is-open', open);
      if (open) item.classList.remove('is-dismissed');
    }
    toggle.addEventListener('click', function () { set(toggle.getAttribute('aria-expanded') !== 'true'); });
    document.addEventListener('click', function (e) { if (!item.contains(e.target)) set(false); });
    item.addEventListener('focusout', function (e) { if (!e.relatedTarget || !item.contains(e.relatedTarget)) set(false); });
    item.addEventListener('mouseleave', function () { item.classList.remove('is-dismissed'); });
    document.addEventListener('keydown', function (e) {
      if (e.key !== 'Escape') return;
      if (item.classList.contains('is-open')) { set(false); toggle.focus(); }
      if (item.matches(':hover')) item.classList.add('is-dismissed');
    });
  });

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

// Language. The EN/BG switch links each page to the same page in the other language.
// On the first arrival from outside the site (a link, a search, an address typed in), a visitor whose
// browser asks for a language the site has gets that version, everybody else the English one (client,
// 2026-11-04: foreigners should get English automatically); the browser itself then offers to translate
// it into their own language. A language picked with the switch is remembered in this browser and always
// wins; its pages are marked translate="no", so the browser does not translate them again. When the
// browser translates a page into a language the site has (it sets <html lang>, e.g. Chrome translating
// English into Bulgarian), the visitor is taken to our own version of that page. Search engines and
// other robots are never redirected, so both languages stay findable.
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
    try { return window.localStorage.getItem(KEY) || window.sessionStorage.getItem(KEY); } catch (e) { return null; }
  }
  function remember(lang) {
    try { window.localStorage.setItem(KEY, lang); } catch (e) {
      try { window.sessionStorage.setItem(KEY, lang); } catch (err) { /* storage blocked */ }
    }
  }
  // switching keeps the query and the anchor (e.g. contact-us/?topic=multicharger#contact-form)
  function target(a) { return a.href.split(/[?#]/)[0] + window.location.search + window.location.hash; }
  box.addEventListener('click', function (e) {
    var a = e.target.closest('a[hreflang]');
    if (!a || a === current) return;
    remember(a.getAttribute('hreflang'));
    a.href = target(a);
  });
  if (chosen() === pageLang) root.setAttribute('translate', 'no');

  // the first arrival: the visitor's language if the site has it, otherwise English
  function fromOutside() {
    if (!document.referrer) return true;
    try { return new URL(document.referrer).host !== window.location.host; } catch (e) { return true; }
  }
  function wanted() {
    var list = (navigator.languages && navigator.languages.length) ? navigator.languages : [navigator.language || ''];
    for (var i = 0; i < list.length; i++) {
      var l = String(list[i]).toLowerCase().split('-')[0];
      if (versions[l]) return l;
    }
    return 'en';
  }
  var robot = /bot|crawl|spider|slurp|preview|lighthouse|headless/i.test(navigator.userAgent || '');
  if (!chosen() && !robot && fromOutside()) {
    var want = wanted();
    if (want !== pageLang && versions[want]) { window.location.replace(target(versions[want])); return; }
  }

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
  var dec = plate.getAttribute('data-decimal') || '.';
  // whole numbers as 24,600; values with cents (the Box: 86.40 a day) with two decimals
  function fmt(n) {
    var cents = Math.round(n * 100);
    var whole = String(Math.floor(cents / 100)).replace(/\B(?=(\d{3})+(?!\d))/g, sep);
    var rest = cents % 100;
    return rest ? whole + dec + (rest < 10 ? '0' : '') + rest : whole;
  }
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

// Line drawings (the globe, the MultiCharger hologram) draw themselves once when they load, so they
// are loaded only when they come into view: the visitor sees them being drawn. Without JavaScript a
// <noscript> copy shows them finished.
(function () {
  var imgs = Array.prototype.slice.call(document.querySelectorAll('img.js-draw[data-src]'));
  if (!imgs.length) return;
  function load(img) { img.src = img.getAttribute('data-src'); img.removeAttribute('data-src'); }
  if (!('IntersectionObserver' in window)) { imgs.forEach(load); return; }
  var seen = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { load(e.target); seen.unobserve(e.target); }
    });
  }, { threshold: 0.3 });
  imgs.forEach(function (img) { seen.observe(img); });
  // Once the page has loaded, fetch the drawings and their glow (style.css) ahead into the browser's cache,
  // not as images, so each still starts drawing only when it is seen, but at once: on a slow connection the
  // lens stood empty for a moment before.
  window.addEventListener('load', function () {
    if (!window.fetch) return;
    (window.requestIdleCallback || function (f) { setTimeout(f, 300); })(function () {
      imgs.forEach(function (img) {
        var src = img.getAttribute('data-src');
        if (!src) return;
        [src, src.replace(/\.svg$/, '-glow.webp')].forEach(function (u) {
          try { fetch(u, { priority: 'low' }).catch(function () {}); } catch (e) {}
        });
      });
    });
  });
})();
