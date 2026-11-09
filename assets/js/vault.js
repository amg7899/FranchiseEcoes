// The Defense area (/defense/, /bg/defense/): the content is encrypted in the page (tools/defense.py) and opens
// only with the access code: PBKDF2-SHA256 derives the AES-GCM key from the code, Web Crypto decrypts it here.
// Its photos are encrypted files beside the page (vault-1.bin, ...: IV + ciphertext, the file name as associated
// data), fetched and decrypted with the same key once the content is open, so the gate page stays small.
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
      .then(function (key) {
        return crypto.subtle.decrypt({ name: 'AES-GCM', iv: bytes(data.iv) }, key, bytes(data.ct))
          .then(function (buf) { return { key: key, html: new TextDecoder().decode(buf) }; });
      });
  }

  function photos(key) {
    Array.prototype.forEach.call(target.querySelectorAll('img[data-vault-src]'), function (img) {
      var name = img.getAttribute('data-vault-src');
      fetch(name)
        .then(function (r) { if (!r.ok) throw new Error(r.status); return r.arrayBuffer(); })
        .then(function (buf) {
          return crypto.subtle.decrypt({ name: 'AES-GCM', iv: new Uint8Array(buf, 0, 12), additionalData: new TextEncoder().encode(name) },
            key, new Uint8Array(buf, 12));
        })
        .then(function (plain) {
          img.src = URL.createObjectURL(new Blob([plain], { type: img.getAttribute('data-vault-type') || 'image/webp' }));
          img.removeAttribute('data-vault-src');
        })
        .catch(function () {});
    });
  }

  function open(opened, focus) {
    target.innerHTML = opened.html;
    target.hidden = false;
    gate.hidden = true;
    document.documentElement.classList.add('vault-open');
    photos(opened.key);
    if (focus) { window.scrollTo(0, 0); target.focus({ preventScroll: true }); }
  }

  var saved = null;
  try { saved = sessionStorage.getItem(KEY); } catch (e) {}
  if (saved) {
    unlock(saved).then(function (opened) { open(opened, false); }, function () {
      try { sessionStorage.removeItem(KEY); } catch (e) {}
    });
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var code = norm(input.value);
    if (!code) { say(form.getAttribute('data-empty')); input.focus(); return; }
    button.disabled = true;
    say(form.getAttribute('data-busy'));
    unlock(code).then(function (opened) {
      try { sessionStorage.setItem(KEY, code); } catch (err) {}
      say('');
      open(opened, true);
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
