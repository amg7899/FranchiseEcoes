// Documents and awards on About us (HISTORY): a thumbnail opens the document full size in a
// dialog, with its caption, previous / next through all of them (also the arrow keys) and a close
// button (also Escape or a click beside the document). Without JavaScript, or without <dialog>,
// the link opens the image itself.
(function () {
  var list = document.querySelector('.docs');   // carries the button labels in the page's language
  var links = Array.prototype.slice.call(document.querySelectorAll('.history .doc-link'));
  if (!list || !links.length || typeof HTMLDialogElement !== 'function') return;
  var root = document.documentElement;
  var icon = function (d) {
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="square" aria-hidden="true" focusable="false"><path d="' + d + '"/></svg>';
  };

  var dialog = document.createElement('dialog');
  dialog.className = 'lightbox';
  dialog.setAttribute('aria-labelledby', 'lightbox-title');
  dialog.innerHTML =
    '<div class="lightbox-top">' +
      '<p class="lightbox-count"></p>' +
      '<button type="button" class="lightbox-btn lightbox-close">' + icon('M6 6l12 12M18 6L6 18') + '</button>' +
    '</div>' +
    '<div class="lightbox-stage"><picture><source type="image/webp"><img class="lightbox-img" alt=""></picture></div>' +
    '<div class="lightbox-bottom">' +
      '<button type="button" class="lightbox-btn lightbox-prev">' + icon('M20 12H5M11 6l-6 6 6 6') + '</button>' +
      '<p class="lightbox-caption" id="lightbox-title"></p>' +
      '<button type="button" class="lightbox-btn lightbox-next">' + icon('M4 12h15M13 6l6 6-6 6') + '</button>' +
    '</div>';
  document.body.appendChild(dialog);

  var closeBtn = dialog.querySelector('.lightbox-close');
  var prevBtn = dialog.querySelector('.lightbox-prev');
  var nextBtn = dialog.querySelector('.lightbox-next');
  var source = dialog.querySelector('source');
  var img = dialog.querySelector('.lightbox-img');
  var caption = dialog.querySelector('.lightbox-caption');
  var count = dialog.querySelector('.lightbox-count');
  closeBtn.setAttribute('aria-label', list.getAttribute('data-close') || 'Close');
  prevBtn.setAttribute('aria-label', list.getAttribute('data-prev') || 'Previous');
  nextBtn.setAttribute('aria-label', list.getAttribute('data-next') || 'Next');
  if (links.length < 2) { prevBtn.hidden = true; nextBtn.hidden = true; }

  var current = 0;
  var opener = null;

  function show(i) {
    current = (i + links.length) % links.length;
    var link = links[current];
    var thumb = link.querySelector('img');
    var title = link.parentNode.querySelector('.doc-title');
    source.srcset = link.getAttribute('data-webp') || '';
    img.src = link.href;
    img.alt = thumb ? thumb.alt : '';
    caption.innerHTML = title ? title.innerHTML : '';
    count.textContent = (current + 1) + ' / ' + links.length;
  }

  links.forEach(function (link, i) {
    link.addEventListener('click', function (e) {
      if (e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;   // new tab etc.
      e.preventDefault();
      opener = link;
      show(i);
      root.classList.add('lightbox-open');
      dialog.showModal();
      closeBtn.focus();
    });
  });

  closeBtn.addEventListener('click', function () { dialog.close(); });
  prevBtn.addEventListener('click', function () { show(current - 1); });
  nextBtn.addEventListener('click', function () { show(current + 1); });
  dialog.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowLeft') { e.preventDefault(); show(current - 1); }
    else if (e.key === 'ArrowRight') { e.preventDefault(); show(current + 1); }
  });
  // a click on the dark ground beside the document closes it
  dialog.addEventListener('click', function (e) {
    if (e.target === dialog || e.target.classList.contains('lightbox-stage')) dialog.close();
  });
  dialog.addEventListener('close', function () {
    root.classList.remove('lightbox-open');
    if (opener) opener.focus();
  });
})();
