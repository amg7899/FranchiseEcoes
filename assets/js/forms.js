// Forms (pre-order, dealer application, offer request on Contact us). Required fields are checked next to
// them; the form is sent by e-mail through FormSubmit (to sales@ecoes.eu, copy to
// ecoes@ecoes.eu, client 2026-11-09). Without JavaScript the form still posts to FormSubmit, which then returns
// here with ?sent=1. If sending fails, the message says why (e.g. the form still waits for
// FormSubmit's one-time activation) and links to sales@ecoes.eu with everything the visitor
// typed already filled in. Texts follow data-lang on the form ("en" or "bg").
(function () {
  var TO = 'sales@ecoes.eu';
  var TEXT = {
    en: {
      sent: 'Thank you! Your form has been sent. We will contact you soon.',
      sending: 'Sending…',
      notActive: 'The form was not sent because it has not been activated yet. Please send it by e-mail to ',
      failed: 'The form could not be sent. Please try again later, or send it by e-mail to ',
      filledIn: ' (the link opens your e-mail program with your entries filled in).',
      detail: 'Details: '
    },
    bg: {
      sent: 'Благодарим ви! Формулярът е изпратен. Ще се свържем с вас скоро.',
      sending: 'Изпращане…',
      notActive: 'Формулярът не беше изпратен, защото все още не е активиран. Моля, изпратете го по имейл до ',
      failed: 'Формулярът не можа да бъде изпратен. Моля, опитайте отново по-късно или го изпратете по имейл до ',
      filledIn: ' (връзката отваря вашата имейл програма с попълнените данни).',
      detail: 'Подробности: '
    }
  };
  var params = new URLSearchParams(window.location.search);

  // Visitor statistics (Plausible: no cookies, no personal data, so no consent banner): a form that was really
  // sent counts as a goal of its kind. The goals carry these names in Plausible (Site settings → Goals → custom
  // events). Without the statistics script on the page this does nothing.
  function goal(form) {
    var name = form.classList.contains('preorder-form') ? 'Pre-order'
      : form.classList.contains('dealer-form') ? 'Dealer application' : 'Contact form';
    if (typeof window.plausible === 'function') window.plausible(name);
  }

  Array.prototype.forEach.call(document.querySelectorAll('.js-form'), function (form) {
    var T = TEXT[form.getAttribute('data-lang')] || TEXT.en;
    var status = form.querySelector('.form-status');
    var button = form.querySelector('button[type="submit"]');
    var buttonLabel = button.querySelector('.btn-label');
    var sendLabel = buttonLabel.textContent;
    var subject = form.querySelector('input[name="_subject"]');
    var topic = form.querySelector('select[data-topics]');

    // the subject of the contact form follows ?topic= (franchise, multicharger, multicharger-box, other)
    var wanted = params.get('topic');
    if (topic && wanted) {
      for (var i = 0; i < topic.options.length; i++) {
        if (topic.options[i].getAttribute('data-topic') === wanted) topic.selectedIndex = i;
      }
    }

    var next = document.createElement('input');
    next.type = 'hidden';
    next.name = '_next';
    next.value = window.location.origin + window.location.pathname + '?sent=1#' + (form.closest('[id]') || form).id;
    form.appendChild(next);
    if (params.get('sent') === '1' && window.location.hash === '#' + (form.closest('[id]') || form).id) show(T.sent, false);

    // required text, e-mail and checkbox fields, each with its error next to it
    var checks = [];
    Array.prototype.forEach.call(form.querySelectorAll('input[required]:not([type="radio"]), textarea[required], select[required]'), function (el) {
      checks.push({
        el: el,
        marks: [el],
        error: document.getElementById((el.getAttribute('aria-describedby') || '').split(' ')[0]),
        ok: function () {
          if (el.type === 'checkbox') return el.checked;
          if (el.type === 'email') return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(el.value.trim());
          return el.value.trim() !== '';
        }
      });
    });
    // required radio groups: the fieldset carries the error
    Array.prototype.forEach.call(form.querySelectorAll('fieldset.choice'), function (set) {
      var radios = set.querySelectorAll('input[type="radio"]');
      if (!radios.length || !radios[0].required) return;
      checks.push({
        el: radios[0],
        marks: [set],
        error: document.getElementById((set.getAttribute('aria-describedby') || '').split(' ')[0]),
        ok: function () { return Array.prototype.some.call(radios, function (r) { return r.checked; }); }
      });
    });

    function check(c) {
      var valid = c.ok();
      c.marks.forEach(function (m) { m.setAttribute('aria-invalid', String(!valid)); });
      if (c.error) c.error.hidden = valid;
      return valid;
    }
    // once a field has been flagged, re-check it as the visitor fixes it
    checks.forEach(function (c) {
      var target = c.marks[0].tagName === 'FIELDSET' ? c.marks[0] : c.el;
      target.addEventListener(c.el.type === 'checkbox' || c.el.type === 'radio' ? 'change' : 'input', function () {
        if (c.marks[0].hasAttribute('aria-invalid')) check(c);
      });
    });

    // the message under the button, kept on screen with a little room (the button may sit at the bottom edge,
    // and the fixed header covers the top)
    var calm = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    function reveal() {
      var r = status.getBoundingClientRect(), room = 24;
      var header = document.querySelector('.site-header');
      var top = (header ? header.offsetHeight : 0) + room;
      var dy = r.bottom > window.innerHeight - room ? Math.min(r.bottom - window.innerHeight + room, r.top - top)
        : (r.top < top ? r.top - top : 0);
      if (dy) window.scrollBy({ top: dy, behavior: calm ? 'auto' : 'smooth' });
    }
    function show(text, isError, busy) {
      status.textContent = text;
      status.classList.toggle('is-error', !!isError);
      status.classList.toggle('is-busy', !!busy);
      status.hidden = false;
      reveal();
    }

    // a mailto link to sales@ecoes.eu (copy to ecoes@ecoes.eu) with the visitor's entries
    function mailto() {
      var lines = [];
      Array.prototype.forEach.call(form.querySelectorAll('input, select, textarea'), function (el) {
        if (!el.name || el.name.charAt(0) === '_' || el.type === 'hidden' || el.name === 'consent') return;
        if ((el.type === 'radio' || el.type === 'checkbox') && !el.checked) return;
        var value = el.value.trim();
        if (!value) return;
        var label = el.type === 'radio' ? el.closest('fieldset').querySelector('legend') : form.querySelector('label[for="' + el.id + '"]');
        var name = label ? label.textContent.replace(/\*/g, '').replace(/^\s*\d+\s*/, '').trim() : el.name;
        lines.push(name + ': ' + value);
      });
      var cc = form.querySelector('input[name="_cc"]');
      return 'mailto:' + TO +
        '?cc=' + encodeURIComponent(cc ? cc.value : '') +
        '&subject=' + encodeURIComponent(subject.value) +
        '&body=' + encodeURIComponent(lines.join('\r\n'));
    }

    function showError(reason) {
      var notActive = /activat/i.test(reason);
      show(notActive ? T.notActive : T.failed, true);
      var link = document.createElement('a');
      link.href = mailto();
      link.textContent = TO;
      link.setAttribute('translate', 'no');
      status.appendChild(link);
      status.appendChild(document.createTextNode(T.filledIn));
      if (!notActive && reason) {
        var detail = document.createElement('small');
        detail.className = 'form-detail';
        detail.textContent = T.detail + reason;
        status.appendChild(detail);
      }
      reveal();   // again: the link and the details made it taller
    }

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var firstInvalid = null;
      checks.forEach(function (c) { if (!check(c) && !firstInvalid) firstInvalid = c.el; });
      if (firstInvalid) { firstInvalid.focus(); return; }
      var honey = form.querySelector('input[name="_honey"]');
      if (honey && honey.value) return;   // filled in by a bot

      subject.value = form.getAttribute('data-subject') + (topic ? ': ' + topic.value : '');
      button.disabled = true;
      buttonLabel.textContent = T.sending;
      // "Sending…" at once under the button too: when FormSubmit is slow, the visitor saw nothing but the
      // button's label change and thought nothing happened (client, 2026-11-09)
      show(T.sending, false, true);

      var data = {};
      new FormData(form).forEach(function (value, key) { data[key] = value; });

      var controller = window.AbortController ? new AbortController() : null;
      var timer = controller && setTimeout(function () { controller.abort(); }, 25000);

      fetch(form.action.replace('formsubmit.co/', 'formsubmit.co/ajax/'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(data),
        signal: controller ? controller.signal : undefined
      })
        .then(function (response) {
          return response.json().catch(function () { return { success: false, message: 'HTTP ' + response.status }; });
        })
        .then(function (result) {
          // FormSubmit answers {success: "true"} or {success: "false", message: "..."}
          if (String(result.success) !== 'true') throw new Error(result.message || 'not sent');
          form.reset();
          checks.forEach(function (c) { c.marks.forEach(function (m) { m.removeAttribute('aria-invalid'); }); });
          show(T.sent, false);
          goal(form);
        })
        .catch(function (err) {
          if (window.console) console.warn('Form:', err);
          showError(err && err.name === 'AbortError' ? 'timeout' : String(err && err.message || err));
        })
        .then(function () {
          if (timer) clearTimeout(timer);
          button.disabled = false;
          buttonLabel.textContent = sendLabel;
        });
    });
  });
})();
