// The Defense area (/defense/, /bg/defense/): the content is encrypted in the page (tools/defense.py) and opens
// only with the access code: PBKDF2-SHA256 derives the AES-GCM key from the code, Web Crypto decrypts it here.
// A right code is kept for this tab only (sessionStorage), so both languages open without typing it again;
// "Lock" forgets it. Texts come from data-* on the form, so EN and BG differ only in the markup.
(function () {
  var block = document.getElementById('vault');
  var form = document.getElementById('vault-form');
  if (!block || !form) return;
  var input = document.getElementById('vault-code');
  var msg = document.getElementById('vault-msg');
  var gate = document.getElementById('vault-gate');
  var target = document.getElementById('vault-content');
  var button = form.querySelector('button[type="submit"]');
  var KEY = 'ecoes-defense-code';

  function say(text) { msg.textContent = text; msg.hidden = !text; }
  function norm(code) { return String(code || '').replace(/[^0-9A-Za-z]/g, '').toUpperCase(); }
  function bytes(b64) {
    var bin = atob(b64), out = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
    return out;
  }

  var data;
  try { data = JSON.parse(block.textContent); } catch (e) { data = null; }
  if (!data || !data.ct || !window.crypto || !crypto.subtle || !window.TextEncoder) {
    say(form.getAttribute('data-nocrypto'));
    button.disabled = true;
    return;
  }

  function unlock(code) {
    return crypto.subtle.importKey('raw', new TextEncoder().encode(norm(code)), 'PBKDF2', false, ['deriveKey'])
      .then(function (base) {
        return crypto.subtle.deriveKey({ name: 'PBKDF2', salt: bytes(data.salt), iterations: data.iter, hash: 'SHA-256' },
          base, { name: 'AES-GCM', length: 256 }, false, ['decrypt']);
      })
      .then(function (key) { return crypto.subtle.decrypt({ name: 'AES-GCM', iv: bytes(data.iv) }, key, bytes(data.ct)); })
      .then(function (buf) { return new TextDecoder().decode(buf); });
  }

  function open(html, focus) {
    target.innerHTML = html;
    target.hidden = false;
    gate.hidden = true;
    document.documentElement.classList.add('vault-open');
    if (focus) { window.scrollTo(0, 0); target.focus({ preventScroll: true }); }
  }

  var saved = null;
  try { saved = sessionStorage.getItem(KEY); } catch (e) {}
  if (saved) {
    unlock(saved).then(function (html) { open(html, false); }, function () {
      try { sessionStorage.removeItem(KEY); } catch (e) {}
    });
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var code = norm(input.value);
    if (!code) { say(form.getAttribute('data-empty')); input.focus(); return; }
    button.disabled = true;
    say(form.getAttribute('data-busy'));
    unlock(code).then(function (html) {
      try { sessionStorage.setItem(KEY, code); } catch (err) {}
      say('');
      open(html, true);
    }, function () {
      say(form.getAttribute('data-wrong'));
      input.select();
    }).then(function () { button.disabled = false; });
  });

  document.addEventListener('click', function (e) {
    var lock = e.target.closest && e.target.closest('[data-vault-lock]');
    if (!lock) return;
    try { sessionStorage.removeItem(KEY); } catch (err) {}
    window.location.reload();
  });
})();
